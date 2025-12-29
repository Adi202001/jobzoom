#!/usr/bin/env python3
"""JobCopilot - Main entry point for programmatic usage"""

from typing import Any, Dict, List, Optional

from .core.orchestrator import Orchestrator
from .core.registry import AgentRegistry
from .utils.memory import SharedMemory
from .utils.database import Database

# Import agents to register them
from .agents import (
    ProfileAgent,
    ResumeParserAgent,
    ScraperAgent,
    MatcherAgent,
    ResumeTailorAgent,
    CoverLetterAgent,
    FormFillerAgent,
    QAAgent,
    TrackerAgent,
    DigestAgent,
)


class JobCopilot:
    """Main JobCopilot interface for programmatic usage"""

    def __init__(
        self,
        memory_path: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """Initialize JobCopilot system"""
        self.memory = SharedMemory(memory_path)
        self.database = Database(db_path)
        self.orchestrator = Orchestrator(self.memory, self.database)

    # Profile operations
    def create_profile(
        self,
        name: str,
        email: str,
        phone: str = "",
        location: str = "",
        linkedin: str = "",
        resume_path: Optional[str] = None,
        resume_text: Optional[str] = None,
        target_titles: Optional[List[str]] = None,
        preferred_locations: Optional[List[str]] = None,
        remote_preference: str = "any",
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new user profile"""
        task = {
            "action": "create_profile",
            "personal": {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "linkedin": linkedin
            },
            "job_preferences": {
                "target_titles": target_titles or [],
                "locations": preferred_locations or [],
                "remote_preference": remote_preference,
                "salary_min": salary_min,
                "salary_max": salary_max
            },
            "resume_path": resume_path,
            "resume_text": resume_text
        }
        result = self.orchestrator.execute_agent("PROFILE_AGENT", task)
        return result.output_data

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        result = self.orchestrator.execute_agent("PROFILE_AGENT", {
            "action": "get_profile",
            "user_id": user_id
        })
        return result.output_data

    def update_preferences(
        self,
        user_id: str,
        target_titles: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        remote_preference: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update job preferences"""
        preferences = {}
        if target_titles is not None:
            preferences["target_titles"] = target_titles
        if locations is not None:
            preferences["locations"] = locations
        if remote_preference is not None:
            preferences["remote_preference"] = remote_preference
        if salary_min is not None:
            preferences["salary_min"] = salary_min
        if salary_max is not None:
            preferences["salary_max"] = salary_max

        result = self.orchestrator.execute_agent("PROFILE_AGENT", {
            "action": "update_preferences",
            "user_id": user_id,
            "preferences": preferences
        })
        return result.output_data

    # Resume operations
    def parse_resume(
        self,
        user_id: str,
        resume_text: Optional[str] = None,
        resume_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse and extract resume data"""
        result = self.orchestrator.execute_agent("RESUME_PARSER_AGENT", {
            "action": "parse_resume",
            "user_id": user_id,
            "resume_text": resume_text,
            "resume_path": resume_path
        })
        return result.output_data

    # Job operations
    def scrape_jobs(
        self,
        url: Optional[str] = None,
        company: Optional[str] = None,
        user_id: Optional[str] = None,
        auto_match: bool = True
    ) -> Dict[str, Any]:
        """Scrape jobs from URL or company career page"""
        if url:
            task = {
                "action": "scrape_url",
                "url": url,
                "user_id": user_id,
                "auto_match": auto_match and bool(user_id)
            }
        elif company:
            task = {
                "action": "scrape_company",
                "company": company,
                "user_id": user_id,
                "auto_match": auto_match and bool(user_id)
            }
        else:
            task = {
                "action": "scrape_new_jobs",
                "user_id": user_id
            }

        result = self.orchestrator.execute_agent("SCRAPER_AGENT", task)
        return result.output_data

    def match_jobs(
        self,
        user_id: str,
        job_id: Optional[str] = None,
        job_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Match jobs to user profile"""
        if job_id:
            task = {
                "action": "match_job",
                "user_id": user_id,
                "job_id": job_id
            }
        else:
            task = {
                "action": "match_jobs",
                "user_id": user_id,
                "job_ids": job_ids or []
            }

        result = self.orchestrator.execute_agent("MATCHER_AGENT", task)
        return result.output_data

    def get_recommendations(
        self,
        user_id: str,
        min_score: int = 75,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get job recommendations for user"""
        result = self.orchestrator.execute_agent("MATCHER_AGENT", {
            "action": "get_recommendations",
            "user_id": user_id,
            "min_score": min_score,
            "limit": limit
        })
        return result.output_data

    # Application operations
    def prepare_application(
        self,
        user_id: str,
        job_id: str
    ) -> List[Dict[str, Any]]:
        """Prepare a complete application (resume, cover letter, forms)"""
        results = self.orchestrator.execute_workflow(
            "RESUME_TAILOR_AGENT",
            {
                "action": "tailor_resume",
                "user_id": user_id,
                "job_id": job_id
            }
        )
        return [r.output_data for r in results]

    def tailor_resume(
        self,
        user_id: str,
        job_id: str
    ) -> Dict[str, Any]:
        """Tailor resume for a specific job"""
        result = self.orchestrator.execute_agent("RESUME_TAILOR_AGENT", {
            "action": "tailor_resume",
            "user_id": user_id,
            "job_id": job_id
        })
        return result.output_data

    def generate_cover_letter(
        self,
        user_id: str,
        job_id: str,
        template: str = "professional"
    ) -> Dict[str, Any]:
        """Generate a cover letter"""
        result = self.orchestrator.execute_agent("COVER_LETTER_AGENT", {
            "action": "generate_letter",
            "user_id": user_id,
            "job_id": job_id,
            "template": template
        })
        return result.output_data

    def answer_question(
        self,
        question: str,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Answer an application question"""
        result = self.orchestrator.execute_agent("QA_AGENT", {
            "action": "answer_question",
            "question": question,
            "user_id": user_id,
            "job_id": job_id
        })
        return result.output_data

    # Tracking operations
    def create_application(
        self,
        user_id: str,
        job_id: str,
        match_score: float = 0
    ) -> Dict[str, Any]:
        """Create an application record"""
        result = self.orchestrator.execute_agent("TRACKER_AGENT", {
            "action": "create_application",
            "user_id": user_id,
            "job_id": job_id,
            "match_score": match_score
        })
        return result.output_data

    def update_application_status(
        self,
        app_id: str,
        status: str,
        note: str = ""
    ) -> Dict[str, Any]:
        """Update application status"""
        result = self.orchestrator.execute_agent("TRACKER_AGENT", {
            "action": "update_status",
            "app_id": app_id,
            "status": status,
            "note": note
        })
        return result.output_data

    def get_applications(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all applications for a user"""
        result = self.orchestrator.execute_agent("TRACKER_AGENT", {
            "action": "get_all_applications",
            "user_id": user_id,
            "status": status
        })
        return result.output_data

    # Digest operations
    def get_daily_digest(self, user_id: str) -> Dict[str, Any]:
        """Get daily digest"""
        result = self.orchestrator.execute_agent("DIGEST_AGENT", {
            "action": "generate_digest",
            "user_id": user_id
        })
        return result.output_data

    def get_weekly_summary(self, user_id: str) -> Dict[str, Any]:
        """Get weekly summary"""
        result = self.orchestrator.execute_agent("DIGEST_AGENT", {
            "action": "weekly_summary",
            "user_id": user_id
        })
        return result.output_data

    def get_pipeline_report(self, user_id: str) -> Dict[str, Any]:
        """Get pipeline status report"""
        result = self.orchestrator.execute_agent("DIGEST_AGENT", {
            "action": "pipeline_report",
            "user_id": user_id
        })
        return result.output_data

    # Pipeline operations
    def run_full_pipeline(self, user_id: str) -> List[Dict[str, Any]]:
        """Run the full application pipeline"""
        results = self.orchestrator.run_pipeline(user_id, "full_application")
        return [r.output_data for r in results]

    def run_daily_digest_pipeline(self, user_id: str) -> List[Dict[str, Any]]:
        """Run the daily digest pipeline"""
        results = self.orchestrator.run_pipeline(user_id, "daily_digest")
        return [r.output_data for r in results]

    # System operations
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return self.orchestrator.get_system_status()

    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return AgentRegistry.list_agents()

    def execute_agent(
        self,
        agent_name: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific agent directly"""
        result = self.orchestrator.execute_agent(agent_name, task)
        return result.output_data


# Create a default instance for convenience
_default_instance: Optional[JobCopilot] = None


def get_copilot() -> JobCopilot:
    """Get the default JobCopilot instance"""
    global _default_instance
    if _default_instance is None:
        _default_instance = JobCopilot()
    return _default_instance
