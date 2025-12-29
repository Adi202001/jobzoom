"""Base agent class for all JobCopilot agents"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import logging

from ..schemas import AgentOutput
from ..utils.memory import SharedMemory
from ..utils.database import Database


class BaseAgent(ABC):
    """Base class for all agents in the JobCopilot system"""

    def __init__(
        self,
        memory: Optional[SharedMemory] = None,
        database: Optional[Database] = None
    ):
        self.memory = memory or SharedMemory()
        self.database = database or Database()
        self.logger = logging.getLogger(self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name identifier"""
        pass

    @property
    def description(self) -> str:
        """Agent description"""
        return ""

    def get_state(self) -> Dict[str, Any]:
        """Get agent's current state from shared memory"""
        return self.memory.get_agent_state(self.name)

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set agent's state in shared memory"""
        self.memory.set_agent_state(self.name, state)

    def log_action(
        self,
        action: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None
    ) -> None:
        """Log an action to both memory and database"""
        self.memory.log(self.name, action, {
            "input": input_data,
            "output": output_data
        })
        self.database.log_agent_action(self.name, action, input_data, output_data)

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """
        Execute the agent's primary task

        Args:
            task: Task configuration and input data

        Returns:
            AgentOutput with results and next agent info
        """
        pass

    def create_output(
        self,
        action: str,
        output_data: Dict[str, Any],
        next_agent: Optional[str] = None,
        pass_data: Optional[Dict[str, Any]] = None,
        save_to_memory: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """Helper to create standardized agent output"""
        output = AgentOutput(
            agent=self.name,
            action=action,
            output_data=output_data,
            next_agent=next_agent,
            pass_data=pass_data,
            save_to_memory=save_to_memory
        )

        # Save to memory if requested
        if save_to_memory:
            self.memory.update(save_to_memory)

        # Log the action
        self.log_action(action, output_data=output_data)

        return output

    def validate_input(self, task: Dict[str, Any], required_fields: list) -> bool:
        """Validate that required fields are present in task"""
        missing = [f for f in required_fields if f not in task]
        if missing:
            self.logger.error(f"Missing required fields: {missing}")
            return False
        return True

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from database"""
        return self.database.get_user(user_id)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job from database"""
        return self.database.get_job(job_id)

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get application from database"""
        return self.database.get_application(app_id)
