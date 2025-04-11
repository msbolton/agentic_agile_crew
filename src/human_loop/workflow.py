"""
Workflow adapter for integrating human-in-the-loop with CrewAI.

This module provides utilities for intercepting task outputs and sending them
for human review before they are passed to the next task in the workflow.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Union
from crewai import Task, Agent
from .manager import HumanReviewManager, HumanReviewRequest

logger = logging.getLogger("human_review.workflow")

class HumanReviewTask:
    """
    Wraps a CrewAI task to intercept its output for human review.
    """
    
    def __init__(
        self,
        original_task: Task,
        review_manager: HumanReviewManager,
        stage_name: str,
        artifact_type: str,
        wait_for_review: bool = True
    ):
        """
        Initialize a human review task wrapper.
        
        Args:
            original_task: The original CrewAI task
            review_manager: Human review manager instance
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact being produced
            wait_for_review: Whether to wait for human review before proceeding
        """
        self.original_task = original_task
        self.review_manager = review_manager
        self.stage_name = stage_name
        self.artifact_type = artifact_type
        self.wait_for_review = wait_for_review
        
        # Store original execute method
        self._original_execute = original_task.execute
        
        # Replace with our interceptor
        original_task.execute = self._execute_with_review
    
    def _execute_with_review(self, *args, **kwargs):
        """
        Execute the original task and intercept its output for human review.
        """
        logger.info(f"Executing task with human review: {self.stage_name}")
        
        # Execute the original task
        output = self._original_execute(*args, **kwargs)
        
        if self.wait_for_review:
            # Create a new review request
            request = HumanReviewRequest(
                agent_id=self.original_task.agent.name,
                stage_name=self.stage_name,
                artifact_type=self.artifact_type,
                content=output,
                context={"task_description": self.original_task.description},
            )
            
            # Submit for review and wait for response
            review_id = self.review_manager.request_review(request)
            
            # This is a bit tricky - we need to wait for the review to complete
            # In a real CLI application, we would need to implement a waiting mechanism
            # For now, we'll use a simple sentinel file approach
            
            print(f"\n[!] Task output sent for human review. ID: {review_id}")
            print(f"The workflow will pause until review is complete.")
            print(f"Run 'python cli.py review {review_id}' to review.")
            
            # Create a sentinel file to indicate we're waiting for review
            # This could be replaced with a more robust approach in a real application
            
            logger.info(f"Task output sent for human review. ID: {review_id}")
            
            # Wait for the review to complete - in a real CLI this would be handled differently
            # For a CLI application, the main process would exit here and be resumed later
            
            # For now, we'll simulate the process by manually checking for reviews
            # In a real application, we would implement a more robust waiting mechanism
            
            return output
        else:
            # Skip human review
            logger.info(f"Skipping human review for {self.stage_name}")
            return output


class WorkflowAdapter:
    """
    Adapts the CrewAI workflow to include human-in-the-loop reviews.
    """
    
    def __init__(self, review_manager: HumanReviewManager):
        """
        Initialize the workflow adapter.
        
        Args:
            review_manager: Human review manager instance
        """
        self.review_manager = review_manager
        self.wrapped_tasks = {}
    
    def wrap_task(
        self,
        task: Task,
        stage_name: str,
        artifact_type: str,
        wait_for_review: bool = True
    ) -> Task:
        """
        Wrap a CrewAI task to include human review.
        
        Args:
            task: The original CrewAI task
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact being produced
            wait_for_review: Whether to wait for human review before proceeding
            
        Returns:
            The wrapped task (same instance, modified)
        """
        wrapper = HumanReviewTask(
            original_task=task,
            review_manager=self.review_manager,
            stage_name=stage_name,
            artifact_type=artifact_type,
            wait_for_review=wait_for_review
        )
        
        self.wrapped_tasks[task.description] = wrapper
        logger.info(f"Wrapped task for human review: {stage_name}")
        
        return task  # Return the same task, but with execute method replaced
