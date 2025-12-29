"""Profile Agent - Manages user data and preferences"""

from typing import Any, Dict, Optional
import uuid
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import (
    AgentOutput, UserProfile, Personal, JobPreferences,
    Filters, Resume, RemotePreference
)


@AgentRegistry.register
class ProfileAgent(BaseAgent):
    """Agent responsible for managing user profiles and preferences"""

    @property
    def name(self) -> str:
        return "PROFILE_AGENT"

    @property
    def description(self) -> str:
        return "Manages user data, preferences, and profile information"

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute profile management tasks"""
        action = task.get("action", "")

        if action == "create_profile":
            return self._create_profile(task)
        elif action == "update_profile":
            return self._update_profile(task)
        elif action == "get_profile":
            return self._get_profile(task)
        elif action == "update_preferences":
            return self._update_preferences(task)
        elif action == "update_filters":
            return self._update_filters(task)
        elif action == "set_resume":
            return self._set_resume(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _create_profile(self, task: Dict[str, Any]) -> AgentOutput:
        """Create a new user profile"""
        user_id = task.get("user_id") or str(uuid.uuid4())

        # Check if profile already exists
        existing = self.database.get_user(user_id)
        if existing:
            return self.create_output(
                action="profile_exists",
                output_data={"user_id": user_id, "message": "Profile already exists"}
            )

        # Create new profile
        profile = UserProfile(user_id=user_id)

        # Set personal info if provided
        personal_data = task.get("personal", {})
        if personal_data:
            profile.personal = Personal(
                name=personal_data.get("name", ""),
                email=personal_data.get("email", ""),
                phone=personal_data.get("phone", ""),
                location=personal_data.get("location", ""),
                linkedin=personal_data.get("linkedin", "")
            )

        # Set job preferences if provided
        prefs_data = task.get("job_preferences", {})
        if prefs_data:
            remote_pref = prefs_data.get("remote_preference", "any")
            profile.job_preferences = JobPreferences(
                target_titles=prefs_data.get("target_titles", []),
                locations=prefs_data.get("locations", []),
                remote_preference=RemotePreference(remote_pref),
                salary_min=prefs_data.get("salary_min"),
                salary_max=prefs_data.get("salary_max"),
                job_types=prefs_data.get("job_types", ["full-time"])
            )

        # Set filters if provided
        filters_data = task.get("filters", {})
        if filters_data:
            profile.filters = Filters(
                required_keywords=filters_data.get("required_keywords", []),
                excluded_keywords=filters_data.get("excluded_keywords", []),
                blacklisted_companies=filters_data.get("blacklisted_companies", [])
            )

        # Save to database
        profile_dict = profile.to_dict()
        self.database.save_user(user_id, profile_dict)

        # Determine next agent
        next_agent = None
        pass_data = None
        if task.get("resume_path") or task.get("resume_text"):
            next_agent = "RESUME_PARSER_AGENT"
            pass_data = {
                "user_id": user_id,
                "resume_path": task.get("resume_path"),
                "resume_text": task.get("resume_text")
            }

        return self.create_output(
            action="profile_created",
            output_data=profile_dict,
            next_agent=next_agent,
            pass_data=pass_data,
            save_to_memory={f"users.{user_id}": profile_dict}
        )

    def _update_profile(self, task: Dict[str, Any]) -> AgentOutput:
        """Update an existing user profile"""
        user_id = task.get("user_id")
        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        profile = self.database.get_user(user_id)
        if not profile:
            return self.create_output(
                action="error",
                output_data={"error": f"Profile not found: {user_id}"}
            )

        # Update personal info if provided
        if "personal" in task:
            profile["personal"].update(task["personal"])

        # Update job preferences if provided
        if "job_preferences" in task:
            profile["job_preferences"].update(task["job_preferences"])

        # Update filters if provided
        if "filters" in task:
            profile["filters"].update(task["filters"])

        # Save updated profile
        self.database.save_user(user_id, profile)

        return self.create_output(
            action="profile_updated",
            output_data=profile,
            save_to_memory={f"users.{user_id}": profile}
        )

    def _get_profile(self, task: Dict[str, Any]) -> AgentOutput:
        """Get a user profile"""
        user_id = task.get("user_id")
        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        profile = self.database.get_user(user_id)
        if not profile:
            return self.create_output(
                action="error",
                output_data={"error": f"Profile not found: {user_id}"}
            )

        return self.create_output(
            action="profile_retrieved",
            output_data=profile
        )

    def _update_preferences(self, task: Dict[str, Any]) -> AgentOutput:
        """Update job preferences"""
        user_id = task.get("user_id")
        preferences = task.get("preferences", {})

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        profile = self.database.get_user(user_id)
        if not profile:
            return self.create_output(
                action="error",
                output_data={"error": f"Profile not found: {user_id}"}
            )

        profile["job_preferences"].update(preferences)
        self.database.save_user(user_id, profile)

        return self.create_output(
            action="preferences_updated",
            output_data={"user_id": user_id, "job_preferences": profile["job_preferences"]}
        )

    def _update_filters(self, task: Dict[str, Any]) -> AgentOutput:
        """Update job filters"""
        user_id = task.get("user_id")
        filters = task.get("filters", {})

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        profile = self.database.get_user(user_id)
        if not profile:
            return self.create_output(
                action="error",
                output_data={"error": f"Profile not found: {user_id}"}
            )

        profile["filters"].update(filters)
        self.database.save_user(user_id, profile)

        return self.create_output(
            action="filters_updated",
            output_data={"user_id": user_id, "filters": profile["filters"]}
        )

    def _set_resume(self, task: Dict[str, Any]) -> AgentOutput:
        """Set resume for user"""
        user_id = task.get("user_id")
        resume_text = task.get("resume_text", "")
        resume_path = task.get("resume_path", "")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        profile = self.database.get_user(user_id)
        if not profile:
            return self.create_output(
                action="error",
                output_data={"error": f"Profile not found: {user_id}"}
            )

        profile["resume"]["raw_text"] = resume_text
        profile["resume"]["file_path"] = resume_path
        self.database.save_user(user_id, profile)

        # Trigger resume parsing
        return self.create_output(
            action="resume_set",
            output_data={"user_id": user_id},
            next_agent="RESUME_PARSER_AGENT",
            pass_data={
                "user_id": user_id,
                "resume_text": resume_text,
                "resume_path": resume_path
            }
        )
