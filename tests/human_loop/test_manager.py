"""
Unit tests for the HumanReviewManager in src.human_loop.manager
"""

import os
import json
import tempfile
import shutil
from unittest import TestCase, mock
import pytest
from datetime import datetime

from src.human_loop.manager import HumanReviewManager, HumanReviewRequest


class TestHumanReviewRequest(TestCase):
    """Test cases for HumanReviewRequest class"""
    
    def test_init(self):
        """Test initialization with required parameters"""
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content"
        )
        
        # Verify instance variables
        self.assertEqual(request.agent_id, "test_agent")
        self.assertEqual(request.stage_name, "test_stage")
        self.assertEqual(request.artifact_type, "test_artifact")
        self.assertEqual(request.content, "Test content")
        self.assertEqual(request.status, "pending")
        self.assertEqual(request.feedback, "")
        self.assertEqual(request.context, {})
        self.assertIsNone(request.callback)
        
        # ID should be a string
        self.assertIsInstance(request.id, str)
        self.assertTrue(len(request.id) > 0)
        
        # Timestamp should be an ISO format string
        self.assertIsInstance(request.timestamp, str)
        
    def test_init_with_optional_params(self):
        """Test initialization with optional parameters"""
        context = {"key": "value"}
        callback = lambda a, b: None
        
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content",
            context=context,
            callback=callback
        )
        
        # Verify optional parameters
        self.assertEqual(request.context, context)
        self.assertEqual(request.callback, callback)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content",
            context={"test": "value"}
        )
        
        # Convert to dictionary
        request_dict = request.to_dict()
        
        # Verify dictionary keys and values
        self.assertEqual(request_dict["id"], request.id)
        self.assertEqual(request_dict["agent_id"], "test_agent")
        self.assertEqual(request_dict["stage_name"], "test_stage")
        self.assertEqual(request_dict["artifact_type"], "test_artifact")
        self.assertEqual(request_dict["content"], "Test content")
        self.assertEqual(request_dict["context"], {"test": "value"})
        self.assertEqual(request_dict["status"], "pending")
        self.assertEqual(request_dict["feedback"], "")
        self.assertEqual(request_dict["timestamp"], request.timestamp)
    
    def test_from_dict(self):
        """Test creating instance from dictionary"""
        data = {
            "id": "test-id-123",
            "agent_id": "test_agent",
            "stage_name": "test_stage",
            "artifact_type": "test_artifact",
            "content": "Test content",
            "context": {"test": "value"},
            "status": "approved",
            "feedback": "Good job!",
            "timestamp": "2023-01-01T12:00:00"
        }
        
        # Create from dictionary
        request = HumanReviewRequest.from_dict(data)
        
        # Verify instance variables
        self.assertEqual(request.id, "test-id-123")
        self.assertEqual(request.agent_id, "test_agent")
        self.assertEqual(request.stage_name, "test_stage")
        self.assertEqual(request.artifact_type, "test_artifact")
        self.assertEqual(request.content, "Test content")
        self.assertEqual(request.context, {"test": "value"})
        self.assertEqual(request.status, "approved")
        self.assertEqual(request.feedback, "Good job!")
        self.assertEqual(request.timestamp, "2023-01-01T12:00:00")
        self.assertIsNone(request.callback)


class TestHumanReviewManager(TestCase):
    """Test cases for HumanReviewManager class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = HumanReviewManager(storage_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test initialization creates directory and loads reviews"""
        # Verify directory was created
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # Verify empty lists are initialized
        self.assertEqual(len(self.manager.pending_reviews), 0)
        self.assertEqual(len(self.manager.completed_reviews), 0)
        self.assertEqual(len(self.manager.callbacks), 0)
    
    def test_load_reviews(self):
        """Test loading reviews from storage"""
        # Create test data
        pending_data = [
            {
                "id": "pending-1",
                "agent_id": "agent1",
                "stage_name": "stage1",
                "artifact_type": "type1",
                "content": "content1",
                "context": {},
                "status": "pending",
                "feedback": "",
                "timestamp": "2023-01-01T12:00:00"
            }
        ]
        
        completed_data = [
            {
                "id": "completed-1",
                "agent_id": "agent2",
                "stage_name": "stage2",
                "artifact_type": "type2",
                "content": "content2",
                "context": {},
                "status": "approved",
                "feedback": "Good",
                "timestamp": "2023-01-02T12:00:00",
                "completed_at": "2023-01-02T13:00:00"
            }
        ]
        
        # Write test data to files
        pending_path = os.path.join(self.temp_dir, "pending_reviews.json")
        completed_path = os.path.join(self.temp_dir, "completed_reviews.json")
        
        with open(pending_path, 'w') as f:
            json.dump(pending_data, f)
            
        with open(completed_path, 'w') as f:
            json.dump(completed_data, f)
        
        # Create a new manager to load the data
        manager = HumanReviewManager(storage_dir=self.temp_dir)
        
        # Verify pending reviews were loaded
        self.assertEqual(len(manager.pending_reviews), 1)
        self.assertEqual(manager.pending_reviews[0].id, "pending-1")
        
        # Verify completed reviews were loaded
        self.assertEqual(len(manager.completed_reviews), 1)
        self.assertEqual(manager.completed_reviews[0]["id"], "completed-1")
    
    def test_request_review(self):
        """Test requesting a review"""
        # Create a test request
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content",
            callback=lambda a, b: None
        )
        
        # Request review
        review_id = self.manager.request_review(request)
        
        # Verify the ID is returned
        self.assertEqual(review_id, request.id)
        
        # Verify request was added to pending reviews
        self.assertEqual(len(self.manager.pending_reviews), 1)
        self.assertEqual(self.manager.pending_reviews[0].id, request.id)
        
        # Verify callback was stored separately
        self.assertEqual(len(self.manager.callbacks), 1)
        self.assertIn(request.id, self.manager.callbacks)
        
        # Verify request was saved to file
        pending_path = os.path.join(self.temp_dir, "pending_reviews.json")
        self.assertTrue(os.path.exists(pending_path))
        
        # Verify file content
        with open(pending_path, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 1)
        self.assertEqual(saved_data[0]["id"], request.id)
        self.assertEqual(saved_data[0]["agent_id"], "test_agent")
    
    def test_get_pending_reviews(self):
        """Test getting pending reviews"""
        # Add test requests
        request1 = HumanReviewRequest(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="type1",
            content="content1"
        )
        
        request2 = HumanReviewRequest(
            agent_id="agent2",
            stage_name="stage2",
            artifact_type="type2",
            content="content2"
        )
        
        self.manager.pending_reviews.append(request1)
        self.manager.pending_reviews.append(request2)
        
        # Get pending reviews
        pending = self.manager.get_pending_reviews()
        
        # Verify result
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0].id, request1.id)
        self.assertEqual(pending[1].id, request2.id)
    
    def test_get_completed_reviews(self):
        """Test getting completed reviews"""
        # Add test completed reviews
        completed1 = {"id": "completed-1", "status": "approved"}
        completed2 = {"id": "completed-2", "status": "rejected"}
        
        self.manager.completed_reviews.append(completed1)
        self.manager.completed_reviews.append(completed2)
        
        # Get completed reviews
        completed = self.manager.get_completed_reviews()
        
        # Verify result
        self.assertEqual(len(completed), 2)
        self.assertEqual(completed[0]["id"], "completed-1")
        self.assertEqual(completed[1]["id"], "completed-2")
    
    def test_get_review_by_id(self):
        """Test getting a review by ID"""
        # Add test requests
        request1 = HumanReviewRequest(
            agent_id="agent1",
            stage_name="stage1",
            artifact_type="type1",
            content="content1"
        )
        
        request2 = HumanReviewRequest(
            agent_id="agent2",
            stage_name="stage2",
            artifact_type="type2",
            content="content2"
        )
        
        self.manager.pending_reviews.append(request1)
        self.manager.pending_reviews.append(request2)
        
        # Get review by ID
        found = self.manager.get_review_by_id(request1.id)
        
        # Verify correct review is returned
        self.assertEqual(found.id, request1.id)
        self.assertEqual(found.agent_id, "agent1")
        
        # Try non-existent ID
        not_found = self.manager.get_review_by_id("nonexistent-id")
        self.assertIsNone(not_found)
    
    def test_submit_feedback_approved(self):
        """Test submitting approval feedback"""
        # Create a test request
        callback_called = False
        callback_args = None
        
        def test_callback(approved, feedback):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = (approved, feedback)
        
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content"
        )
        
        # Add to pending reviews
        self.manager.pending_reviews.append(request)
        
        # Register callback
        self.manager.callbacks[request.id] = test_callback
        
        # Submit approval feedback
        result = self.manager.submit_feedback(
            review_id=request.id,
            approved=True,
            feedback="Great job!"
        )
        
        # Verify result
        self.assertTrue(result)
        
        # Verify callback was called
        self.assertTrue(callback_called)
        self.assertEqual(callback_args, (True, "Great job!"))
        
        # Verify review was removed from pending
        self.assertEqual(len(self.manager.pending_reviews), 0)
        
        # Verify review was added to completed
        self.assertEqual(len(self.manager.completed_reviews), 1)
        self.assertEqual(self.manager.completed_reviews[0]["id"], request.id)
        self.assertEqual(self.manager.completed_reviews[0]["status"], "approved")
        self.assertEqual(self.manager.completed_reviews[0]["feedback"], "Great job!")
        
        # Verify files were updated
        pending_path = os.path.join(self.temp_dir, "pending_reviews.json")
        completed_path = os.path.join(self.temp_dir, "completed_reviews.json")
        
        with open(pending_path, 'r') as f:
            pending_data = json.load(f)
        
        with open(completed_path, 'r') as f:
            completed_data = json.load(f)
        
        self.assertEqual(len(pending_data), 0)
        self.assertEqual(len(completed_data), 1)
        self.assertEqual(completed_data[0]["id"], request.id)
    
    def test_submit_feedback_rejected(self):
        """Test submitting rejection feedback"""
        # Create a test request
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content"
        )
        
        # Add to pending reviews
        self.manager.pending_reviews.append(request)
        
        # Submit rejection feedback
        result = self.manager.submit_feedback(
            review_id=request.id,
            approved=False,
            feedback="Needs improvement"
        )
        
        # Verify result
        self.assertTrue(result)
        
        # Verify review was removed from pending
        self.assertEqual(len(self.manager.pending_reviews), 0)
        
        # Verify review was added to completed
        self.assertEqual(len(self.manager.completed_reviews), 1)
        self.assertEqual(self.manager.completed_reviews[0]["id"], request.id)
        self.assertEqual(self.manager.completed_reviews[0]["status"], "rejected")
        self.assertEqual(self.manager.completed_reviews[0]["feedback"], "Needs improvement")
    
    def test_submit_feedback_invalid_id(self):
        """Test submitting feedback for non-existent review"""
        # Submit feedback for non-existent review
        result = self.manager.submit_feedback(
            review_id="nonexistent-id",
            approved=True,
            feedback="Great!"
        )
        
        # Verify result
        self.assertFalse(result)
        
        # Verify no reviews were changed
        self.assertEqual(len(self.manager.pending_reviews), 0)
        self.assertEqual(len(self.manager.completed_reviews), 0)
    
    def test_submit_feedback_callback_error(self):
        """Test handling errors in callbacks"""
        # Create a test request
        request = HumanReviewRequest(
            agent_id="test_agent",
            stage_name="test_stage",
            artifact_type="test_artifact",
            content="Test content"
        )
        
        # Add to pending reviews
        self.manager.pending_reviews.append(request)
        
        # Register callback that raises an exception
        def error_callback(approved, feedback):
            raise ValueError("Simulated callback error")
        
        self.manager.callbacks[request.id] = error_callback
        
        # Submit feedback
        result = self.manager.submit_feedback(
            review_id=request.id,
            approved=True,
            feedback="Great job!"
        )
        
        # Verify result (should still succeed despite callback error)
        self.assertTrue(result)
        
        # Verify review was processed correctly
        self.assertEqual(len(self.manager.pending_reviews), 0)
        self.assertEqual(len(self.manager.completed_reviews), 1)
