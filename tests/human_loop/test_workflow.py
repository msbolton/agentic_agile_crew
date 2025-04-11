"""
Unit tests for the workflow adapter in src.human_loop.workflow
"""

import os
import tempfile
import shutil
from unittest import TestCase, mock
import pytest

from src.human_loop.workflow import WorkflowAdapter, HumanReviewTask
from src.human_loop.manager import HumanReviewManager, HumanReviewRequest


class MockAgent:
    """Mock agent for testing"""
    def __init__(self, name="mock_agent"):
        self.name = name


class MockTask:
    """Mock task for testing"""
    def __init__(self, description="mock_task", agent=None):
        self.description = description
        self.agent = agent or MockAgent()
        self.execute_called = False
        self.execute_args = None
        self.execute_kwargs = None
        self.result = "Mock task output"
        self.original_execute = None  # Store the original execute method
    
    def execute(self, *args, **kwargs):
        """Mock execute method"""
        self.execute_called = True
        self.execute_args = args
        self.execute_kwargs = kwargs
        return self.result


class TestHumanReviewTask(TestCase):
    """Test cases for HumanReviewTask class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.review_manager = HumanReviewManager(storage_dir=self.temp_dir)
        
        # Create mock task
        self.agent = MockAgent(name="test_agent")
        self.original_task = MockTask(description="test_task", agent=self.agent)
        # Store the original execute method
        self.original_execute = self.original_task.execute
    
    def tearDown(self):
        """Clean up temporary directory after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test initialization"""
        # Create wrapper
        wrapper = HumanReviewTask(
            original_task=self.original_task,
            review_manager=self.review_manager,
            stage_name="test_stage",
            artifact_type="test_artifact"
        )
        
        # Verify instance variables
        self.assertEqual(wrapper.original_task, self.original_task)
        self.assertEqual(wrapper.review_manager, self.review_manager)
        self.assertEqual(wrapper.stage_name, "test_stage")
        self.assertEqual(wrapper.artifact_type, "test_artifact")
        self.assertTrue(wrapper.wait_for_review)
        
        # Verify the execute method was replaced
        self.assertIsNotNone(self.original_task.execute)
        self.assertNotEqual(self.original_task.execute, self.original_execute)
    
    def test_execute_with_review(self):
        """Test execution with human review"""
        # Create wrapper
        wrapper = HumanReviewTask(
            original_task=self.original_task,
            review_manager=self.review_manager,
            stage_name="test_stage",
            artifact_type="test_artifact"
        )
        
        # Mock review_manager.request_review to avoid actual file operations
        with mock.patch.object(
            self.review_manager, 'request_review', return_value="mock-id-123"
        ) as mock_request:
            # Execute the task
            result = self.original_task.execute("arg1", kwarg1="value1")
            
            # Verify original task was executed
            self.assertTrue(self.original_task.execute_called)
            self.assertEqual(self.original_task.execute_args, ("arg1",))
            self.assertEqual(self.original_task.execute_kwargs, {"kwarg1": "value1"})
            
            # Verify review was requested
            self.assertEqual(mock_request.call_count, 1)
            request = mock_request.call_args[0][0]
            self.assertEqual(request.agent_id, "test_agent")
            self.assertEqual(request.stage_name, "test_stage")
            self.assertEqual(request.artifact_type, "test_artifact")
            self.assertEqual(request.content, "Mock task output")
            
            # Verify correct result is returned
            self.assertEqual(result, "Mock task output")
    
    def test_execute_without_review(self):
        """Test execution without human review"""
        # Create wrapper with wait_for_review=False
        wrapper = HumanReviewTask(
            original_task=self.original_task,
            review_manager=self.review_manager,
            stage_name="test_stage",
            artifact_type="test_artifact",
            wait_for_review=False
        )
        
        # Mock review_manager.request_review to verify it's not called
        with mock.patch.object(self.review_manager, 'request_review') as mock_request:
            # Execute the task
            result = self.original_task.execute()
            
            # Verify original task was executed
            self.assertTrue(self.original_task.execute_called)
            
            # Verify review was not requested
            mock_request.assert_not_called()
            
            # Verify correct result is returned
            self.assertEqual(result, "Mock task output")


class TestWorkflowAdapter(TestCase):
    """Test cases for WorkflowAdapter class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.review_manager = HumanReviewManager(storage_dir=self.temp_dir)
        self.workflow_adapter = WorkflowAdapter(self.review_manager)
        
        # Create mock tasks
        self.agent1 = MockAgent(name="agent1")
        self.agent2 = MockAgent(name="agent2")
        self.task1 = MockTask(description="task1", agent=self.agent1)
        self.task2 = MockTask(description="task2", agent=self.agent2)
    
    def tearDown(self):
        """Clean up temporary directory after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test initialization"""
        # Verify instance variables
        self.assertEqual(self.workflow_adapter.review_manager, self.review_manager)
        self.assertEqual(self.workflow_adapter.wrapped_tasks, {})
    
    def test_wrap_task(self):
        """Test wrapping a task"""
        # Wrap task1
        wrapped_task = self.workflow_adapter.wrap_task(
            task=self.task1,
            stage_name="stage1",
            artifact_type="artifact1"
        )
        
        # Verify task was wrapped
        self.assertEqual(wrapped_task, self.task1)  # Same instance is returned
        self.assertEqual(len(self.workflow_adapter.wrapped_tasks), 1)
        self.assertIn("task1", self.workflow_adapter.wrapped_tasks)
        
        # Verify wrapper type
        wrapper = self.workflow_adapter.wrapped_tasks["task1"]
        self.assertIsInstance(wrapper, HumanReviewTask)
        
        # Verify wrapper attributes
        self.assertEqual(wrapper.original_task, self.task1)
        self.assertEqual(wrapper.review_manager, self.review_manager)
        self.assertEqual(wrapper.stage_name, "stage1")
        self.assertEqual(wrapper.artifact_type, "artifact1")
        self.assertTrue(wrapper.wait_for_review)
    
    def test_wrap_multiple_tasks(self):
        """Test wrapping multiple tasks"""
        # Wrap task1
        self.workflow_adapter.wrap_task(
            task=self.task1,
            stage_name="stage1",
            artifact_type="artifact1"
        )
        
        # Wrap task2
        self.workflow_adapter.wrap_task(
            task=self.task2,
            stage_name="stage2",
            artifact_type="artifact2",
            wait_for_review=False
        )
        
        # Verify both tasks were wrapped
        self.assertEqual(len(self.workflow_adapter.wrapped_tasks), 2)
        self.assertIn("task1", self.workflow_adapter.wrapped_tasks)
        self.assertIn("task2", self.workflow_adapter.wrapped_tasks)
        
        # Verify wrapper attributes for task2
        wrapper2 = self.workflow_adapter.wrapped_tasks["task2"]
        self.assertEqual(wrapper2.original_task, self.task2)
        self.assertEqual(wrapper2.stage_name, "stage2")
        self.assertEqual(wrapper2.artifact_type, "artifact2")
        self.assertFalse(wrapper2.wait_for_review)
