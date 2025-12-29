"""Tracker Agent - Tracks application status"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput, ApplicationStatus, TimelineEntry


@AgentRegistry.register
class TrackerAgent(BaseAgent):
    """Agent responsible for tracking application status and history"""

    @property
    def name(self) -> str:
        return "TRACKER_AGENT"

    @property
    def description(self) -> str:
        return "Tracks application status and maintains application history"

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute tracking tasks"""
        action = task.get("action", "")

        if action == "create_application":
            return self._create_application(task)
        elif action == "update_status":
            return self._update_status(task)
        elif action == "get_status":
            return self._get_status(task)
        elif action == "get_all_applications":
            return self._get_all_applications(task)
        elif action == "update_tracking":
            return self._update_tracking(task)
        elif action == "refresh_status":
            return self._refresh_status(task)
        elif action == "get_timeline":
            return self._get_timeline(task)
        elif action == "add_note":
            return self._add_note(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _create_application(self, task: Dict[str, Any]) -> AgentOutput:
        """Create a new application record"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")
        application_data = task.get("application_data", {})

        if not user_id or not job_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id and job_id are required"}
            )

        # Check if application already exists
        existing = self._find_existing_application(user_id, job_id)
        if existing:
            return self.create_output(
                action="application_exists",
                output_data={
                    "app_id": existing["app_id"],
                    "status": existing["status"],
                    "message": "Application already exists for this job"
                }
            )

        # Create new application
        app_id = str(uuid.uuid4())[:12]
        now = datetime.now().isoformat()

        application = {
            "app_id": app_id,
            "user_id": user_id,
            "job_id": job_id,
            "status": ApplicationStatus.PREPARING.value,
            "match_score": task.get("match_score", 0),
            "tailored_resume": application_data.get("tailored_resume", ""),
            "cover_letter": application_data.get("cover_letter", ""),
            "form_answers": application_data.get("form_answers", {}),
            "submitted_at": None,
            "created_at": now,
            "updated_at": now,
            "timeline": [{
                "status": ApplicationStatus.PREPARING.value,
                "date": now,
                "note": "Application created"
            }]
        }

        self.database.save_application(app_id, application)

        return self.create_output(
            action="application_created",
            output_data={
                "app_id": app_id,
                "user_id": user_id,
                "job_id": job_id,
                "status": ApplicationStatus.PREPARING.value
            },
            save_to_memory={
                f"applications.{app_id}": application
            }
        )

    def _update_status(self, task: Dict[str, Any]) -> AgentOutput:
        """Update application status"""
        app_id = task.get("app_id")
        new_status = task.get("status")
        note = task.get("note", "")

        if not app_id or not new_status:
            return self.create_output(
                action="error",
                output_data={"error": "app_id and status are required"}
            )

        # Validate status
        try:
            status_enum = ApplicationStatus(new_status)
        except ValueError:
            return self.create_output(
                action="error",
                output_data={"error": f"Invalid status: {new_status}"}
            )

        application = self.database.get_application(app_id)
        if not application:
            return self.create_output(
                action="error",
                output_data={"error": f"Application not found: {app_id}"}
            )

        old_status = application.get("status")
        now = datetime.now().isoformat()

        # Update status
        application["status"] = new_status
        application["updated_at"] = now

        # Add to timeline
        timeline = application.get("timeline", [])
        timeline.append({
            "status": new_status,
            "date": now,
            "note": note or f"Status changed from {old_status} to {new_status}"
        })
        application["timeline"] = timeline

        # Set submitted_at if newly submitted
        if new_status == ApplicationStatus.SUBMITTED.value and not application.get("submitted_at"):
            application["submitted_at"] = now

        self.database.save_application(app_id, application)

        return self.create_output(
            action="status_updated",
            output_data={
                "app_id": app_id,
                "old_status": old_status,
                "new_status": new_status,
                "updated_at": now
            }
        )

    def _get_status(self, task: Dict[str, Any]) -> AgentOutput:
        """Get status of an application"""
        app_id = task.get("app_id")

        if not app_id:
            return self.create_output(
                action="error",
                output_data={"error": "app_id is required"}
            )

        application = self.database.get_application(app_id)
        if not application:
            return self.create_output(
                action="error",
                output_data={"error": f"Application not found: {app_id}"}
            )

        # Get job details
        job = self.database.get_job(application.get("job_id", ""))

        return self.create_output(
            action="status_retrieved",
            output_data={
                "app_id": app_id,
                "status": application.get("status"),
                "job_title": job.get("title", "") if job else "",
                "company": job.get("company", "") if job else "",
                "match_score": application.get("match_score", 0),
                "submitted_at": application.get("submitted_at"),
                "last_updated": application.get("updated_at"),
                "days_since_submission": self._calculate_days_since(
                    application.get("submitted_at")
                )
            }
        )

    def _get_all_applications(self, task: Dict[str, Any]) -> AgentOutput:
        """Get all applications for a user"""
        user_id = task.get("user_id")
        status_filter = task.get("status")
        limit = task.get("limit", 50)

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        applications = self.database.get_user_applications(user_id, status_filter)

        # Enrich with job details
        enriched = []
        for app in applications[:limit]:
            job = self.database.get_job(app.get("job_id", ""))
            enriched.append({
                "app_id": app.get("app_id"),
                "job_id": app.get("job_id"),
                "job_title": job.get("title", "") if job else "",
                "company": job.get("company", "") if job else "",
                "status": app.get("status"),
                "match_score": app.get("match_score", 0),
                "submitted_at": app.get("submitted_at"),
                "days_since_submission": self._calculate_days_since(
                    app.get("submitted_at")
                )
            })

        # Get stats
        stats = self.database.get_application_stats(user_id)

        return self.create_output(
            action="applications_retrieved",
            output_data={
                "user_id": user_id,
                "total_applications": len(applications),
                "applications": enriched,
                "stats": stats
            }
        )

    def _update_tracking(self, task: Dict[str, Any]) -> AgentOutput:
        """Update tracking for new applications in pipeline"""
        user_id = task.get("user_id")
        job_ids = task.get("job_ids", [])
        application_data = task.get("application_data")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        created = []
        updated = []

        for job_id in job_ids:
            existing = self._find_existing_application(user_id, job_id)

            if existing:
                # Update existing application
                if application_data:
                    existing.update(application_data)
                    existing["updated_at"] = datetime.now().isoformat()
                    self.database.save_application(existing["app_id"], existing)
                    updated.append(existing["app_id"])
            else:
                # Create new application
                result = self._create_application({
                    "user_id": user_id,
                    "job_id": job_id,
                    "application_data": application_data or {}
                })
                if result.output_data.get("app_id"):
                    created.append(result.output_data["app_id"])

        return self.create_output(
            action="tracking_updated",
            output_data={
                "user_id": user_id,
                "created_count": len(created),
                "updated_count": len(updated),
                "created_apps": created,
                "updated_apps": updated
            },
            next_agent="DIGEST_AGENT",
            pass_data={
                "user_id": user_id,
                "new_applications": created
            }
        )

    def _refresh_status(self, task: Dict[str, Any]) -> AgentOutput:
        """Refresh status of all pending applications"""
        user_id = task.get("user_id")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        # Get all non-terminal applications
        all_apps = self.database.get_user_applications(user_id)
        pending_statuses = [
            ApplicationStatus.PREPARING.value,
            ApplicationStatus.READY.value,
            ApplicationStatus.SUBMITTED.value,
            ApplicationStatus.INTERVIEW.value
        ]

        pending_apps = [
            app for app in all_apps
            if app.get("status") in pending_statuses
        ]

        refreshed = []
        stale = []

        for app in pending_apps:
            submitted_at = app.get("submitted_at")
            if submitted_at:
                days = self._calculate_days_since(submitted_at)
                if days and days > 30:
                    stale.append({
                        "app_id": app["app_id"],
                        "days_since_submission": days,
                        "status": app["status"]
                    })
            refreshed.append(app["app_id"])

        return self.create_output(
            action="status_refreshed",
            output_data={
                "user_id": user_id,
                "total_refreshed": len(refreshed),
                "stale_applications": stale,
                "pending_count": len(pending_apps)
            }
        )

    def _get_timeline(self, task: Dict[str, Any]) -> AgentOutput:
        """Get timeline for an application"""
        app_id = task.get("app_id")

        if not app_id:
            return self.create_output(
                action="error",
                output_data={"error": "app_id is required"}
            )

        application = self.database.get_application(app_id)
        if not application:
            return self.create_output(
                action="error",
                output_data={"error": f"Application not found: {app_id}"}
            )

        timeline = application.get("timeline", [])

        return self.create_output(
            action="timeline_retrieved",
            output_data={
                "app_id": app_id,
                "timeline": timeline,
                "current_status": application.get("status"),
                "total_events": len(timeline)
            }
        )

    def _add_note(self, task: Dict[str, Any]) -> AgentOutput:
        """Add a note to an application timeline"""
        app_id = task.get("app_id")
        note = task.get("note", "")

        if not app_id or not note:
            return self.create_output(
                action="error",
                output_data={"error": "app_id and note are required"}
            )

        application = self.database.get_application(app_id)
        if not application:
            return self.create_output(
                action="error",
                output_data={"error": f"Application not found: {app_id}"}
            )

        now = datetime.now().isoformat()

        # Add note to timeline
        timeline = application.get("timeline", [])
        timeline.append({
            "status": application.get("status"),
            "date": now,
            "note": note
        })
        application["timeline"] = timeline
        application["updated_at"] = now

        self.database.save_application(app_id, application)

        return self.create_output(
            action="note_added",
            output_data={
                "app_id": app_id,
                "note": note,
                "added_at": now
            }
        )

    def _find_existing_application(
        self,
        user_id: str,
        job_id: str
    ) -> Optional[Dict]:
        """Find existing application for user and job"""
        applications = self.database.get_user_applications(user_id)
        for app in applications:
            if app.get("job_id") == job_id:
                return app
        return None

    def _calculate_days_since(self, date_str: Optional[str]) -> Optional[int]:
        """Calculate days since a date"""
        if not date_str:
            return None

        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
            return (now - date).days
        except (ValueError, TypeError):
            return None
