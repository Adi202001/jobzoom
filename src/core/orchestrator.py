"""Orchestrator for coordinating agent workflows"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from .registry import AgentRegistry
from ..schemas import AgentOutput
from ..utils.memory import SharedMemory
from ..utils.database import Database


class Orchestrator:
    """Coordinates agent execution and workflow management"""

    def __init__(
        self,
        memory: Optional[SharedMemory] = None,
        database: Optional[Database] = None
    ):
        self.memory = memory or SharedMemory()
        self.database = database or Database()
        self.logger = logging.getLogger("Orchestrator")

        # Initialize registry with shared resources
        AgentRegistry.initialize(self.memory, self.database)

    def execute_agent(
        self,
        agent_name: str,
        task: Dict[str, Any]
    ) -> AgentOutput:
        """Execute a single agent with the given task"""
        agent = AgentRegistry.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")

        self.logger.info(f"Executing {agent_name} with task: {task.get('action', 'unknown')}")

        # Execute the agent
        result = agent.execute(task)

        # Log the execution
        self.memory.log("Orchestrator", "agent_execution", {
            "agent": agent_name,
            "action": result.action,
            "success": True
        })

        return result

    def execute_workflow(
        self,
        start_agent: str,
        initial_task: Dict[str, Any],
        max_steps: int = 10
    ) -> List[AgentOutput]:
        """Execute a workflow starting from an agent and following next_agent chains"""
        results = []
        current_agent = start_agent
        current_task = initial_task
        step = 0

        while current_agent and step < max_steps:
            try:
                result = self.execute_agent(current_agent, current_task)
                results.append(result)

                # Prepare for next agent
                if result.next_agent:
                    current_agent = result.next_agent
                    current_task = result.pass_data or {}
                else:
                    break

                step += 1

            except Exception as e:
                self.logger.error(f"Workflow error at {current_agent}: {e}")
                break

        return results

    def run_pipeline(
        self,
        user_id: str,
        pipeline_type: str = "full_application"
    ) -> List[AgentOutput]:
        """Run a predefined pipeline"""
        pipelines = {
            "full_application": [
                ("SCRAPER_AGENT", {"action": "scrape_new_jobs"}),
                ("MATCHER_AGENT", {"action": "match_jobs", "user_id": user_id}),
                ("RESUME_TAILOR_AGENT", {"action": "tailor_resumes", "user_id": user_id}),
                ("COVER_LETTER_AGENT", {"action": "generate_letters", "user_id": user_id}),
                ("TRACKER_AGENT", {"action": "update_tracking", "user_id": user_id}),
            ],
            "daily_digest": [
                ("TRACKER_AGENT", {"action": "refresh_status", "user_id": user_id}),
                ("DIGEST_AGENT", {"action": "generate_digest", "user_id": user_id}),
            ],
            "profile_setup": [
                ("PROFILE_AGENT", {"action": "create_profile", "user_id": user_id}),
                ("RESUME_PARSER_AGENT", {"action": "parse_resume", "user_id": user_id}),
            ]
        }

        if pipeline_type not in pipelines:
            raise ValueError(f"Unknown pipeline: {pipeline_type}")

        results = []
        for agent_name, task in pipelines[pipeline_type]:
            task["user_id"] = user_id
            result = self.execute_agent(agent_name, task)
            results.append(result)

        return results

    def queue_task(
        self,
        agent_name: str,
        task: Dict[str, Any],
        priority: int = 5
    ) -> None:
        """Queue a task for later execution"""
        self.memory.add_to_queue({
            "agent": agent_name,
            "task": task,
            "priority": priority,
            "status": "pending"
        })

    def process_queue(self, max_tasks: int = 10) -> List[AgentOutput]:
        """Process tasks from the queue"""
        results = []
        for _ in range(max_tasks):
            item = self.memory.pop_from_queue()
            if not item:
                break

            try:
                result = self.execute_agent(item["agent"], item["task"])
                results.append(result)
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")

        return results

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "registered_agents": AgentRegistry.list_agents(),
            "queue_size": len(self.memory.get("queue", [])),
            "memory_state": self.memory.get_all().get("metadata", {}),
            "recent_logs": self.memory.get_logs(limit=10)
        }
