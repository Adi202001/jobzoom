"""Matcher Agent - Scores job-user fit"""

import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput, JobStatus


@AgentRegistry.register
class MatcherAgent(BaseAgent):
    """Agent responsible for matching users to jobs and scoring fit"""

    @property
    def name(self) -> str:
        return "MATCHER_AGENT"

    @property
    def description(self) -> str:
        return "Scores job-user fit and ranks opportunities"

    # Weight configuration for matching
    WEIGHTS = {
        "title_match": 25,
        "skills_match": 30,
        "location_match": 15,
        "salary_match": 15,
        "keywords_match": 10,
        "experience_level": 5
    }

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute matching tasks"""
        action = task.get("action", "")

        if action == "match_job":
            return self._match_single_job(task)
        elif action == "match_jobs":
            return self._match_multiple_jobs(task)
        elif action == "rank_jobs":
            return self._rank_jobs(task)
        elif action == "get_recommendations":
            return self._get_recommendations(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _match_single_job(self, task: Dict[str, Any]) -> AgentOutput:
        """Match a single job to a user"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")

        if not user_id or not job_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id and job_id are required"}
            )

        user = self.database.get_user(user_id)
        job = self.database.get_job(job_id)

        if not user:
            return self.create_output(
                action="error",
                output_data={"error": f"User not found: {user_id}"}
            )

        if not job:
            return self.create_output(
                action="error",
                output_data={"error": f"Job not found: {job_id}"}
            )

        # Calculate match score
        score, breakdown = self._calculate_match_score(user, job)

        # Check filters
        filtered_out, filter_reason = self._check_filters(user, job)

        result = {
            "job_id": job_id,
            "user_id": user_id,
            "match_score": score,
            "score_breakdown": breakdown,
            "filtered_out": filtered_out,
            "filter_reason": filter_reason,
            "recommendation": self._get_recommendation_text(score, filtered_out)
        }

        # Update job status if it's a good match
        if score >= 70 and not filtered_out:
            job["status"] = JobStatus.MATCHED.value
            self.database.save_job(job_id, job)

        return self.create_output(
            action="job_matched",
            output_data=result,
            next_agent="RESUME_TAILOR_AGENT" if score >= 70 and not filtered_out else None,
            pass_data={
                "user_id": user_id,
                "job_id": job_id,
                "match_score": score
            } if score >= 70 and not filtered_out else None
        )

    def _match_multiple_jobs(self, task: Dict[str, Any]) -> AgentOutput:
        """Match multiple jobs to a user"""
        user_id = task.get("user_id")
        job_ids = task.get("job_ids", [])

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        user = self.database.get_user(user_id)
        if not user:
            return self.create_output(
                action="error",
                output_data={"error": f"User not found: {user_id}"}
            )

        # If no job_ids provided, get all new jobs
        if not job_ids:
            jobs = self.database.get_jobs_by_status(JobStatus.NEW.value)
            job_ids = [j["job_id"] for j in jobs]

        matches = []
        qualified_jobs = []

        for job_id in job_ids:
            job = self.database.get_job(job_id)
            if not job:
                continue

            score, breakdown = self._calculate_match_score(user, job)
            filtered_out, filter_reason = self._check_filters(user, job)

            match_result = {
                "job_id": job_id,
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "match_score": score,
                "filtered_out": filtered_out,
                "filter_reason": filter_reason
            }
            matches.append(match_result)

            if score >= 70 and not filtered_out:
                qualified_jobs.append(job_id)
                job["status"] = JobStatus.MATCHED.value
                self.database.save_job(job_id, job)

        # Sort by score
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        return self.create_output(
            action="jobs_matched",
            output_data={
                "user_id": user_id,
                "total_jobs": len(job_ids),
                "qualified_jobs": len(qualified_jobs),
                "matches": matches,
                "qualified_job_ids": qualified_jobs
            },
            next_agent="RESUME_TAILOR_AGENT" if qualified_jobs else None,
            pass_data={
                "user_id": user_id,
                "job_ids": qualified_jobs
            } if qualified_jobs else None
        )

    def _rank_jobs(self, task: Dict[str, Any]) -> AgentOutput:
        """Rank jobs for a user by match score"""
        user_id = task.get("user_id")
        limit = task.get("limit", 20)

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        user = self.database.get_user(user_id)
        if not user:
            return self.create_output(
                action="error",
                output_data={"error": f"User not found: {user_id}"}
            )

        # Get matched jobs
        jobs = self.database.get_jobs_by_status(JobStatus.MATCHED.value)

        ranked = []
        for job in jobs:
            score, _ = self._calculate_match_score(user, job)
            filtered_out, _ = self._check_filters(user, job)

            if not filtered_out:
                ranked.append({
                    "job_id": job["job_id"],
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "match_score": score
                })

        # Sort by score and limit
        ranked.sort(key=lambda x: x["match_score"], reverse=True)
        ranked = ranked[:limit]

        return self.create_output(
            action="jobs_ranked",
            output_data={
                "user_id": user_id,
                "ranked_jobs": ranked,
                "total_count": len(ranked)
            }
        )

    def _get_recommendations(self, task: Dict[str, Any]) -> AgentOutput:
        """Get job recommendations for a user"""
        user_id = task.get("user_id")
        min_score = task.get("min_score", 75)
        limit = task.get("limit", 10)

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        user = self.database.get_user(user_id)
        if not user:
            return self.create_output(
                action="error",
                output_data={"error": f"User not found: {user_id}"}
            )

        # Get all jobs that haven't been applied to
        all_jobs = self.database.search_jobs(limit=500)
        user_apps = self.database.get_user_applications(user_id)
        applied_job_ids = {app["job_id"] for app in user_apps}

        recommendations = []
        for job in all_jobs:
            if job["job_id"] in applied_job_ids:
                continue

            score, breakdown = self._calculate_match_score(user, job)
            filtered_out, _ = self._check_filters(user, job)

            if score >= min_score and not filtered_out:
                recommendations.append({
                    "job_id": job["job_id"],
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "match_score": score,
                    "highlights": self._get_match_highlights(user, job, breakdown)
                })

        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        recommendations = recommendations[:limit]

        return self.create_output(
            action="recommendations_generated",
            output_data={
                "user_id": user_id,
                "recommendations": recommendations,
                "count": len(recommendations)
            }
        )

    def _calculate_match_score(self, user: Dict, job: Dict) -> Tuple[float, Dict]:
        """Calculate match score between user and job"""
        breakdown = {}

        # Title match
        title_score = self._calculate_title_match(user, job)
        breakdown["title_match"] = title_score

        # Skills match
        skills_score = self._calculate_skills_match(user, job)
        breakdown["skills_match"] = skills_score

        # Location match
        location_score = self._calculate_location_match(user, job)
        breakdown["location_match"] = location_score

        # Salary match
        salary_score = self._calculate_salary_match(user, job)
        breakdown["salary_match"] = salary_score

        # Keywords match
        keywords_score = self._calculate_keywords_match(user, job)
        breakdown["keywords_match"] = keywords_score

        # Calculate weighted total
        total_score = sum(
            breakdown[key] * (self.WEIGHTS[key] / 100)
            for key in breakdown
        )

        return round(total_score, 2), breakdown

    def _calculate_title_match(self, user: Dict, job: Dict) -> float:
        """Calculate title match score"""
        target_titles = [t.lower() for t in user.get("job_preferences", {}).get("target_titles", [])]
        job_title = job.get("title", "").lower()

        if not target_titles:
            return 50  # Neutral if no preferences

        # Check for exact or partial matches
        for target in target_titles:
            if target in job_title or job_title in target:
                return 100

            # Check word overlap
            target_words = set(target.split())
            job_words = set(job_title.split())
            overlap = len(target_words & job_words)
            if overlap >= 2:
                return 80
            elif overlap >= 1:
                return 60

        return 30

    def _calculate_skills_match(self, user: Dict, job: Dict) -> float:
        """Calculate skills match score"""
        resume = user.get("resume", {}).get("parsed", {})
        if not resume:
            return 50

        user_skills = set()
        skills_data = resume.get("skills", {})
        if isinstance(skills_data, dict):
            user_skills.update(s.lower() for s in skills_data.get("technical", []))
            user_skills.update(s.lower() for s in skills_data.get("tools", []))

        user_skills.update(s.lower() for s in resume.get("extracted_keywords", []))

        # Extract skills from job requirements
        job_requirements = " ".join(job.get("requirements", []) + [job.get("description", "")])
        job_requirements_lower = job_requirements.lower()

        matched_skills = sum(1 for skill in user_skills if skill in job_requirements_lower)

        if len(user_skills) == 0:
            return 50

        match_ratio = matched_skills / max(len(user_skills), 1)
        return min(100, match_ratio * 100 + 20)

    def _calculate_location_match(self, user: Dict, job: Dict) -> float:
        """Calculate location match score"""
        prefs = user.get("job_preferences", {})
        preferred_locations = [loc.lower() for loc in prefs.get("locations", [])]
        remote_pref = prefs.get("remote_preference", "any")

        job_location = job.get("location", "").lower()
        job_remote = job.get("remote_status", "")

        # Handle remote preference
        if remote_pref == "remote_only":
            if job_remote == "remote":
                return 100
            return 20

        if job_remote == "remote":
            return 90  # Remote is usually acceptable

        # Check location match
        if not preferred_locations:
            return 70  # Neutral if no preferences

        for pref_loc in preferred_locations:
            if pref_loc in job_location or job_location in pref_loc:
                return 100

        return 40

    def _calculate_salary_match(self, user: Dict, job: Dict) -> float:
        """Calculate salary match score"""
        prefs = user.get("job_preferences", {})
        min_salary = prefs.get("salary_min")
        max_salary = prefs.get("salary_max")

        job_salary = job.get("salary_range", {})
        job_min = job_salary.get("min")
        job_max = job_salary.get("max")

        if not min_salary and not max_salary:
            return 70  # Neutral if no preferences

        if not job_min and not job_max:
            return 60  # Unknown job salary

        # Check if job salary meets minimum
        if min_salary and job_max and job_max < min_salary:
            return 20  # Below minimum

        if min_salary and job_min and job_min >= min_salary:
            return 100  # Meets minimum

        if job_min and min_salary:
            ratio = job_min / min_salary
            if ratio >= 0.9:
                return 90
            elif ratio >= 0.8:
                return 70

        return 60

    def _calculate_keywords_match(self, user: Dict, job: Dict) -> float:
        """Calculate keywords match score"""
        filters = user.get("filters", {})
        required = [k.lower() for k in filters.get("required_keywords", [])]
        excluded = [k.lower() for k in filters.get("excluded_keywords", [])]

        job_text = (
            job.get("title", "") + " " +
            job.get("description", "") + " " +
            " ".join(job.get("requirements", []))
        ).lower()

        # Check excluded keywords (immediate disqualification)
        for excl in excluded:
            if excl in job_text:
                return 0

        # Check required keywords
        if not required:
            return 80  # No requirements, generally acceptable

        matched = sum(1 for req in required if req in job_text)
        return (matched / len(required)) * 100

    def _check_filters(self, user: Dict, job: Dict) -> Tuple[bool, Optional[str]]:
        """Check if job passes user filters"""
        filters = user.get("filters", {})

        # Check blacklisted companies
        blacklist = [c.lower() for c in filters.get("blacklisted_companies", [])]
        company = job.get("company", "").lower()

        for blocked in blacklist:
            if blocked in company:
                return True, f"Company '{job.get('company')}' is blacklisted"

        # Check excluded keywords
        excluded = [k.lower() for k in filters.get("excluded_keywords", [])]
        job_text = (
            job.get("title", "") + " " +
            job.get("description", "")
        ).lower()

        for excl in excluded:
            if excl in job_text:
                return True, f"Contains excluded keyword: '{excl}'"

        # Check required keywords
        required = [k.lower() for k in filters.get("required_keywords", [])]
        for req in required:
            if req not in job_text:
                return True, f"Missing required keyword: '{req}'"

        return False, None

    def _get_recommendation_text(self, score: float, filtered_out: bool) -> str:
        """Get recommendation text based on score"""
        if filtered_out:
            return "Not recommended - failed filters"
        elif score >= 90:
            return "Highly recommended - excellent match"
        elif score >= 80:
            return "Recommended - strong match"
        elif score >= 70:
            return "Consider applying - good match"
        elif score >= 60:
            return "Possible fit - review carefully"
        else:
            return "Low match - may not be suitable"

    def _get_match_highlights(self, user: Dict, job: Dict, breakdown: Dict) -> List[str]:
        """Get highlights of why job matches"""
        highlights = []

        if breakdown.get("title_match", 0) >= 80:
            highlights.append("Title matches your target roles")

        if breakdown.get("skills_match", 0) >= 70:
            highlights.append("Good skills alignment")

        if breakdown.get("location_match", 0) >= 90:
            highlights.append("Location matches preferences")

        if breakdown.get("salary_match", 0) >= 80:
            highlights.append("Salary meets expectations")

        return highlights
