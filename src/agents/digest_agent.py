"""Digest Agent - Creates daily summaries"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput, ApplicationStatus


@AgentRegistry.register
class DigestAgent(BaseAgent):
    """Agent responsible for creating daily summaries and reports"""

    @property
    def name(self) -> str:
        return "DIGEST_AGENT"

    @property
    def description(self) -> str:
        return "Creates daily summaries and progress reports"

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute digest tasks"""
        action = task.get("action", "")

        if action == "generate_digest":
            return self._generate_digest(task)
        elif action == "weekly_summary":
            return self._weekly_summary(task)
        elif action == "pipeline_report":
            return self._pipeline_report(task)
        elif action == "activity_summary":
            return self._activity_summary(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _generate_digest(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate a daily digest for the user"""
        user_id = task.get("user_id")
        new_applications = task.get("new_applications", [])

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

        # Gather data for digest
        all_apps = self.database.get_user_applications(user_id)
        stats = self.database.get_application_stats(user_id)

        # Get recent activity
        recent_activity = self._get_recent_activity(all_apps, days=1)

        # Get status updates
        status_updates = self._get_status_updates(all_apps, days=1)

        # Get upcoming follow-ups
        follow_ups = self._get_follow_ups(all_apps)

        # Generate digest text
        digest_text = self._format_digest(
            user.get("personal", {}).get("name", ""),
            stats,
            recent_activity,
            status_updates,
            follow_ups,
            new_applications
        )

        return self.create_output(
            action="digest_generated",
            output_data={
                "user_id": user_id,
                "date": datetime.now().isoformat(),
                "digest": digest_text,
                "stats": stats,
                "recent_activity_count": len(recent_activity),
                "status_updates_count": len(status_updates),
                "follow_ups_count": len(follow_ups)
            }
        )

    def _weekly_summary(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate a weekly summary"""
        user_id = task.get("user_id")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        all_apps = self.database.get_user_applications(user_id)
        stats = self.database.get_application_stats(user_id)

        # Get weekly metrics
        weekly_activity = self._get_recent_activity(all_apps, days=7)
        weekly_updates = self._get_status_updates(all_apps, days=7)

        # Calculate trends
        applications_this_week = len([
            a for a in all_apps
            if self._is_within_days(a.get("created_at"), 7)
        ])

        interviews_this_week = len([
            a for a in weekly_updates
            if a.get("new_status") == ApplicationStatus.INTERVIEW.value
        ])

        # Response rate
        submitted = stats.get(ApplicationStatus.SUBMITTED.value, 0)
        responses = (
            stats.get(ApplicationStatus.INTERVIEW.value, 0) +
            stats.get(ApplicationStatus.OFFER.value, 0) +
            stats.get(ApplicationStatus.REJECTED.value, 0)
        )
        response_rate = (responses / submitted * 100) if submitted > 0 else 0

        summary = {
            "week_ending": datetime.now().isoformat(),
            "applications_submitted": applications_this_week,
            "interviews_scheduled": interviews_this_week,
            "response_rate": round(response_rate, 1),
            "total_active": len([
                a for a in all_apps
                if a.get("status") not in [
                    ApplicationStatus.REJECTED.value,
                    ApplicationStatus.OFFER.value
                ]
            ]),
            "status_breakdown": stats,
            "highlights": self._generate_weekly_highlights(
                applications_this_week,
                interviews_this_week,
                response_rate
            )
        }

        return self.create_output(
            action="weekly_summary_generated",
            output_data={
                "user_id": user_id,
                "summary": summary
            }
        )

    def _pipeline_report(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate a pipeline status report"""
        user_id = task.get("user_id")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        all_apps = self.database.get_user_applications(user_id)

        # Group by status
        pipeline = defaultdict(list)
        for app in all_apps:
            status = app.get("status", "unknown")
            job = self.database.get_job(app.get("job_id", ""))
            pipeline[status].append({
                "app_id": app.get("app_id"),
                "job_title": job.get("title", "") if job else "",
                "company": job.get("company", "") if job else "",
                "match_score": app.get("match_score", 0),
                "days_in_status": self._calculate_days_in_status(app)
            })

        # Calculate averages
        stage_averages = {}
        for status, apps in pipeline.items():
            if apps:
                avg_days = sum(
                    a.get("days_in_status", 0) or 0 for a in apps
                ) / len(apps)
                stage_averages[status] = round(avg_days, 1)

        return self.create_output(
            action="pipeline_report_generated",
            output_data={
                "user_id": user_id,
                "pipeline": dict(pipeline),
                "stage_counts": {s: len(apps) for s, apps in pipeline.items()},
                "stage_averages_days": stage_averages,
                "total_applications": len(all_apps)
            }
        )

    def _activity_summary(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate an activity summary"""
        user_id = task.get("user_id")
        days = task.get("days", 7)

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        # Get agent logs
        logs = self.database.get_agent_logs(limit=500)
        cutoff = datetime.now() - timedelta(days=days)

        # Filter recent logs
        recent_logs = []
        for log in logs:
            try:
                log_time = datetime.fromisoformat(
                    log.get("timestamp", "").replace('Z', '+00:00')
                )
                if log_time > cutoff:
                    recent_logs.append(log)
            except (ValueError, TypeError):
                continue

        # Count by agent
        agent_counts = defaultdict(int)
        action_counts = defaultdict(int)
        for log in recent_logs:
            agent_counts[log.get("agent", "unknown")] += 1
            action_counts[log.get("action", "unknown")] += 1

        return self.create_output(
            action="activity_summary_generated",
            output_data={
                "user_id": user_id,
                "period_days": days,
                "total_actions": len(recent_logs),
                "by_agent": dict(agent_counts),
                "by_action": dict(action_counts),
                "most_active_agent": max(agent_counts, key=agent_counts.get) if agent_counts else None
            }
        )

    def _get_recent_activity(
        self,
        applications: List[Dict],
        days: int
    ) -> List[Dict]:
        """Get recent application activity"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []

        for app in applications:
            created = app.get("created_at")
            if created and self._is_after(created, cutoff):
                job = self.database.get_job(app.get("job_id", ""))
                recent.append({
                    "app_id": app.get("app_id"),
                    "job_title": job.get("title", "") if job else "",
                    "company": job.get("company", "") if job else "",
                    "status": app.get("status"),
                    "created_at": created
                })

        return recent

    def _get_status_updates(
        self,
        applications: List[Dict],
        days: int
    ) -> List[Dict]:
        """Get recent status updates"""
        cutoff = datetime.now() - timedelta(days=days)
        updates = []

        for app in applications:
            timeline = app.get("timeline", [])
            for event in timeline:
                if self._is_after(event.get("date"), cutoff):
                    job = self.database.get_job(app.get("job_id", ""))
                    updates.append({
                        "app_id": app.get("app_id"),
                        "job_title": job.get("title", "") if job else "",
                        "company": job.get("company", "") if job else "",
                        "new_status": event.get("status"),
                        "date": event.get("date"),
                        "note": event.get("note", "")
                    })

        return updates

    def _get_follow_ups(self, applications: List[Dict]) -> List[Dict]:
        """Get applications needing follow-up"""
        follow_ups = []

        for app in applications:
            status = app.get("status")
            submitted_at = app.get("submitted_at")

            # Check if follow-up needed (e.g., 7 days after submission with no response)
            if status == ApplicationStatus.SUBMITTED.value and submitted_at:
                days = self._calculate_days_since(submitted_at)
                if days and days >= 7:
                    job = self.database.get_job(app.get("job_id", ""))
                    follow_ups.append({
                        "app_id": app.get("app_id"),
                        "job_title": job.get("title", "") if job else "",
                        "company": job.get("company", "") if job else "",
                        "days_since_submission": days,
                        "suggested_action": "Send follow-up email"
                    })

        return follow_ups

    def _format_digest(
        self,
        name: str,
        stats: Dict,
        recent_activity: List,
        status_updates: List,
        follow_ups: List,
        new_applications: List
    ) -> str:
        """Format digest into readable text"""
        lines = []

        lines.append(f"# Daily Digest for {name or 'User'}")
        lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        lines.append("")

        # Overview
        lines.append("## Overview")
        total = sum(stats.values())
        lines.append(f"- Total Applications: {total}")
        for status, count in stats.items():
            lines.append(f"  - {status.replace('_', ' ').title()}: {count}")
        lines.append("")

        # Today's Activity
        if recent_activity:
            lines.append("## Today's Activity")
            for item in recent_activity[:5]:
                lines.append(f"- {item['job_title']} at {item['company']} ({item['status']})")
            lines.append("")

        # Status Updates
        if status_updates:
            lines.append("## Status Updates")
            for update in status_updates[:5]:
                lines.append(
                    f"- {update['job_title']} at {update['company']}: "
                    f"Now {update['new_status'].replace('_', ' ')}"
                )
            lines.append("")

        # New Applications
        if new_applications:
            lines.append("## New Applications Created")
            lines.append(f"Created {len(new_applications)} new applications today")
            lines.append("")

        # Follow-ups Needed
        if follow_ups:
            lines.append("## Action Items - Follow-ups Needed")
            for item in follow_ups[:5]:
                lines.append(
                    f"- {item['job_title']} at {item['company']} "
                    f"({item['days_since_submission']} days ago)"
                )
            lines.append("")

        # Tips
        lines.append("## Tips")
        if not recent_activity:
            lines.append("- Consider applying to more jobs today")
        if follow_ups:
            lines.append("- Send follow-up emails to pending applications")
        if stats.get(ApplicationStatus.INTERVIEW.value, 0) > 0:
            lines.append("- Prepare for upcoming interviews")

        return "\n".join(lines)

    def _generate_weekly_highlights(
        self,
        applications: int,
        interviews: int,
        response_rate: float
    ) -> List[str]:
        """Generate weekly highlights"""
        highlights = []

        if applications > 0:
            highlights.append(f"Submitted {applications} new applications")

        if interviews > 0:
            highlights.append(f"Scheduled {interviews} interviews")

        if response_rate > 0:
            if response_rate >= 30:
                highlights.append(f"Great response rate of {response_rate}%!")
            elif response_rate >= 15:
                highlights.append(f"Solid response rate of {response_rate}%")
            else:
                highlights.append(
                    f"Response rate of {response_rate}% - "
                    f"consider refining your applications"
                )

        if not highlights:
            highlights.append("Keep up the momentum - apply to more positions!")

        return highlights

    def _calculate_days_in_status(self, app: Dict) -> Optional[int]:
        """Calculate days in current status"""
        timeline = app.get("timeline", [])
        if not timeline:
            return None

        # Get most recent status change
        last_event = timeline[-1]
        return self._calculate_days_since(last_event.get("date"))

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

    def _is_within_days(self, date_str: Optional[str], days: int) -> bool:
        """Check if date is within N days"""
        result = self._calculate_days_since(date_str)
        return result is not None and result <= days

    def _is_after(self, date_str: Optional[str], cutoff: datetime) -> bool:
        """Check if date is after cutoff"""
        if not date_str:
            return False

        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if date.tzinfo:
                cutoff = cutoff.replace(tzinfo=date.tzinfo)
            return date > cutoff
        except (ValueError, TypeError):
            return False
