"""Shared memory management for inter-agent communication"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import threading


class SharedMemory:
    """Thread-safe shared memory for agent communication"""

    DEFAULT_PATH = "/data/jobcopilot/memory.json"

    def __init__(self, memory_path: Optional[str] = None):
        self.memory_path = Path(memory_path or self.DEFAULT_PATH)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._cache: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load memory from disk"""
        with self._lock:
            if self.memory_path.exists():
                try:
                    with open(self.memory_path, 'r') as f:
                        self._cache = json.load(f)
                except (json.JSONDecodeError, IOError):
                    self._cache = self._default_memory()
            else:
                self._cache = self._default_memory()
                self._save()

    def _default_memory(self) -> Dict[str, Any]:
        """Create default memory structure"""
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "users": {},
            "jobs": {},
            "applications": {},
            "agent_state": {},
            "queue": [],
            "logs": []
        }

    def _save(self) -> None:
        """Save memory to disk"""
        with self._lock:
            self._cache["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.memory_path, 'w') as f:
                json.dump(self._cache, f, indent=2, default=str)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from memory"""
        with self._lock:
            keys = key.split('.')
            value = self._cache
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value

    def set(self, key: str, value: Any) -> None:
        """Set a value in memory"""
        with self._lock:
            keys = key.split('.')
            target = self._cache
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            self._save()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values in memory"""
        with self._lock:
            for key, value in updates.items():
                self.set(key, value)

    def delete(self, key: str) -> bool:
        """Delete a key from memory"""
        with self._lock:
            keys = key.split('.')
            target = self._cache
            for k in keys[:-1]:
                if k not in target:
                    return False
                target = target[k]
            if keys[-1] in target:
                del target[keys[-1]]
                self._save()
                return True
            return False

    def add_to_queue(self, item: Dict[str, Any]) -> None:
        """Add an item to the processing queue"""
        with self._lock:
            item["queued_at"] = datetime.now().isoformat()
            self._cache["queue"].append(item)
            self._save()

    def pop_from_queue(self) -> Optional[Dict[str, Any]]:
        """Pop an item from the processing queue"""
        with self._lock:
            if self._cache["queue"]:
                item = self._cache["queue"].pop(0)
                self._save()
                return item
            return None

    def log(self, agent: str, action: str, details: Optional[Dict] = None) -> None:
        """Add a log entry"""
        with self._lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "agent": agent,
                "action": action,
                "details": details or {}
            }
            self._cache["logs"].append(entry)
            # Keep last 1000 log entries
            if len(self._cache["logs"]) > 1000:
                self._cache["logs"] = self._cache["logs"][-1000:]
            self._save()

    def get_logs(self, agent: Optional[str] = None, limit: int = 100) -> list:
        """Get log entries, optionally filtered by agent"""
        with self._lock:
            logs = self._cache.get("logs", [])
            if agent:
                logs = [l for l in logs if l.get("agent") == agent]
            return logs[-limit:]

    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """Get state for a specific agent"""
        return self.get(f"agent_state.{agent_name}", {})

    def set_agent_state(self, agent_name: str, state: Dict[str, Any]) -> None:
        """Set state for a specific agent"""
        self.set(f"agent_state.{agent_name}", state)

    def get_all(self) -> Dict[str, Any]:
        """Get entire memory state"""
        with self._lock:
            return self._cache.copy()

    def clear(self) -> None:
        """Clear all memory"""
        with self._lock:
            self._cache = self._default_memory()
            self._save()
