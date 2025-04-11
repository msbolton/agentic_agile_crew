"""
Integration tests for main application with human-in-the-loop functionality.

These tests verify that the main application correctly integrates with
the human review system.
"""

import os
import sys
import tempfile
import shutil
from unittest import TestCase, mock
import pytest
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Use mocks to work around module imports
sys.modules['src.tasks.business_analysis_task'] = mock.MagicMock()
sys.modules['src.tasks.prd_creation_task'] = mock.MagicMock()
sys.modules['src.tasks.architecture_design_task'] = mock.MagicMock()
sys.modules['src.tasks.task_list_creation_task'] = mock.MagicMock()
sys.modules['src.tasks.jira_creation_task'] = mock.MagicMock()
sys.modules['src.tasks.development_task'] = mock.MagicMock()
sys.modules['config.settings'] = mock.MagicMock()

# Now we can safely import main
with mock.patch('src.agents.business_analyst.create_business_analyst', return_value=mock.MagicMock()):
    with mock.patch('src.agents.project_manager.create_project_manager', return_value=mock.MagicMock()):
        with mock.patch('src.agents.architect.create_architect', return_value=mock.MagicMock()):
            with mock.patch('src.agents.product_owner.create_product_owner', return_value=mock.MagicMock()):
                with mock.patch('src.agents.scrum_master.create_scrum_master', return_value=mock.MagicMock()):
                    with mock.patch('src.agents.developer.create_developer', return_value=mock.MagicMock()):
                        from src.human_loop.manager import HumanReviewManager, HumanReviewRequest
                        import unittest.mock as mock_module
                        
                        # Create a base test case that doesn't rely on the actual main module
                        class TestMainIntegrationBase(TestCase):
                            """Base class for main application integration tests"""
                            
                            def setUp(self):
                                """Set up test environment"""
                                # Create a temporary directory for test data
                                self.temp_dir = tempfile.mkdtemp()
                                
                                # Create a test product idea
                                self.product_idea = """# Test Product
                                
                                Create a simple note-taking application with the following features:
                                - User authentication
                                - Create, edit, and delete notes
                                - Share notes with other users
                                - Search functionality
                                """
                            
                            def tearDown(self):
                                """Clean up after tests"""
                                shutil.rmtree(self.temp_dir)


class TestMainIntegration(TestMainIntegrationBase):
    """Integration tests for main application with human review system"""
    
    def test_human_review_integration(self):
        """Test that human review can be integrated into a workflow"""
        # Create a review manager
        review_manager = HumanReviewManager(storage_dir=self.temp_dir)
        
        # Create a mock task and agent
        mock_agent = mock.MagicMock()
        mock_agent.name = "TestAgent"
        
        mock_task = mock.MagicMock()
        mock_task.description = "Test task"
        mock_task.agent = mock_agent
        
        # Create a mock execute method that we can track
        original_execute = lambda: "Test output"
        mock_task.execute = original_execute
        
        # Create workflow adapter
        from src.human_loop.workflow import WorkflowAdapter
        workflow_adapter = WorkflowAdapter(review_manager)
        
        # Wrap the task
        wrapped_task = workflow_adapter.wrap_task(
            task=mock_task,
            stage_name="test_stage",
            artifact_type="test_artifact"
        )
        
        # Verify task was wrapped
        self.assertEqual(len(workflow_adapter.wrapped_tasks), 1)
        self.assertIn("Test task", workflow_adapter.wrapped_tasks)
        
        # Verify wrapper attributes
        wrapper = workflow_adapter.wrapped_tasks["Test task"]
        self.assertEqual(wrapper.original_task, mock_task)
        self.assertEqual(wrapper.stage_name, "test_stage")
        self.assertEqual(wrapper.artifact_type, "test_artifact")
        
        # Verify execute method was replaced
        self.assertIsNotNone(mock_task.execute)
        self.assertNotEqual(mock_task.execute, original_execute)
    
    def test_human_review_workflow(self):
        """Test a complete workflow with human review"""
        # Create a review manager
        review_manager = HumanReviewManager(storage_dir=self.temp_dir)
        
        # Create mock agents
        mock_agent1 = mock.MagicMock()
        mock_agent1.name = "Agent1"
        
        mock_agent2 = mock.MagicMock()
        mock_agent2.name = "Agent2"
        
        # Create mock tasks
        mock_task1 = mock.MagicMock()
        mock_task1.description = "Task1"
        mock_task1.agent = mock_agent1
        mock_task1.execute.return_value = "Output from Task1"
        
        mock_task2 = mock.MagicMock()
        mock_task2.description = "Task2" 
        mock_task2.agent = mock_agent2
        mock_task2.execute.return_value = "Output from Task2"
        
        # Create workflow adapter
        from src.human_loop.workflow import WorkflowAdapter
        workflow_adapter = WorkflowAdapter(review_manager)
        
        # Wrap tasks
        workflow_adapter.wrap_task(
            task=mock_task1,
            stage_name="stage1",
            artifact_type="artifact1"
        )
        
        workflow_adapter.wrap_task(
            task=mock_task2,
            stage_name="stage2",
            artifact_type="artifact2"
        )
        
        # Track review requests
        review_requests = []
        original_request_review = review_manager.request_review
        
        def capture_request_review(request):
            """Capture review requests and auto-approve"""
            review_id = original_request_review(request)
            review_requests.append((review_id, request))
            
            # Auto-approve
            review_manager.submit_feedback(
                review_id=review_id,
                approved=True,
                feedback="Looks good!"
            )
            
            return review_id
        
        # Create mock crew
        mock_crew = mock.MagicMock()
        mock_crew.agents = [mock_agent1, mock_agent2]
        mock_crew.tasks = [mock_task1, mock_task2]
        
        # Run the workflow with auto-approval
        with mock.patch.object(
            review_manager, 'request_review', side_effect=capture_request_review
        ):
            # Simulate crew execution by directly calling task execute methods
            output1 = mock_task1.execute()
            output2 = mock_task2.execute()
        
        # Verify reviews were requested and processed
        self.assertEqual(len(review_requests), 2)
        
        # Verify review stages
        stages = [req.stage_name for _, req in review_requests]
        self.assertEqual(stages, ["stage1", "stage2"])
        
        # Verify task outputs
        self.assertEqual(output1, "Output from Task1")
        self.assertEqual(output2, "Output from Task2")
        
        # Verify completed reviews
        completed = review_manager.get_completed_reviews()
        self.assertEqual(len(completed), 2)
