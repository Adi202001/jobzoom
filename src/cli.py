#!/usr/bin/env python3
"""JobCopilot CLI - Command-line interface for the job application automation system"""

import argparse
import json
import sys
from typing import Optional

from .core.orchestrator import Orchestrator
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


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser"""
    parser = argparse.ArgumentParser(
        prog="jobcopilot",
        description="JobCopilot - Multi-Agent Job Application Automation System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Profile commands
    profile_parser = subparsers.add_parser("profile", help="Manage user profile")
    profile_subparsers = profile_parser.add_subparsers(dest="profile_action")

    profile_create = profile_subparsers.add_parser("create", help="Create a new profile")
    profile_create.add_argument("--name", required=True, help="Full name")
    profile_create.add_argument("--email", required=True, help="Email address")
    profile_create.add_argument("--phone", help="Phone number")
    profile_create.add_argument("--location", help="Current location")
    profile_create.add_argument("--linkedin", help="LinkedIn URL")
    profile_create.add_argument("--resume", help="Path to resume file")

    profile_show = profile_subparsers.add_parser("show", help="Show profile")
    profile_show.add_argument("--user-id", required=True, help="User ID")

    profile_update = profile_subparsers.add_parser("update", help="Update profile")
    profile_update.add_argument("--user-id", required=True, help="User ID")
    profile_update.add_argument("--name", help="Full name")
    profile_update.add_argument("--email", help="Email address")
    profile_update.add_argument("--phone", help="Phone number")
    profile_update.add_argument("--location", help="Current location")

    # Job preferences commands
    prefs_parser = subparsers.add_parser("preferences", help="Manage job preferences")
    prefs_subparsers = prefs_parser.add_subparsers(dest="prefs_action")

    prefs_set = prefs_subparsers.add_parser("set", help="Set job preferences")
    prefs_set.add_argument("--user-id", required=True, help="User ID")
    prefs_set.add_argument("--titles", nargs="+", help="Target job titles")
    prefs_set.add_argument("--locations", nargs="+", help="Preferred locations")
    prefs_set.add_argument("--remote", choices=["remote_only", "hybrid_ok", "onsite_ok", "any"])
    prefs_set.add_argument("--salary-min", type=int, help="Minimum salary")
    prefs_set.add_argument("--salary-max", type=int, help="Maximum salary")

    # Scraper commands
    scrape_parser = subparsers.add_parser("scrape", help="Scrape jobs")
    scrape_subparsers = scrape_parser.add_subparsers(dest="scrape_action")

    scrape_url = scrape_subparsers.add_parser("url", help="Scrape from URL")
    scrape_url.add_argument("--url", required=True, help="Career page URL")
    scrape_url.add_argument("--user-id", help="User ID for auto-matching")

    scrape_company = scrape_subparsers.add_parser("company", help="Scrape company careers")
    scrape_company.add_argument("--company", required=True, help="Company name")
    scrape_company.add_argument("--user-id", help="User ID for auto-matching")

    # Match commands
    match_parser = subparsers.add_parser("match", help="Match jobs to user")
    match_parser.add_argument("--user-id", required=True, help="User ID")
    match_parser.add_argument("--job-id", help="Specific job ID to match")

    # Apply commands
    apply_parser = subparsers.add_parser("apply", help="Prepare application")
    apply_parser.add_argument("--user-id", required=True, help="User ID")
    apply_parser.add_argument("--job-id", required=True, help="Job ID")

    # Status commands
    status_parser = subparsers.add_parser("status", help="Check application status")
    status_subparsers = status_parser.add_subparsers(dest="status_action")

    status_list = status_subparsers.add_parser("list", help="List all applications")
    status_list.add_argument("--user-id", required=True, help="User ID")
    status_list.add_argument("--filter", help="Filter by status")

    status_update = status_subparsers.add_parser("update", help="Update application status")
    status_update.add_argument("--app-id", required=True, help="Application ID")
    status_update.add_argument("--status", required=True, help="New status")
    status_update.add_argument("--note", help="Optional note")

    # Digest commands
    digest_parser = subparsers.add_parser("digest", help="Generate digest/summary")
    digest_parser.add_argument("--user-id", required=True, help="User ID")
    digest_parser.add_argument("--type", choices=["daily", "weekly", "pipeline"],
                               default="daily", help="Digest type")

    # Pipeline commands
    pipeline_parser = subparsers.add_parser("pipeline", help="Run automated pipeline")
    pipeline_parser.add_argument("--user-id", required=True, help="User ID")
    pipeline_parser.add_argument("--type", choices=["full_application", "daily_digest", "profile_setup"],
                                 default="full_application", help="Pipeline type")

    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Run specific agent")
    agent_parser.add_argument("--name", required=True, help="Agent name")
    agent_parser.add_argument("--task", required=True, help="Task JSON")

    # System commands
    system_parser = subparsers.add_parser("system", help="System commands")
    system_subparsers = system_parser.add_subparsers(dest="system_action")

    system_status = system_subparsers.add_parser("status", help="Show system status")
    system_agents = system_subparsers.add_parser("agents", help="List registered agents")
    system_reset = system_subparsers.add_parser("reset", help="Reset system state")

    return parser


def run_command(args: argparse.Namespace) -> None:
    """Run the specified command"""
    orchestrator = Orchestrator()

    if args.command == "profile":
        handle_profile_command(orchestrator, args)
    elif args.command == "preferences":
        handle_preferences_command(orchestrator, args)
    elif args.command == "scrape":
        handle_scrape_command(orchestrator, args)
    elif args.command == "match":
        handle_match_command(orchestrator, args)
    elif args.command == "apply":
        handle_apply_command(orchestrator, args)
    elif args.command == "status":
        handle_status_command(orchestrator, args)
    elif args.command == "digest":
        handle_digest_command(orchestrator, args)
    elif args.command == "pipeline":
        handle_pipeline_command(orchestrator, args)
    elif args.command == "agent":
        handle_agent_command(orchestrator, args)
    elif args.command == "system":
        handle_system_command(orchestrator, args)
    else:
        print("Use --help to see available commands")


def handle_profile_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle profile commands"""
    if args.profile_action == "create":
        result = orchestrator.execute_agent("PROFILE_AGENT", {
            "action": "create_profile",
            "personal": {
                "name": args.name,
                "email": args.email,
                "phone": args.phone or "",
                "location": args.location or "",
                "linkedin": args.linkedin or ""
            },
            "resume_path": args.resume
        })
        print(f"Profile created: {result.output_data.get('user_id')}")
        print(json.dumps(result.output_data, indent=2))

    elif args.profile_action == "show":
        result = orchestrator.execute_agent("PROFILE_AGENT", {
            "action": "get_profile",
            "user_id": args.user_id
        })
        print(json.dumps(result.output_data, indent=2))

    elif args.profile_action == "update":
        personal = {}
        if args.name:
            personal["name"] = args.name
        if args.email:
            personal["email"] = args.email
        if args.phone:
            personal["phone"] = args.phone
        if args.location:
            personal["location"] = args.location

        result = orchestrator.execute_agent("PROFILE_AGENT", {
            "action": "update_profile",
            "user_id": args.user_id,
            "personal": personal
        })
        print(json.dumps(result.output_data, indent=2))


def handle_preferences_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle preferences commands"""
    if args.prefs_action == "set":
        preferences = {}
        if args.titles:
            preferences["target_titles"] = args.titles
        if args.locations:
            preferences["locations"] = args.locations
        if args.remote:
            preferences["remote_preference"] = args.remote
        if args.salary_min:
            preferences["salary_min"] = args.salary_min
        if args.salary_max:
            preferences["salary_max"] = args.salary_max

        result = orchestrator.execute_agent("PROFILE_AGENT", {
            "action": "update_preferences",
            "user_id": args.user_id,
            "preferences": preferences
        })
        print(json.dumps(result.output_data, indent=2))


def handle_scrape_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle scrape commands"""
    if args.scrape_action == "url":
        result = orchestrator.execute_agent("SCRAPER_AGENT", {
            "action": "scrape_url",
            "url": args.url,
            "user_id": args.user_id,
            "auto_match": bool(args.user_id)
        })
        print(f"Scraped {result.output_data.get('jobs_found', 0)} jobs")
        print(json.dumps(result.output_data, indent=2))

    elif args.scrape_action == "company":
        result = orchestrator.execute_agent("SCRAPER_AGENT", {
            "action": "scrape_company",
            "company": args.company,
            "user_id": args.user_id,
            "auto_match": bool(args.user_id)
        })
        print(json.dumps(result.output_data, indent=2))


def handle_match_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle match commands"""
    if args.job_id:
        result = orchestrator.execute_agent("MATCHER_AGENT", {
            "action": "match_job",
            "user_id": args.user_id,
            "job_id": args.job_id
        })
    else:
        result = orchestrator.execute_agent("MATCHER_AGENT", {
            "action": "match_jobs",
            "user_id": args.user_id
        })
    print(json.dumps(result.output_data, indent=2))


def handle_apply_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle apply commands - runs the application preparation workflow"""
    results = orchestrator.execute_workflow(
        "RESUME_TAILOR_AGENT",
        {
            "action": "tailor_resume",
            "user_id": args.user_id,
            "job_id": args.job_id
        }
    )

    print(f"Application preparation completed ({len(results)} steps)")
    for result in results:
        print(f"- {result.agent}: {result.action}")


def handle_status_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle status commands"""
    if args.status_action == "list":
        result = orchestrator.execute_agent("TRACKER_AGENT", {
            "action": "get_all_applications",
            "user_id": args.user_id,
            "status": args.filter
        })
        print(json.dumps(result.output_data, indent=2))

    elif args.status_action == "update":
        result = orchestrator.execute_agent("TRACKER_AGENT", {
            "action": "update_status",
            "app_id": args.app_id,
            "status": args.status,
            "note": args.note
        })
        print(json.dumps(result.output_data, indent=2))


def handle_digest_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle digest commands"""
    action_map = {
        "daily": "generate_digest",
        "weekly": "weekly_summary",
        "pipeline": "pipeline_report"
    }

    result = orchestrator.execute_agent("DIGEST_AGENT", {
        "action": action_map[args.type],
        "user_id": args.user_id
    })

    if args.type == "daily":
        print(result.output_data.get("digest", ""))
    else:
        print(json.dumps(result.output_data, indent=2))


def handle_pipeline_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle pipeline commands"""
    results = orchestrator.run_pipeline(args.user_id, args.type)
    print(f"Pipeline '{args.type}' completed ({len(results)} steps)")
    for result in results:
        print(f"- {result.agent}: {result.action}")


def handle_agent_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle direct agent commands"""
    try:
        task = json.loads(args.task)
    except json.JSONDecodeError:
        print("Error: Invalid JSON task")
        return

    result = orchestrator.execute_agent(args.name, task)
    print(json.dumps(result.to_dict(), indent=2))


def handle_system_command(orchestrator: Orchestrator, args: argparse.Namespace) -> None:
    """Handle system commands"""
    if args.system_action == "status":
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.system_action == "agents":
        from .core.registry import AgentRegistry
        info = AgentRegistry.get_agent_info()
        print("Registered Agents:")
        for name, desc in info.items():
            print(f"  - {name}: {desc}")

    elif args.system_action == "reset":
        orchestrator.memory.clear()
        print("System state reset")


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        run_command(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
