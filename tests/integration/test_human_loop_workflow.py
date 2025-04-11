"""
Integration tests for human-in-the-loop workflow in Agentic Agile Crew.

These tests verify that the human review functionality works correctly
with the actual CrewAI workflow.
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

# Import our application components
from src.human_loop.manager import HumanReviewManager, HumanReviewRequest
from src.human_loop.workflow import WorkflowAdapter


class MockTask:
    """Mock task for testing"""
    def __init__(self, description, agent):
        self.description = description
        self.agent = agent
        self.context = []
    
    def execute(self):
        """Execute the task"""
        return f"Output from {self.description}"


class TestHumanLoopWorkflow(TestCase):
    """Integration tests for human-in-the-loop workflow"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create human review manager
        self.review_manager = HumanReviewManager(storage_dir=self.temp_dir)
        
        # Create workflow adapter
        self.workflow_adapter = WorkflowAdapter(self.review_manager)
        
        # Create mock agents
        self.business_analyst = mock.MagicMock()
        self.business_analyst.name = "BusinessAnalyst"
        self.business_analyst.role = "Business Analyst"
        
        self.project_manager = mock.MagicMock()
        self.project_manager.name = "ProjectManager"
        self.project_manager.role = "Project Manager"
        
        self.architect = mock.MagicMock()
        self.architect.name = "Architect"
        self.architect.role = "System Architect"
        
        # Set expected outputs for execute_task if needed
        self.business_analyst.execute_task.return_value = "Business Requirements"
        self.project_manager.execute_task.return_value = "PRD Document"
        self.architect.execute_task.return_value = "Architecture Document"
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_workflow_with_approval(self):
        """Test a simple workflow where all reviews are approved"""
        # Create the tasks
        product_idea = "Build a test application"
        
        # Create tasks
        business_analysis_task = MockTask(
            description="Analyze the product idea",
            agent=self.business_analyst
        )
        
        prd_creation_task = MockTask(
            description="Create a PRD document",
            agent=self.project_manager
        )
        
        architecture_design_task = MockTask(
            description="Design the system architecture",
            agent=self.architect
        )
        
        # Wrap tasks with human review
        self.workflow_adapter.wrap_task(
            task=business_analysis_task,
            stage_name="business_analysis",
            artifact_type="requirements"
        )
        
        self.workflow_adapter.wrap_task(
            task=prd_creation_task,
            stage_name="prd_creation",
            artifact_type="PRD document"
        )
        
        self.workflow_adapter.wrap_task(
            task=architecture_design_task,
            stage_name="architecture_design",
            artifact_type="architecture document"
        )
        
        # Set up auto-approval for all review requests
        original_request_review = self.review_manager.request_review
        review_ids = []
        
        def mock_request_review(request):
            """Mock request_review to automatically approve all requests"""
            review_id = original_request_review(request)
            review_ids.append(review_id)
            
            # Auto-approve the review
            self.review_manager.submit_feedback(
                review_id=review_id,
                approved=True,
                feedback="Looks good!"
            )
            
            return review_id
        
        # Run the workflow with auto-approval
        with mock.patch.object(
            self.review_manager, 'request_review', side_effect=mock_request_review
        ):
            # Execute each task in sequence to simulate the workflow
            result1 = business_analysis_task.execute()
            result2 = prd_creation_task.execute()
            result3 = architecture_design_task.execute()
        
        # Verify all tasks were reviewed and approved
        self.assertEqual(len(review_ids), 3)
        
        # Verify all tasks executed
        self.assertEqual(result1, "Output from Analyze the product idea")
        self.assertEqual(result2, "Output from Create a PRD document")
        self.assertEqual(result3, "Output from Design the system architecture")
        
        # Verify all reviews were completed with "approved" status
        completed_reviews = self.review_manager.get_completed_reviews()
        self.assertEqual(len(completed_reviews), 3)
        for review in completed_reviews:
            self.assertEqual(review["status"], "approved")
    
    def test_workflow_with_rejection_and_revision(self):
        """Test a workflow where a review is rejected and the agent must revise"""
        # Create the tasks
        product_idea = "Build a test application"
        
        # Create tasks
        business_analysis_task = MockTask(
            description="Analyze the product idea",
            agent=self.business_analyst
        )
        
        prd_creation_task = MockTask(
            description="Create a PRD document",
            agent=self.project_manager
        )
        
        # Create a mock for the original execute method
        original_execute = business_analysis_task.execute
        
        # Create a function to track revision
        revision_requested = False
        
        def revised_execute():
            nonlocal revision_requested
            if not revision_requested:
                # First call - original output
                result = original_execute()
            else:
                # Revised output after rejection
                result = "Revised " + original_execute()
            return result
        
        # Replace the execute method
        business_analysis_task.execute = revised_execute
        
        # Wrap tasks with human review
        self.workflow_adapter.wrap_task(
            task=business_analysis_task,
            stage_name="business_analysis",
            artifact_type="requirements"
        )
        
        self.workflow_adapter.wrap_task(
            task=prd_creation_task,
            stage_name="prd_creation",
            artifact_type="PRD document"
        )
        
        # Set up a counter for the review requests
        review_counter = 0
        original_request_review = self.review_manager.request_review
        
        def mock_request_review(request):
            """Mock request_review to reject first task and approve others"""
            nonlocal review_counter
            nonlocal revision_requested
            review_counter += 1
            
            review_id = original_request_review(request)
            
            # First review is rejected, others are approved
            if review_counter == 1:
                # Reject the business analysis
                revision_requested = True
                self.review_manager.submit_feedback(
                    review_id=review_id,
                    approved=False,
                    feedback="Missing security requirements"
                )
            else:
                # Approve other reviews
                self.review_manager.submit_feedback(
                    review_id=review_id,
                    approved=True,
                    feedback="Looks good!"
                )
            
            return review_id
        
        # Run the workflow with rejection scenario
        with mock.patch.object(
            self.review_manager, 'request_review', side_effect=mock_request_review
        ):
            # Execute each task in sequence to simulate the workflow
            result1 = business_analysis_task.execute()
            # Second execution after rejection
            result1_revised = business_analysis_task.execute()
            result2 = prd_creation_task.execute()
        
        # Verify the workflow handled rejection and revision
        self.assertEqual(review_counter, 3)  # Initial task, revised task, second task
        
        # Verify results
        self.assertEqual(result1, "Output from Analyze the product idea")
        self.assertEqual(result1_revised, "Revised Output from Analyze the product idea")
        self.assertEqual(result2, "Output from Create a PRD document")
        
        # Verify reviews were processed
        completed_reviews = self.review_manager.get_completed_reviews()
        self.assertEqual(len(completed_reviews), 3)
        
        # Check statuses
        statuses = [review["status"] for review in completed_reviews]
        self.assertIn("rejected", statuses)
        self.assertIn("approved", statuses)
    
    def test_workflow_with_human_intervention(self):
        """Test a more complex workflow with simulated human intervention"""
        # Create the tasks
        product_idea = "Build a test application"
        
        # Create tasks
        business_analysis_task = MockTask(
            description="Analyze the product idea",
            agent=self.business_analyst
        )
        
        prd_creation_task = MockTask(
            description="Create a PRD document",
            agent=self.project_manager
        )
        
        architecture_design_task = MockTask(
            description="Design the system architecture",
            agent=self.architect
        )
        
        # Create mocks for the original execute methods
        original_ba_execute = business_analysis_task.execute
        original_pm_execute = prd_creation_task.execute
        
        # Create a function to track revision for PRD
        prd_revision_requested = False
        
        def revised_pm_execute():
            if not prd_revision_requested:
                # First call - original output
                result = original_pm_execute()
            else:
                # Revised output after rejection
                result = "Revised " + original_pm_execute() + " with User Stories"
            return result
        
        # Replace the execute method
        prd_creation_task.execute = revised_pm_execute
        
        # Wrap tasks with human review
        self.workflow_adapter.wrap_task(
            task=business_analysis_task,
            stage_name="business_analysis",
            artifact_type="requirements"
        )
        
        self.workflow_adapter.wrap_task(
            task=prd_creation_task,
            stage_name="prd_creation",
            artifact_type="PRD document"
        )
        
        self.workflow_adapter.wrap_task(
            task=architecture_design_task,
            stage_name="architecture_design",
            artifact_type="architecture document"
        )
        
        # Record all review requests
        original_request_review = self.review_manager.request_review
        review_requests = []
        
        def capture_request_review(request):
            """Capture review requests and simulate manual reviews"""
            nonlocal prd_revision_requested
            
            review_id = original_request_review(request)
            review_requests.append((review_id, request))
            
            # Simulate different review decisions based on stage
            if request.stage_name == "business_analysis":
                # Approve business analysis
                self.review_manager.submit_feedback(
                    review_id=review_id,
                    approved=True,
                    feedback="Requirements look complete"
                )
            elif request.stage_name == "prd_creation":
                if not prd_revision_requested:
                    # Reject PRD with feedback (first time)
                    prd_revision_requested = True
                    self.review_manager.submit_feedback(
                        review_id=review_id,
                        approved=False,
                        feedback="Need more detail on user stories"
                    )
                else:
                    # Approve revised PRD
                    self.review_manager.submit_feedback(
                        review_id=review_id,
                        approved=True,
                        feedback="User stories look good now"
                    )
            else:
                # Approve architecture with feedback
                self.review_manager.submit_feedback(
                    review_id=review_id,
                    approved=True,
                    feedback="Architecture looks good, consider adding caching layer in future"
                )
            
            return review_id
        
        # Run the workflow with simulated human reviews
        with mock.patch.object(
            self.review_manager, 'request_review', side_effect=capture_request_review
        ):
            # Execute each task in sequence to simulate the workflow
            result1 = business_analysis_task.execute()
            result2 = prd_creation_task.execute()  # This will be rejected
            result2_revised = prd_creation_task.execute()  # This should be the revised version
            result3 = architecture_design_task.execute()
        
        # Verify the correct number of reviews were performed
        self.assertEqual(len(review_requests), 4)  # Initial 3 tasks + 1 revision
        
        # Verify review stages
        stages = [req.stage_name for _, req in review_requests]
        self.assertEqual(stages.count("business_analysis"), 1)
        self.assertEqual(stages.count("prd_creation"), 2)  # Original + revision
        self.assertEqual(stages.count("architecture_design"), 1)
        
        # Verify output contents
        self.assertEqual(result1, "Output from Analyze the product idea")
        self.assertEqual(result2, "Output from Create a PRD document")
        self.assertEqual(result2_revised, "Revised Output from Create a PRD document with User Stories")
        self.assertEqual(result3, "Output from Design the system architecture")
        
        # Verify completed reviews
        completed_reviews = self.review_manager.get_completed_reviews()
        self.assertEqual(len(completed_reviews), 4)
