"""Resume Tailor Agent - Customizes resumes for specific jobs"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput


@AgentRegistry.register
class ResumeTailorAgent(BaseAgent):
    """Agent responsible for tailoring resumes to specific job descriptions"""

    @property
    def name(self) -> str:
        return "RESUME_TAILOR_AGENT"

    @property
    def description(self) -> str:
        return "Customizes resumes to match specific job requirements"

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute resume tailoring tasks"""
        action = task.get("action", "")

        if action == "tailor_resume":
            return self._tailor_resume(task)
        elif action == "tailor_resumes":
            return self._tailor_multiple_resumes(task)
        elif action == "suggest_improvements":
            return self._suggest_improvements(task)
        elif action == "highlight_skills":
            return self._highlight_skills(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _tailor_resume(self, task: Dict[str, Any]) -> AgentOutput:
        """Tailor a resume for a specific job"""
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

        resume = user.get("resume", {})
        if not resume.get("parsed"):
            return self.create_output(
                action="error",
                output_data={"error": "No parsed resume found for user"}
            )

        # Analyze job requirements
        job_keywords = self._extract_job_keywords(job)

        # Tailor the resume
        tailored = self._create_tailored_resume(
            resume["parsed"],
            job,
            job_keywords,
            user.get("personal", {})
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(resume["parsed"], job, job_keywords)

        result = {
            "user_id": user_id,
            "job_id": job_id,
            "tailored_resume": tailored,
            "suggestions": suggestions,
            "keywords_used": job_keywords[:15],
            "tailoring_notes": self._get_tailoring_notes(resume["parsed"], job_keywords)
        }

        return self.create_output(
            action="resume_tailored",
            output_data=result,
            next_agent="COVER_LETTER_AGENT",
            pass_data={
                "user_id": user_id,
                "job_id": job_id,
                "tailored_resume": tailored,
                "job_keywords": job_keywords
            }
        )

    def _tailor_multiple_resumes(self, task: Dict[str, Any]) -> AgentOutput:
        """Tailor resumes for multiple jobs"""
        user_id = task.get("user_id")
        job_ids = task.get("job_ids", [])

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        if not job_ids:
            return self.create_output(
                action="error",
                output_data={"error": "job_ids are required"}
            )

        results = []
        for job_id in job_ids:
            result = self._tailor_resume({
                "user_id": user_id,
                "job_id": job_id
            })
            results.append({
                "job_id": job_id,
                "success": "error" not in result.output_data,
                "output": result.output_data
            })

        return self.create_output(
            action="resumes_tailored",
            output_data={
                "user_id": user_id,
                "total_jobs": len(job_ids),
                "successful": sum(1 for r in results if r["success"]),
                "results": results
            }
        )

    def _suggest_improvements(self, task: Dict[str, Any]) -> AgentOutput:
        """Suggest improvements for a resume based on job requirements"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")

        user = self.database.get_user(user_id)
        job = self.database.get_job(job_id)

        if not user or not job:
            return self.create_output(
                action="error",
                output_data={"error": "User or job not found"}
            )

        resume = user.get("resume", {}).get("parsed", {})
        job_keywords = self._extract_job_keywords(job)

        suggestions = self._generate_suggestions(resume, job, job_keywords)

        return self.create_output(
            action="improvements_suggested",
            output_data={
                "user_id": user_id,
                "job_id": job_id,
                "suggestions": suggestions
            }
        )

    def _highlight_skills(self, task: Dict[str, Any]) -> AgentOutput:
        """Highlight skills relevant to a job"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")

        user = self.database.get_user(user_id)
        job = self.database.get_job(job_id)

        if not user or not job:
            return self.create_output(
                action="error",
                output_data={"error": "User or job not found"}
            )

        resume = user.get("resume", {}).get("parsed", {})
        job_keywords = self._extract_job_keywords(job)

        # Find matching skills
        user_skills = set()
        skills_data = resume.get("skills", {})
        if isinstance(skills_data, dict):
            user_skills.update(s.lower() for s in skills_data.get("technical", []))
            user_skills.update(s.lower() for s in skills_data.get("tools", []))
        user_skills.update(s.lower() for s in resume.get("extracted_keywords", []))

        matching = [s for s in user_skills if s in [k.lower() for k in job_keywords]]
        missing = [k for k in job_keywords if k.lower() not in user_skills]

        return self.create_output(
            action="skills_highlighted",
            output_data={
                "matching_skills": matching,
                "missing_skills": missing[:10],
                "recommendation": self._get_skills_recommendation(matching, missing)
            }
        )

    def _extract_job_keywords(self, job: Dict) -> List[str]:
        """Extract important keywords from job description"""
        text = (
            job.get("title", "") + " " +
            job.get("description", "") + " " +
            " ".join(job.get("requirements", []))
        )

        keywords = set()

        # Technical terms pattern
        tech_patterns = [
            r'\b(?:Python|JavaScript|TypeScript|Java|C\+\+|Go|Rust|Ruby|PHP|Swift|Kotlin)\b',
            r'\b(?:React|Angular|Vue|Django|Flask|FastAPI|Spring|Node\.js|Express)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Terraform|Jenkins|Git)\b',
            r'\b(?:PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|SQL)\b',
            r'\b(?:REST|GraphQL|API|Microservices|CI/CD|DevOps|Agile|Scrum)\b',
            r'\b(?:Machine Learning|Deep Learning|AI|Data Science|Analytics)\b'
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(m for m in matches)

        # Years of experience
        exp_match = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if exp_match:
            keywords.add(f"{exp_match[0]}+ years experience")

        # Degree requirements
        degree_match = re.findall(r"(?:Bachelor|Master|Ph\.?D|MBA)(?:'?s)?\s*(?:degree)?", text, re.IGNORECASE)
        keywords.update(degree_match)

        return list(keywords)

    def _create_tailored_resume(
        self,
        parsed_resume: Dict,
        job: Dict,
        job_keywords: List[str],
        personal: Dict
    ) -> str:
        """Create a tailored resume text"""
        lines = []

        # Header
        name = personal.get("name", "")
        email = personal.get("email", "")
        phone = personal.get("phone", "")
        linkedin = personal.get("linkedin", "")

        lines.append(f"# {name}")
        contact_parts = [p for p in [email, phone, linkedin] if p]
        lines.append(" | ".join(contact_parts))
        lines.append("")

        # Tailored Summary
        original_summary = parsed_resume.get("summary", "")
        tailored_summary = self._tailor_summary(original_summary, job, job_keywords)
        lines.append("## Professional Summary")
        lines.append(tailored_summary)
        lines.append("")

        # Skills (prioritized by job relevance)
        skills = parsed_resume.get("skills", {})
        prioritized_skills = self._prioritize_skills(skills, job_keywords)
        lines.append("## Technical Skills")
        lines.append(", ".join(prioritized_skills[:20]))
        lines.append("")

        # Experience (with tailored bullets)
        lines.append("## Professional Experience")
        for exp in parsed_resume.get("experience", []):
            lines.append(f"### {exp.get('title', '')} at {exp.get('company', '')}")
            lines.append(f"*{exp.get('duration', '')}*")
            tailored_bullets = self._tailor_bullets(exp.get("bullets", []), job_keywords)
            for bullet in tailored_bullets:
                lines.append(f"- {bullet}")
            lines.append("")

        # Education
        lines.append("## Education")
        for edu in parsed_resume.get("education", []):
            lines.append(f"**{edu.get('degree', '')}** - {edu.get('institution', '')} ({edu.get('year', '')})")
        lines.append("")

        # Certifications (if relevant)
        certs = parsed_resume.get("certifications", [])
        if certs:
            lines.append("## Certifications")
            for cert in certs[:5]:
                lines.append(f"- {cert}")
            lines.append("")

        # Projects (if relevant to job)
        projects = parsed_resume.get("projects", [])
        relevant_projects = self._filter_relevant_projects(projects, job_keywords)
        if relevant_projects:
            lines.append("## Key Projects")
            for proj in relevant_projects[:3]:
                lines.append(f"### {proj.get('name', '')}")
                lines.append(proj.get("description", ""))
                if proj.get("tech"):
                    lines.append(f"*Technologies: {', '.join(proj['tech'])}*")
                lines.append("")

        return "\n".join(lines)

    def _tailor_summary(self, summary: str, job: Dict, keywords: List[str]) -> str:
        """Tailor the professional summary for the job"""
        job_title = job.get("title", "")
        company = job.get("company", "")

        # Start with base summary
        if not summary:
            summary = "Experienced professional"

        # Enhance with job-relevant keywords
        keyword_additions = []
        for keyword in keywords[:5]:
            if keyword.lower() not in summary.lower():
                keyword_additions.append(keyword)

        if keyword_additions:
            summary += f" with expertise in {', '.join(keyword_additions[:3])}"

        # Add job focus if not present
        if job_title and job_title.lower() not in summary.lower():
            summary = f"{job_title} professional. " + summary

        return summary[:500]  # Limit length

    def _prioritize_skills(self, skills: Dict, job_keywords: List[str]) -> List[str]:
        """Prioritize skills based on job relevance"""
        all_skills = []
        if isinstance(skills, dict):
            all_skills.extend(skills.get("technical", []))
            all_skills.extend(skills.get("tools", []))
            all_skills.extend(skills.get("soft", []))

        job_keywords_lower = [k.lower() for k in job_keywords]

        # Sort by relevance to job
        prioritized = sorted(
            all_skills,
            key=lambda s: (
                -1 if s.lower() in job_keywords_lower else 0,
                s.lower()
            )
        )

        return prioritized

    def _tailor_bullets(self, bullets: List[str], job_keywords: List[str]) -> List[str]:
        """Tailor experience bullets for the job"""
        if not bullets:
            return []

        job_keywords_lower = [k.lower() for k in job_keywords]

        # Score and sort bullets by relevance
        scored_bullets = []
        for bullet in bullets:
            score = sum(1 for k in job_keywords_lower if k in bullet.lower())
            scored_bullets.append((score, bullet))

        scored_bullets.sort(key=lambda x: x[0], reverse=True)

        # Return top bullets, ensuring at least some content
        return [b for _, b in scored_bullets[:5]]

    def _filter_relevant_projects(self, projects: List[Dict], job_keywords: List[str]) -> List[Dict]:
        """Filter projects relevant to the job"""
        job_keywords_lower = [k.lower() for k in job_keywords]

        relevant = []
        for proj in projects:
            text = (
                proj.get("name", "") + " " +
                proj.get("description", "") + " " +
                " ".join(proj.get("tech", []))
            ).lower()

            if any(k in text for k in job_keywords_lower):
                relevant.append(proj)

        return relevant

    def _generate_suggestions(self, resume: Dict, job: Dict, job_keywords: List[str]) -> List[Dict]:
        """Generate suggestions for improving resume match"""
        suggestions = []

        # Check for missing keywords
        resume_text = str(resume).lower()
        missing_keywords = [k for k in job_keywords if k.lower() not in resume_text]

        if missing_keywords:
            suggestions.append({
                "type": "add_keywords",
                "priority": "high",
                "message": f"Consider adding these keywords: {', '.join(missing_keywords[:5])}",
                "keywords": missing_keywords[:10]
            })

        # Check experience alignment
        experience = resume.get("experience", [])
        if not experience:
            suggestions.append({
                "type": "add_experience",
                "priority": "high",
                "message": "Add relevant work experience to your resume"
            })

        # Check for quantified achievements
        has_numbers = any(
            re.search(r'\d+%|\$\d+|\d+\s*(?:users|customers|projects)', str(exp))
            for exp in experience
        )
        if not has_numbers:
            suggestions.append({
                "type": "add_metrics",
                "priority": "medium",
                "message": "Add quantified achievements (e.g., 'increased sales by 20%')"
            })

        # Check skills section
        skills = resume.get("skills", {})
        if not skills or (isinstance(skills, dict) and not skills.get("technical")):
            suggestions.append({
                "type": "add_skills",
                "priority": "high",
                "message": "Add a technical skills section highlighting relevant technologies"
            })

        return suggestions

    def _get_tailoring_notes(self, resume: Dict, job_keywords: List[str]) -> List[str]:
        """Get notes about what was tailored"""
        notes = []

        resume_text = str(resume).lower()
        matched = [k for k in job_keywords if k.lower() in resume_text]

        if matched:
            notes.append(f"Emphasized {len(matched)} matching skills/keywords")

        notes.append("Reordered experience bullets by relevance")
        notes.append("Prioritized skills matching job requirements")

        return notes

    def _get_skills_recommendation(self, matching: List, missing: List) -> str:
        """Get recommendation based on skills match"""
        match_ratio = len(matching) / max(len(matching) + len(missing), 1)

        if match_ratio >= 0.8:
            return "Excellent skills match. Your resume aligns well with this role."
        elif match_ratio >= 0.6:
            return "Good skills match. Consider highlighting the matching skills more prominently."
        elif match_ratio >= 0.4:
            return "Moderate match. Consider emphasizing transferable skills and relevant projects."
        else:
            return "Limited direct match. Focus on transferable skills and demonstrate learning ability."
