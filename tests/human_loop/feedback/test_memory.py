"""
Unit tests for the FeedbackMemory module
"""

import pytest
import os
import json
import tempfile
import shutil
from datetime import datetime
from src.human_loop.feedback.memory import FeedbackMemory, RevisionHistory

class TestRevisionHistory:
    """
    Test cases for the RevisionHistory class
    """
    
    def test_revision_history_initialization(self):
        """Test initializing a revision history"""
        history = RevisionHistory("test_agent", "test_stage", "test_artifact")
        
        assert history.agent_id == "test_agent"
        assert history.stage_name == "test_stage"
        assert history.artifact_type == "test_artifact"
        assert history.revisions == []
    
    def test_add_revision(self):
        """Test adding revisions to history"""
        history = RevisionHistory("test_agent", "test_stage", "test_artifact")
        
        # Add first revision
        content1 = "Original content"
        version1 = history.add_revision(content1, "Needs improvement", "rejected")
        
        assert version1 == 1
        assert len(history.revisions) == 1
        assert history.revisions[0]["version"] == 1
        assert history.revisions[0]["content"] == content1
        assert history.revisions[0]["feedback"] == "Needs improvement"
        assert history.revisions[0]["status"] == "rejected"
        assert "timestamp" in history.revisions[0]
        
        # Add second revision
        content2 = "Improved content"
        version2 = history.add_revision(content2, "Looks good", "approved")
        
        assert version2 == 2
        assert len(history.revisions) == 2
        assert history.revisions[1]["content"] == content2
    
    def test_get_latest_revision(self):
        """Test getting the latest revision"""
        history = RevisionHistory("test_agent", "test_stage", "test_artifact")
        
        # Empty history
        assert history.get_latest_revision() is None
        
        # Add revisions
        history.add_revision("Content 1", "Feedback 1", "rejected")
        history.add_revision("Content 2", "Feedback 2", "approved")
        
        latest = history.get_latest_revision()
        assert latest["version"] == 2
        assert latest["content"] == "Content 2"
        assert latest["feedback"] == "Feedback 2"
        assert latest["status"] == "approved"
    
    def test_get_revision(self):
        """Test getting a specific revision"""
        history = RevisionHistory("test_agent", "test_stage", "test_artifact")
        
        # Add revisions
        history.add_revision("Content 1", "Feedback 1", "rejected")
        history.add_revision("Content 2", "Feedback 2", "rejected")
        history.add_revision("Content 3", "Feedback 3", "approved")
        
        # Get specific revisions
        rev1 = history.get_revision(1)
        rev2 = history.get_revision(2)
        rev3 = history.get_revision(3)
        
        assert rev1["content"] == "Content 1"
        assert rev2["content"] == "Content 2"
        assert rev3["content"] == "Content 3"
        
        # Invalid versions
        assert history.get_revision(0) is None
        assert history.get_revision(4) is None
    
    def test_to_dict(self):
        """Test converting revision history to dictionary"""
        history = RevisionHistory("test_agent", "test_stage", "test_artifact")
        history.add_revision("Content", "Feedback", "rejected")
        
        history_dict = history.to_dict()
        
        assert history_dict["agent_id"] == "test_agent"
        assert history_dict["stage_name"] == "test_stage"
        assert history_dict["artifact_type"] == "test_artifact"
        assert isinstance(history_dict["revisions"], list)
        assert len(history_dict["revisions"]) == 1
    
    def test_from_dict(self):
        """Test creating revision history from dictionary"""
        data = {
            "agent_id": "test_agent",
            "stage_name": "test_stage",
            "artifact_type": "test_artifact",
            "revisions": [
                {
                    "version": 1,
                    "content": "Content",
                    "feedback": "Feedback",
                    "status": "rejected",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        history = RevisionHistory.from_dict(data)
        
        assert history.agent_id == "test_agent"
        assert history.stage_name == "test_stage"
        assert history.artifact_type == "test_artifact"
        assert len(history.revisions) == 1
        assert history.revisions[0]["content"] == "Content"


class TestFeedbackMemory:
    """
    Test cases for the FeedbackMemory class
    """
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_dir):
        """Test initializing feedback memory"""
        memory = FeedbackMemory(storage_dir=temp_dir)
        
        assert memory.storage_dir == temp_dir
        assert memory._memory_file == os.path.join(temp_dir, "revision_history.json")
        assert isinstance(memory._histories, dict)
        assert len(memory._histories) == 0
        
        # Directory should be created
        assert os.path.exists(temp_dir)
    
    def test_get_key(self):
        """Test key generation for histories"""
        memory = FeedbackMemory(storage_dir=tempfile.mkdtemp())
        
        key = memory._get_key("agent1", "stage1")
        assert key == "agent1_stage1"
    
    def test_get_history_new(self, temp_dir):
        """Test getting a new history"""
        memory = FeedbackMemory(storage_dir=temp_dir)
        
        history = memory.get_history("agent1", "stage1")
        
        assert isinstance(history, RevisionHistory)
        assert history.agent_id == "agent1"
        assert history.stage_name == "stage1"
        assert history.artifact_type == "unknown"
        assert len(history.revisions) == 0
    
    def test_record_revision(self, temp_dir):
        """Test recording revisions"""
        memory = FeedbackMemory(storage_dir=temp_dir)
        
        # Record first revision
        version1 = memory.record_revision(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="document",
            content="Content 1",
            feedback="Feedback 1",
            status="rejected"
        )
        
        assert version1 == 1
        assert "agent1_stage1" in memory._histories
        
        # Record second revision
        version2 = memory.record_revision(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="document",
            content="Content 2",
            feedback="Feedback 2",
            status="approved"
        )
        
        assert version2 == 2
        
        # Check history
        history = memory.get_history("agent1", "stage1")
        assert len(history.revisions) == 2
        assert history.revisions[0]["content"] == "Content 1"
        assert history.revisions[1]["content"] == "Content 2"
    
    def test_get_revision_context_empty(self, temp_dir):
        """Test getting context with no history"""
        memory = FeedbackMemory(storage_dir=temp_dir)
        
        context = memory.get_revision_context("agent1", "stage1")
        
        assert isinstance(context, dict)
        assert context["revision_count"] == 0
        assert context["previous_feedback"] == []
        assert "previous_content" not in context
    
    def test_get_revision_context_with_history(self, temp_dir):
        """Test getting context with existing history"""
        memory = FeedbackMemory(storage_dir=temp_dir)
        
        # Add revisions
        memory.record_revision(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="document",
            content="Content 1",
            feedback="Feedback 1",
            status="rejected"
        )
        
        memory.record_revision(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="document",
            content="Content 2",
            feedback="Feedback 2",
            status="approved"
        )
        
        context = memory.get_revision_context("agent1", "stage1")
        
        assert context["revision_count"] == 2
        assert len(context["previous_feedback"]) == 2
        assert context["previous_content"] == "Content 2"  # Most recent content
        
        # Check feedback details
        feedback1 = context["previous_feedback"][0]
        feedback2 = context["previous_feedback"][1]
        
        assert feedback1["version"] == 1
        assert feedback1["feedback"] == "Feedback 1"
        assert feedback1["status"] == "rejected"
        
        assert feedback2["version"] == 2
        assert feedback2["feedback"] == "Feedback 2"
        assert feedback2["status"] == "approved"
    
    def test_save_and_load(self, temp_dir):
        """Test saving and loading histories"""
        # Create and save some revision history
        memory1 = FeedbackMemory(storage_dir=temp_dir)
        memory1.record_revision(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="document",
            content="Content",
            feedback="Feedback",
            status="approved"
        )
        
        # Memory file should exist
        assert os.path.exists(memory1._memory_file)
        
        # Create a new instance that should load the saved data
        memory2 = FeedbackMemory(storage_dir=temp_dir)
        
        # Check the loaded history
        history = memory2.get_history("agent1", "stage1")
        assert len(history.revisions) == 1
        assert history.revisions[0]["content"] == "Content"
        assert history.revisions[0]["feedback"] == "Feedback"
        assert history.revisions[0]["status"] == "approved"
