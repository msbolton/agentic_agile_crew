"""
Revision Cycle for the Human-in-the-Loop review process.

This module implements the core revision cycle logic, managing the flow
of feedback from humans back to agents for revision.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Union
from crewai import Task, Agent

from .parser import FeedbackParser, FeedbackItem
from .memory import FeedbackMemory
from .limiter import CycleLimiter

logger = logging.getLogger("human_review.revision_cycle")

class RevisionCycle:
    """
    Manages the revision cycle process, routing feedback back to agents.
    """
    
    def __init__(
        self,
        feedback_memory: FeedbackMemory,
        cycle_limiter: CycleLimiter
    ):
        """
        Initialize the revision cycle.
        
        Args:
            feedback_memory: Memory system for storing revisions and feedback
            cycle_limiter: Limiter to prevent infinite revision cycles
        """
        self.feedback_memory = feedback_memory
        self.cycle_limiter = cycle_limiter
        self.in_progress_revisions = {}
    
    def start_revision(
        self,
        agent: Agent,
        original_task: Task,
        stage_name: str,
        artifact_type: str,
        feedback: str,
        original_content: Any,
        callback: Callable = None
    ) -> Dict[str, Any]:
        """
        Start a revision cycle based on feedback.
        
        Args:
            agent: The agent that will perform the revision
            original_task: The original task that produced the content
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact being revised
            feedback: Human feedback to incorporate
            original_content: The original content to be revised
            callback: Function to call when revision is complete
            
        Returns:
            Dictionary with revision information
        """
        agent_id = agent.name
        
        # Parse the feedback
        feedback_items = FeedbackParser.parse(feedback)
        formatted_feedback = FeedbackParser.format_for_agent(feedback_items)
        
        # Track cycle and check limits
        cycle_status = self.cycle_limiter.track_cycle(agent_id, stage_name)
        
        # Get revision context from memory
        revision_context = self.feedback_memory.get_revision_context(agent_id, stage_name)
        
        # Create the revision task description
        task_description = self._create_revision_task_description(
            original_task.description,
            formatted_feedback,
            cycle_status,
            revision_context
        )
        
        # Create a new task for the revision
        revision_task = Task(
            description=task_description,
            agent=agent,
            expected_output=f"Revised {artifact_type}",
            async_execution=False
        )
        
        # Store information about the in-progress revision
        revision_info = {
            "agent_id": agent_id,
            "stage_name": stage_name,
            "artifact_type": artifact_type,
            "original_content": original_content,
            "feedback": feedback,
            "formatted_feedback": formatted_feedback,
            "task": revision_task,
            "cycle_status": cycle_status,
            "callback": callback
        }
        
        # Generate a unique key for this revision
        revision_key = f"{agent_id}_{stage_name}_{cycle_status['cycle_count']}"
        self.in_progress_revisions[revision_key] = revision_info
        
        logger.info(
            f"Starting revision cycle {cycle_status['cycle_count']} "
            f"for {agent_id} in {stage_name}"
        )
        
        return {
            "revision_key": revision_key,
            "task": revision_task,
            "cycle_status": cycle_status
        }
    
    def _create_revision_task_description(
        self,
        original_description: str,
        formatted_feedback: str,
        cycle_status: Dict[str, Any],
        revision_context: Dict[str, Any]
    ) -> str:
        """
        Create a detailed task description for the revision task.
        
        Args:
            original_description: Original task description
            formatted_feedback: Formatted feedback for agent consumption
            cycle_status: Current cycle status information
            revision_context: Context from previous revisions
            
        Returns:
            Detailed task description for the revision
        """
        # Start with the original task description
        description = original_description
        
        # Add revision-specific instructions
        description += "\n\n"
        description += "## REVISION REQUIRED\n\n"
        description += f"This is revision cycle {cycle_status['cycle_count']} of a maximum {cycle_status['max_cycles']}.\n\n"
        
        # Add the formatted feedback
        description += formatted_feedback + "\n\n"
        
        # Add context from previous revisions if available
        if revision_context['revision_count'] > 0:
            description += "## Previous Revision History\n\n"
            description += f"You have made {revision_context['revision_count']} previous revision(s).\n"
            
            # Add previous feedback summaries
            if revision_context['previous_feedback']:
                description += "\nPrevious feedback:\n\n"
                for feedback_item in revision_context['previous_feedback']:
                    status = feedback_item['status'].upper()
                    version = feedback_item['version']
                    feedback_text = feedback_item['feedback']
                    
                    description += f"- Version {version} ({status}): {feedback_text[:100]}...\n"
        
        # Add final guidance
        description += "\n## Revision Instructions\n\n"
        description += "1. Carefully review the feedback provided.\n"
        description += "2. Revise the content to address all feedback points.\n"
        description += "3. If any feedback is unclear, use your best judgment.\n"
        description += "4. Return the complete revised content, not just the changes.\n"
        
        if cycle_status['limit_reached']:
            description += "\n**NOTE: This is the final revision cycle. Make your best effort to address all feedback.**\n"
        
        return description
    
    def complete_revision(
        self,
        revision_key: str,
        revised_content: Any,
        status: str = "completed"
    ) -> Dict[str, Any]:
        """
        Complete a revision cycle.
        
        Args:
            revision_key: The unique key for the revision
            revised_content: The revised content produced by the agent
            status: Status of the revision (completed/failed)
            
        Returns:
            Dictionary with completion information
        """
        if revision_key not in self.in_progress_revisions:
            logger.error(f"Revision key {revision_key} not found")
            return {"success": False, "error": "Revision not found"}
        
        # Get the revision info
        revision_info = self.in_progress_revisions[revision_key]
        
        # Record the revision in memory
        self.feedback_memory.record_revision(
            agent_id=revision_info["agent_id"],
            stage_name=revision_info["stage_name"],
            artifact_type=revision_info["artifact_type"],
            content=revised_content,
            feedback=revision_info["feedback"],
            status=status
        )
        
        # Execute callback if available
        callback = revision_info.get("callback")
        if callback:
            try:
                callback(revised_content, status)
            except Exception as e:
                logger.error(f"Error executing revision callback: {e}")
        
        # Clean up
        del self.in_progress_revisions[revision_key]
        
        logger.info(
            f"Completed revision cycle for {revision_info['agent_id']} "
            f"in {revision_info['stage_name']} with status {status}"
        )
        
        return {
            "success": True,
            "agent_id": revision_info["agent_id"],
            "stage_name": revision_info["stage_name"],
            "cycle_count": revision_info["cycle_status"]["cycle_count"],
            "status": status
        }
    
    def get_active_revisions(self) -> List[Dict[str, Any]]:
        """
        Get information about all active revisions.
        
        Returns:
            List of dictionaries with revision information
        """
        result = []
        for key, info in self.in_progress_revisions.items():
            result.append({
                "revision_key": key,
                "agent_id": info["agent_id"],
                "stage_name": info["stage_name"],
                "artifact_type": info["artifact_type"],
                "cycle_count": info["cycle_status"]["cycle_count"],
                "max_cycles": info["cycle_status"]["max_cycles"]
            })
        
        return result
