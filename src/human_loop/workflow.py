"""
Workflow adapter for integrating human-in-the-loop with CrewAI.

This module provides utilities for intercepting task outputs and sending them
for human review before they are passed to the next task in the workflow.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Callable, Union
from crewai import Task, Agent
from .manager import HumanReviewManager, HumanReviewRequest

# Optional imports
try:
    from src.artifacts.manager import ArtifactManager
    from src.artifacts.service import ArtifactService
    from src.artifacts.jira_connector import JiraConnector
    ARTIFACTS_AVAILABLE = True
except ImportError:
    ARTIFACTS_AVAILABLE = False

logger = logging.getLogger("human_review.workflow")

class HumanReviewTask:
    """
    Wraps a CrewAI task to intercept its output for human review.
    Supports feedback-driven revision cycles.
    """
    
    def __init__(
        self,
        original_task: Task,
        review_manager: HumanReviewManager,
        stage_name: str,
        artifact_type: str,
        workflow_adapter: 'WorkflowAdapter',
        wait_for_review: bool = True
    ):
        """
        Initialize a human review task wrapper.
        
        Args:
            original_task: The original CrewAI task
            review_manager: Human review manager instance
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact being produced
            workflow_adapter: Reference to the parent workflow adapter
            wait_for_review: Whether to wait for human review before proceeding
        """
        self.original_task = original_task
        self.review_manager = review_manager
        self.stage_name = stage_name
        self.artifact_type = artifact_type
        self.workflow_adapter = workflow_adapter
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
                context={
                    "task_description": self.original_task.description,
                    "workflow_adapter": self.workflow_adapter,
                    "original_task": self.original_task,
                    "agent": self.original_task.agent
                },
            )
            
            # Define callback for when review is complete
            def on_review_complete(approved: bool, feedback: str):
                if approved:
                    logger.info(f"Review approved for {self.stage_name}")
                    
                    # Try to save the artifact using the artifact service first
                    if self.workflow_adapter.artifact_service:
                        try:
                            filepath = self.workflow_adapter.artifact_service.save_artifact(
                                self.artifact_type,
                                output
                            )
                            logger.info(f"Saved artifact to {filepath} using artifact service")
                            
                            # Handle JIRA integration for stories/epics
                            if (self.workflow_adapter.jira_connector and 
                                self.workflow_adapter.jira_enabled and 
                                self.artifact_type == "JIRA epics and stories"):
                                try:
                                    logger.info("Creating JIRA epics and stories...")
                                    results = self.workflow_adapter.jira_connector.create_epics_and_stories(output)
                                    if results["success"]:
                                        logger.info(f"Created {len(results.get('epics', []))} epics and {len(results.get('stories', []))} stories in JIRA")
                                    else:
                                        logger.warning(f"Failed to create JIRA items: {results.get('error', 'Unknown error')}")
                                except Exception as e:
                                    logger.error(f"Error creating JIRA items: {e}")
                        except Exception as e:
                            logger.error(f"Error saving artifact via service: {e}")
                    # Fall back to using the artifact manager directly if needed
                    elif self.workflow_adapter.artifact_manager and self.workflow_adapter.product_idea_name:
                        try:
                            filepath = self.workflow_adapter.artifact_manager.save_artifact(
                                self.workflow_adapter.product_idea_name,
                                self.artifact_type,
                                output
                            )
                            logger.info(f"Saved artifact to {filepath} using artifact manager")
                            
                            # Handle JIRA integration for stories/epics
                            if (self.workflow_adapter.jira_connector and 
                                self.workflow_adapter.jira_enabled and 
                                self.artifact_type == "JIRA epics and stories"):
                                try:
                                    logger.info("Creating JIRA epics and stories...")
                                    results = self.workflow_adapter.jira_connector.create_epics_and_stories(output)
                                    if results["success"]:
                                        logger.info(f"Created {len(results.get('epics', []))} epics and {len(results.get('stories', []))} stories in JIRA")
                                    else:
                                        logger.warning(f"Failed to create JIRA items: {results.get('error', 'Unknown error')}")
                                except Exception as e:
                                    logger.error(f"Error creating JIRA items: {e}")
                        except Exception as e:
                            logger.error(f"Error saving artifact: {e}")
                else:
                    logger.info(f"Review rejected for {self.stage_name} with feedback: {feedback}")
                    # Note: Rejection will now be handled by the feedback-driven revision system
                    # in the HumanReviewManager.submit_feedback method
            
            # Submit for review with callback
            review_id = self.review_manager.request_review(request)
            self.review_manager.register_callback(review_id, on_review_complete)
            
            print(f"\n[!] Task output sent for human review. ID: {review_id}")
            print(f"The workflow will pause until review is complete.")
            print(f"Run 'python cli.py review {review_id}' to review.")
            
            logger.info(f"Task output sent for human review. ID: {review_id}")
            
            return output
        else:
            # Skip human review
            logger.info(f"Skipping human review for {self.stage_name}")
            return output


class WorkflowAdapter:
    """
    Adapts the CrewAI workflow to include human-in-the-loop reviews.
    """
    
    def __init__(
        self, 
        review_manager: HumanReviewManager,
        artifact_manager: Optional[Any] = None,
        artifact_service: Optional[Any] = None,
        jira_connector: Optional[Any] = None,
        jira_enabled: bool = False
    ):
        """
        Initialize the workflow adapter.
        
        Args:
            review_manager: Human review manager instance
            artifact_manager: Optional artifact manager for saving artifacts
            artifact_service: Optional artifact service for saving artifacts
            jira_connector: Optional JIRA connector for JIRA integration
            jira_enabled: Whether JIRA integration is enabled
        """
        self.review_manager = review_manager
        self.artifact_manager = artifact_manager
        self.artifact_service = artifact_service
        self.jira_connector = jira_connector
        self.jira_enabled = jira_enabled
        self.wrapped_tasks = {}
        self.product_idea_name = None
    
    def set_product_idea_name(self, name: str):
        """
        Set the product idea name for artifact management.
        
        Args:
            name: The product idea name
        """
        self.product_idea_name = name
        logger.info(f"Set product idea name: {name}")
    
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
            workflow_adapter=self,
            wait_for_review=wait_for_review
        )
        
        self.wrapped_tasks[task.description] = wrapper
        logger.info(f"Wrapped task for human review: {stage_name}")
        
        return task  # Return the same task, but with execute method replaced
