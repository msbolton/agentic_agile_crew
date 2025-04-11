"""
Unit tests for the RevisionCycle module
"""

import pytest
from unittest.mock import MagicMock, patch
from src.human_loop.feedback.cycle import RevisionCycle
from src.human_loop.feedback.memory import FeedbackMemory
from src.human_loop.feedback.limiter import CycleLimiter

class TestRevisionCycle:
    """
    Test cases for the RevisionCycle class
    """
    
    @pytest.fixture
    def mock_memory(self):
        """Create a mock FeedbackMemory"""
        memory = MagicMock(spec=FeedbackMemory)
        memory.get_revision_context.return_value = {
            "revision_count": 1,
            "previous_content": "Previous content",
            "previous_feedback": [
                {"version": 1, "feedback": "Previous feedback", "status": "rejected"}
            ]
        }
        return memory
    
    @pytest.fixture
    def mock_limiter(self):
        """Create a mock CycleLimiter"""
        limiter = MagicMock(spec=CycleLimiter)
        limiter.track_cycle.return_value = {
            "cycle_count": 1,
            "max_cycles": 5,
            "limit_reached": False,
            "auto_approve": False
        }
        return limiter
    
    @pytest.fixture
    def revision_cycle(self, mock_memory, mock_limiter):
        """Create a RevisionCycle with mock dependencies"""
        return RevisionCycle(feedback_memory=mock_memory, cycle_limiter=mock_limiter)
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock Agent"""
        agent = MagicMock()
        agent.name = "test_agent"
        return agent
    
    @pytest.fixture
    def mock_task(self):
        """Create a mock Task"""
        task = MagicMock()
        task.description = "Original task description"
        return task
    
    def test_initialization(self, mock_memory, mock_limiter):
        """Test initializing a revision cycle"""
        cycle = RevisionCycle(feedback_memory=mock_memory, cycle_limiter=mock_limiter)
        
        assert cycle.feedback_memory is mock_memory
        assert cycle.cycle_limiter is mock_limiter
        assert cycle.in_progress_revisions == {}
    
    def test_create_revision_task_description(self, revision_cycle):
        """Test creating revision task description"""
        original_description = "Original task description"
        formatted_feedback = "# Feedback\n- CHANGE: Improve section X"
        cycle_status = {"cycle_count": 2, "max_cycles": 5, "limit_reached": False}
        revision_context = {
            "revision_count": 1,
            "previous_feedback": [
                {"version": 1, "feedback": "Previous feedback", "status": "rejected"}
            ]
        }
        
        description = revision_cycle._create_revision_task_description(
            original_description, formatted_feedback, cycle_status, revision_context
        )
        
        # Check that all components are included
        assert original_description in description
        assert formatted_feedback in description
        assert "## REVISION REQUIRED" in description
        assert f"This is revision cycle {cycle_status['cycle_count']}" in description
        assert "Previous Revision History" in description
        assert "## Revision Instructions" in description
        
        # Check for guidance
        assert "Carefully review the feedback" in description
        assert "Return the complete revised content" in description
        
        # Should not have final revision note
        assert "final revision cycle" not in description
    
    def test_create_revision_task_description_limit_reached(self, revision_cycle):
        """Test creating revision task description when limit is reached"""
        original_description = "Original task description"
        formatted_feedback = "# Feedback\n- CHANGE: Improve section X"
        cycle_status = {"cycle_count": 5, "max_cycles": 5, "limit_reached": True}
        revision_context = {"revision_count": 0, "previous_feedback": []}
        
        description = revision_cycle._create_revision_task_description(
            original_description, formatted_feedback, cycle_status, revision_context
        )
        
        # Should have final revision note
        assert "final revision cycle" in description
    
    @patch('src.human_loop.feedback.cycle.FeedbackParser')
    def test_start_revision(self, mock_parser, revision_cycle, mock_agent, mock_task):
        """Test starting a revision cycle"""
        # Setup mocks
        mock_parser.parse.return_value = [MagicMock()]
        mock_parser.format_for_agent.return_value = "Formatted feedback"
        
        # Call the method
        result = revision_cycle.start_revision(
            agent=mock_agent,
            original_task=mock_task,
            stage_name="test_stage",
            artifact_type="test_artifact",
            feedback="Test feedback",
            original_content="Original content",
            callback=lambda x, y: None
        )
        
        # Check interactions
        revision_cycle.feedback_memory.get_revision_context.assert_called_once()
        revision_cycle.cycle_limiter.track_cycle.assert_called_once_with(
            "test_agent", "test_stage"
        )
        mock_parser.parse.assert_called_once_with("Test feedback")
        mock_parser.format_for_agent.assert_called_once()
        
        # Check result
        assert "revision_key" in result
        assert "task" in result
        assert "cycle_status" in result
        
        # Check that revision is stored
        assert len(revision_cycle.in_progress_revisions) == 1
        revision_key = result["revision_key"]
        assert revision_key in revision_cycle.in_progress_revisions
        
        # Check stored revision info
        revision_info = revision_cycle.in_progress_revisions[revision_key]
        assert revision_info["agent_id"] == "test_agent"
        assert revision_info["stage_name"] == "test_stage"
        assert revision_info["artifact_type"] == "test_artifact"
        assert revision_info["original_content"] == "Original content"
        assert revision_info["feedback"] == "Test feedback"
        assert "task" in revision_info
        assert "cycle_status" in revision_info
        assert "callback" in revision_info
    
    def test_complete_revision(self, revision_cycle, mock_agent, mock_task):
        """Test completing a revision cycle"""
        # Create a revision first
        callback = MagicMock()
        
        with patch('src.human_loop.feedback.parser.FeedbackParser'):
            result = revision_cycle.start_revision(
                agent=mock_agent,
                original_task=mock_task,
                stage_name="test_stage",
                artifact_type="test_artifact",
                feedback="Test feedback",
                original_content="Original content",
                callback=callback
            )
        
        revision_key = result["revision_key"]
        
        # Complete the revision
        completion_result = revision_cycle.complete_revision(
            revision_key=revision_key,
            revised_content="Revised content",
            status="completed"
        )
        
        # Check interactions
        revision_cycle.feedback_memory.record_revision.assert_called_once_with(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Revised content",
            feedback="Test feedback",
            status="completed"
        )
        
        # Check callback was called
        callback.assert_called_once_with("Revised content", "completed")
        
        # Check result
        assert completion_result["success"] is True
        assert completion_result["agent_id"] == "test_agent"
        assert completion_result["stage_name"] == "test_stage"
        assert completion_result["status"] == "completed"
        
        # Check revision is removed from in-progress
        assert revision_key not in revision_cycle.in_progress_revisions
    
    def test_complete_revision_invalid_key(self, revision_cycle):
        """Test completing a revision with invalid key"""
        result = revision_cycle.complete_revision(
            revision_key="nonexistent_key",
            revised_content="Revised content"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_active_revisions(self, revision_cycle, mock_agent, mock_task):
        """Test getting active revisions"""
        # Create some revisions
        with patch('src.human_loop.feedback.parser.FeedbackParser'):
            revision_cycle.start_revision(
                agent=mock_agent,
                original_task=mock_task,
                stage_name="stage1",
                artifact_type="artifact1",
                feedback="Feedback 1",
                original_content="Content 1"
            )
            
            revision_cycle.start_revision(
                agent=mock_agent,
                original_task=mock_task,
                stage_name="stage2",
                artifact_type="artifact2",
                feedback="Feedback 2",
                original_content="Content 2"
            )
        
        active_revisions = revision_cycle.get_active_revisions()
        
        assert len(active_revisions) == 2
        
        # Check revision details
        revisions_by_stage = {r["stage_name"]: r for r in active_revisions}
        
        assert "stage1" in revisions_by_stage
        assert "stage2" in revisions_by_stage
        
        assert revisions_by_stage["stage1"]["artifact_type"] == "artifact1"
        assert revisions_by_stage["stage2"]["artifact_type"] == "artifact2"
