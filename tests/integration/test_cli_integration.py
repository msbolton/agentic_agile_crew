"""
Integration tests for CLI interface with human-in-the-loop workflow.

These tests verify that the CLI correctly interacts with the review system
and workflow components.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from unittest import TestCase, mock
import pytest
from typing import List, Dict, Any, Optional
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our CLI and review components
import cli
from src.human_loop.manager import HumanReviewManager, HumanReviewRequest


class TestCLIIntegration(TestCase):
    """Integration tests for CLI interface with human review workflow"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test product idea file
        self.idea_file = os.path.join(self.temp_dir, "test_idea.md")
        with open(self.idea_file, "w") as f:
            f.write("# Test Product Idea\n\nThis is a test product idea for unit testing.")
        
        # Mock the review manager to use our test directory
        self.original_review_manager = cli.review_manager
        cli.review_manager = HumanReviewManager(storage_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original review manager
        cli.review_manager = self.original_review_manager
        
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)
    
    def test_list_reviews_with_actual_reviews(self):
        """Test listing reviews with actual review data"""
        # Create some test review requests
        request1 = HumanReviewRequest(
            agent_id="business_analyst",
            stage_name="business_analysis",
            artifact_type="requirements",
            content="Test requirements"
        )
        
        request2 = HumanReviewRequest(
            agent_id="project_manager",
            stage_name="prd_creation",
            artifact_type="PRD document",
            content="Test PRD document"
        )
        
        # Add reviews to pending list
        cli.review_manager.request_review(request1)
        cli.review_manager.request_review(request2)
        
        # Call list_reviews
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace()
            cli.list_reviews(args)
            
            # Verify output contains review information
            mock_print.assert_any_call(mock.ANY)  # Title
            
            # Check that both reviews are mentioned
            prints = [call[0][0] for call in mock_print.call_args_list if isinstance(call[0][0], str)]
            business_analyst_mentioned = any("business_analyst" in p for p in prints)
            project_manager_mentioned = any("project_manager" in p for p in prints)
            
            self.assertTrue(business_analyst_mentioned)
            self.assertTrue(project_manager_mentioned)
    
    def test_review_item_approval(self):
        """Test reviewing an item with approval"""
        # Create a test review request
        request = HumanReviewRequest(
            agent_id="architect",
            stage_name="architecture_design",
            artifact_type="architecture document",
            content="Test architecture document"
        )
        
        # Add review to pending list
        review_id = cli.review_manager.request_review(request)
        
        # Record callback execution
        callback_executed = False
        callback_approved = None
        callback_feedback = None
        
        def test_callback(approved, feedback):
            nonlocal callback_executed, callback_approved, callback_feedback
            callback_executed = True
            callback_approved = approved
            callback_feedback = feedback
        
        # Register callback
        cli.review_manager.register_callback(review_id, test_callback)
        
        # Mock user input for approval
        with mock.patch("builtins.input", side_effect=["yes", "Great work!"]):
            with mock.patch("builtins.print"):
                with mock.patch("cli.clear_screen"):
                    # Call review_item
                    args = argparse.Namespace(review_id=review_id)
                    cli.review_item(args)
        
        # Verify callback was executed with approval
        self.assertTrue(callback_executed)
        self.assertTrue(callback_approved)
        self.assertEqual(callback_feedback, "Great work!")
        
        # Verify review was moved to completed
        self.assertEqual(len(cli.review_manager.get_pending_reviews()), 0)
        self.assertEqual(len(cli.review_manager.get_completed_reviews()), 1)
        
        # Verify completed review has correct status
        completed = cli.review_manager.get_completed_reviews()[0]
        self.assertEqual(completed["status"], "approved")
        self.assertEqual(completed["feedback"], "Great work!")
    
    def test_review_item_rejection(self):
        """Test reviewing an item with rejection"""
        # Create a test review request
        request = HumanReviewRequest(
            agent_id="product_owner",
            stage_name="task_breakdown",
            artifact_type="task list",
            content="Test task list"
        )
        
        # Add review to pending list
        review_id = cli.review_manager.request_review(request)
        
        # Record callback execution
        callback_executed = False
        callback_approved = None
        callback_feedback = None
        
        def test_callback(approved, feedback):
            nonlocal callback_executed, callback_approved, callback_feedback
            callback_executed = True
            callback_approved = approved
            callback_feedback = feedback
        
        # Register callback
        cli.review_manager.register_callback(review_id, test_callback)
        
        # Mock user input for rejection
        with mock.patch("builtins.input", side_effect=["no", "Need more detailed tasks"]):
            with mock.patch("builtins.print"):
                with mock.patch("cli.clear_screen"):
                    # Call review_item
                    args = argparse.Namespace(review_id=review_id)
                    cli.review_item(args)
        
        # Verify callback was executed with rejection
        self.assertTrue(callback_executed)
        self.assertFalse(callback_approved)
        self.assertEqual(callback_feedback, "Need more detailed tasks")
        
        # Verify review was moved to completed
        self.assertEqual(len(cli.review_manager.get_pending_reviews()), 0)
        self.assertEqual(len(cli.review_manager.get_completed_reviews()), 1)
        
        # Verify completed review has correct status
        completed = cli.review_manager.get_completed_reviews()[0]
        self.assertEqual(completed["status"], "rejected")
        self.assertEqual(completed["feedback"], "Need more detailed tasks")
    
    def test_project_status_with_reviews(self):
        """Test project status display with actual review data"""
        # Create and process some reviews
        # Approved business analysis
        request1 = HumanReviewRequest(
            agent_id="business_analyst",
            stage_name="business_analysis",
            artifact_type="requirements",
            content="Test requirements"
        )
        review_id1 = cli.review_manager.request_review(request1)
        cli.review_manager.submit_feedback(review_id1, True, "Good")
        
        # Rejected PRD
        request2 = HumanReviewRequest(
            agent_id="project_manager",
            stage_name="prd_creation",
            artifact_type="PRD document",
            content="Test PRD document"
        )
        review_id2 = cli.review_manager.request_review(request2)
        cli.review_manager.submit_feedback(review_id2, False, "Needs work")
        
        # Pending architecture
        request3 = HumanReviewRequest(
            agent_id="architect",
            stage_name="architecture_design",
            artifact_type="architecture document",
            content="Test architecture document"
        )
        cli.review_manager.request_review(request3)
        
        # Call project_status
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace()
            cli.project_status(args)
            
            # Verify output contains status information
            prints = [str(call[0][0]) for call in mock_print.call_args_list if len(call[0]) > 0]
            
            # Check for expected status indicators
            approved_status = any("Completed and approved" in p for p in prints)
            rejected_status = any("Completed but rejected" in p for p in prints)
            pending_status = any("Awaiting review" in p for p in prints)
            
            self.assertTrue(approved_status)
            self.assertTrue(rejected_status)
            self.assertTrue(pending_status)
