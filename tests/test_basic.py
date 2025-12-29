"""Basic tests for JobCopilot"""

import sys
import os
import tempfile
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.memory import SharedMemory
from src.utils.database import Database
from src.schemas import UserProfile, Job, Application, AgentOutput


class TestSharedMemory:
    """Tests for SharedMemory"""

    def test_memory_init(self):
        """Test memory initialization"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            memory = SharedMemory(f.name)
            assert memory.get("metadata") is not None
            assert memory.get("metadata.version") == "1.0"

    def test_memory_set_get(self):
        """Test setting and getting values"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            memory = SharedMemory(f.name)
            memory.set("test.key", "value")
            assert memory.get("test.key") == "value"

    def test_memory_nested_keys(self):
        """Test nested key access"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            memory = SharedMemory(f.name)
            memory.set("level1.level2.level3", {"data": "test"})
            assert memory.get("level1.level2.level3.data") == "test"

    def test_memory_queue(self):
        """Test queue operations"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            memory = SharedMemory(f.name)
            memory.add_to_queue({"task": "test1"})
            memory.add_to_queue({"task": "test2"})

            item = memory.pop_from_queue()
            assert item["task"] == "test1"

            item = memory.pop_from_queue()
            assert item["task"] == "test2"


class TestDatabase:
    """Tests for Database"""

    def test_db_init(self):
        """Test database initialization"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db = Database(f.name)
            assert db is not None

    def test_user_crud(self):
        """Test user CRUD operations"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db = Database(f.name)

            # Create
            user_data = {"name": "Test User", "email": "test@example.com"}
            db.save_user("user1", user_data)

            # Read
            user = db.get_user("user1")
            assert user["name"] == "Test User"

            # Update
            user_data["name"] = "Updated User"
            db.save_user("user1", user_data)
            user = db.get_user("user1")
            assert user["name"] == "Updated User"

    def test_job_crud(self):
        """Test job CRUD operations"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db = Database(f.name)

            job_data = {
                "company": "Test Corp",
                "title": "Engineer",
                "location": "Remote",
                "status": "new"
            }
            db.save_job("job1", job_data)

            job = db.get_job("job1")
            assert job["company"] == "Test Corp"


class TestSchemas:
    """Tests for data schemas"""

    def test_user_profile(self):
        """Test UserProfile schema"""
        profile = UserProfile(user_id="test123")
        assert profile.user_id == "test123"
        assert profile.personal.name == ""

        profile_dict = profile.to_dict()
        assert profile_dict["user_id"] == "test123"

    def test_job_id_generation(self):
        """Test job ID generation"""
        job_id = Job.generate_job_id("Company", "Title", "Location")
        assert len(job_id) == 16
        assert isinstance(job_id, str)

        # Same inputs should produce same ID
        job_id2 = Job.generate_job_id("Company", "Title", "Location")
        assert job_id == job_id2

        # Different inputs should produce different ID
        job_id3 = Job.generate_job_id("Other", "Title", "Location")
        assert job_id != job_id3

    def test_agent_output(self):
        """Test AgentOutput schema"""
        output = AgentOutput(
            agent="TEST_AGENT",
            action="test_action",
            output_data={"result": "success"},
            next_agent="NEXT_AGENT",
            pass_data={"key": "value"}
        )

        assert output.agent == "TEST_AGENT"
        output_dict = output.to_dict()
        assert output_dict["agent"] == "TEST_AGENT"
        assert output_dict["next_agent"] == "NEXT_AGENT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
