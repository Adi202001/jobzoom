"""Agent registry for managing all available agents"""

from typing import Dict, Optional, Type, List
from .base_agent import BaseAgent
from ..utils.memory import SharedMemory
from ..utils.database import Database


class AgentRegistry:
    """Registry for all JobCopilot agents"""

    _agents: Dict[str, Type[BaseAgent]] = {}
    _instances: Dict[str, BaseAgent] = {}
    _memory: Optional[SharedMemory] = None
    _database: Optional[Database] = None

    @classmethod
    def initialize(
        cls,
        memory: Optional[SharedMemory] = None,
        database: Optional[Database] = None
    ) -> None:
        """Initialize the registry with shared resources"""
        cls._memory = memory or SharedMemory()
        cls._database = database or Database()

    @classmethod
    def register(cls, agent_class: Type[BaseAgent]) -> Type[BaseAgent]:
        """Decorator to register an agent class"""
        # Create a temporary instance to get the name
        temp_instance = object.__new__(agent_class)
        if hasattr(agent_class, 'name') and isinstance(agent_class.name, property):
            # Get the property value by calling the fget
            name = agent_class.name.fget(temp_instance)
        else:
            name = getattr(temp_instance, 'name', agent_class.__name__)
        cls._agents[name] = agent_class
        return agent_class

    @classmethod
    def get(cls, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent instance by name"""
        if agent_name not in cls._agents:
            return None

        # Return cached instance or create new one
        if agent_name not in cls._instances:
            cls._instances[agent_name] = cls._agents[agent_name](
                memory=cls._memory,
                database=cls._database
            )
        return cls._instances[agent_name]

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent names"""
        return list(cls._agents.keys())

    @classmethod
    def get_agent_info(cls) -> Dict[str, str]:
        """Get info about all registered agents"""
        info = {}
        for name, agent_class in cls._agents.items():
            agent = cls.get(name)
            info[name] = agent.description if agent else ""
        return info

    @classmethod
    def reset(cls) -> None:
        """Reset all agent instances"""
        cls._instances.clear()
