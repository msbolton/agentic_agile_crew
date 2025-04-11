"""
Human Review Manager for Agentic Agile Crew

This module manages human-in-the-loop review requests and responses,
allowing for human oversight at critical stages of the workflow.
It now includes feedback-driven agent refinement loops.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("human_review")

# Import feedback system components
from .feedback.parser import FeedbackParser
from .feedback.cycle import RevisionCycle
from .feedback.memory import FeedbackMemory
from .feedback.limiter import CycleLimiter

class HumanReviewRequest:
    """
    Represents a request for human review of an artifact produced by an agent.
    """
    def __init__(self, 
                agent_id: str, 
                stage_name: str, 
                artifact_type: str,
                content: Any, 
                context: Dict[str, Any] = None,
                callback: Callable = None):
        """
        Initialize a new human review request.
        
        Args:
            agent_id: ID of the agent that produced the artifact
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact (e.g., "requirements", "PRD")
            content: The actual content to be reviewed
            context: Additional context information
            callback: Function to call when review is complete
        """
        self.id = str(uuid.uuid4())
        self.agent_id = agent_id
        self.stage_name = stage_name
        self.artifact_type = artifact_type
        self.content = content
        self.context = context or {}
        self.status = "pending"
        self.feedback = ""
        self.callback = callback
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "stage_name": self.stage_name,
            "artifact_type": self.artifact_type,
            "content": self.content,
            "context": self.context,
            "status": self.status,
            "feedback": self.feedback,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanReviewRequest':
        """Create a HumanReviewRequest from a dictionary"""
        request = cls(
            agent_id=data["agent_id"],
            stage_name=data["stage_name"],
            artifact_type=data["artifact_type"],
            content=data["content"],
            context=data.get("context", {})
        )
        request.id = data["id"]
        request.status = data["status"]
        request.feedback = data["feedback"]
        request.timestamp = data["timestamp"]
        return request


class HumanReviewManager:
    """
    Manages human review requests and responses in the Agentic Agile Crew.
    Now supports feedback-driven agent refinement loops.
    """
    def __init__(self, storage_dir=".agentic_crew", max_revision_cycles=5):
        """
        Initialize the human review manager.
        
        Args:
            storage_dir: Directory to store persistent data
            max_revision_cycles: Maximum number of revision cycles allowed
        """
        self.storage_dir = storage_dir
        self._ensure_storage_exists()
        self.pending_reviews: List[HumanReviewRequest] = []
        self.completed_reviews: List[Dict[str, Any]] = []
        self.callbacks: Dict[str, Callable] = {}
        
        # Initialize feedback system components
        self.feedback_memory = FeedbackMemory(storage_dir=storage_dir)
        self.cycle_limiter = CycleLimiter(max_cycles=max_revision_cycles)
        self.revision_cycle = RevisionCycle(
            feedback_memory=self.feedback_memory,
            cycle_limiter=self.cycle_limiter
        )
        
        # Track revision requests
        self.revision_requests: Dict[str, Dict[str, Any]] = {}
        
        # Load saved reviews
        self._load_reviews()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created storage directory: {self.storage_dir}")
    
    def _load_reviews(self):
        """Load reviews from storage"""
        try:
            # Load pending reviews
            pending_path = os.path.join(self.storage_dir, "pending_reviews.json")
            if os.path.exists(pending_path):
                with open(pending_path, 'r') as f:
                    pending_data = json.load(f)
                    
                self.pending_reviews = [HumanReviewRequest.from_dict(item) for item in pending_data]
                logger.info(f"Loaded {len(self.pending_reviews)} pending reviews")
            
            # Load completed reviews
            completed_path = os.path.join(self.storage_dir, "completed_reviews.json")
            if os.path.exists(completed_path):
                with open(completed_path, 'r') as f:
                    self.completed_reviews = json.load(f)
                    
                logger.info(f"Loaded {len(self.completed_reviews)} completed reviews")
        except Exception as e:
            logger.error(f"Error loading reviews: {e}")
    
    def _save_pending_reviews(self):
        """Save pending reviews to storage"""
        try:
            path = os.path.join(self.storage_dir, "pending_reviews.json")
            serializable = [review.to_dict() for review in self.pending_reviews]
            with open(path, 'w') as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving pending reviews: {e}")
    
    def _save_completed_reviews(self):
        """Save completed reviews to storage"""
        try:
            path = os.path.join(self.storage_dir, "completed_reviews.json")
            with open(path, 'w') as f:
                json.dump(self.completed_reviews, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving completed reviews: {e}")
    
    def register_callback(self, review_id: str, callback: Callable):
        """
        Register a callback function for a specific review
        
        Args:
            review_id: The ID of the review request
            callback: Function to call when review is complete
        """
        self.callbacks[review_id] = callback
        logger.debug(f"Registered callback for review {review_id}")
    
    def request_review(self, request: HumanReviewRequest) -> str:
        """
        Submit artifact for human review and return request ID
        
        Args:
            request: The review request object
            
        Returns:
            The ID of the review request
        """
        # Store the callback separately
        if request.callback:
            self.callbacks[request.id] = request.callback
            request.callback = None  # Don't try to serialize the callback
        
        self.pending_reviews.append(request)
        self._save_pending_reviews()
        
        logger.info(f"New review requested: {request.stage_name} by {request.agent_id}")
        print(f"\n[!] New review requested: {request.stage_name} by {request.agent_id}")
        print(f"Run 'python cli.py list-reviews' to see pending reviews.\n")
        
        return request.id
    
    def get_pending_reviews(self) -> List[HumanReviewRequest]:
        """Get all pending reviews"""
        return self.pending_reviews
    
    def get_completed_reviews(self) -> List[Dict[str, Any]]:
        """Get all completed reviews"""
        return self.completed_reviews
    
    def get_review_by_id(self, review_id: str) -> Optional[HumanReviewRequest]:
        """Get a specific review by ID"""
        return next((r for r in self.pending_reviews if r.id == review_id), None)
    
    def submit_feedback(self, review_id: str, approved: bool, feedback: str) -> bool:
        """
        Process human feedback for a review request
        
        Args:
            review_id: The ID of the review request
            approved: Whether the review was approved
            feedback: Feedback text from the reviewer
            
        Returns:
            True if feedback was processed successfully, False otherwise
        """
        # Find the review request
        request = self.get_review_by_id(review_id)
        if not request:
            logger.error(f"Review request {review_id} not found")
            return False
            
        request.status = "approved" if approved else "rejected"
        request.feedback = feedback
        
        # Store a copy in completed reviews
        completed_review = request.to_dict()
        completed_review["completed_at"] = datetime.now().isoformat()
        self.completed_reviews.append(completed_review)
        
        # If rejected, start a revision cycle (unless it's a revision that's being rejected)
        revision_started = False
        if not approved and not review_id.startswith("revision_"):
            # Get the original workflow adapter from the context if available
            workflow_adapter = request.context.get("workflow_adapter")
            original_task = request.context.get("original_task")
            agent = request.context.get("agent")
            
            if workflow_adapter and original_task and agent:
                # Start a revision cycle
                try:
                    revision_started = self._start_revision_cycle(
                        request.id,
                        request.agent_id,
                        request.stage_name,
                        request.artifact_type,
                        request.content,
                        feedback,
                        agent,
                        original_task,
                        workflow_adapter
                    )
                    
                    if revision_started:
                        logger.info(f"Started revision cycle for {request.id}")
                    else:
                        logger.warning(f"Failed to start revision cycle for {request.id}")
                except Exception as e:
                    logger.error(f"Error starting revision cycle: {e}")
        
        # Execute callback if available and a revision wasn't started
        if not revision_started:
            callback = self.callbacks.get(review_id)
            if callback:
                try:
                    logger.info(f"Executing callback for review {review_id}")
                    callback(approved, feedback)
                    # Remove the callback after execution
                    del self.callbacks[review_id]
                except Exception as e:
                    logger.error(f"Error executing callback for review {review_id}: {e}")
        
        # Remove from pending
        self.pending_reviews.remove(request)
        
        # Save changes
        self._save_pending_reviews()
        self._save_completed_reviews()
        
        logger.info(f"Review {review_id} completed with status: {request.status}")
        return True
    
    def _start_revision_cycle(
        self,
        original_review_id: str,
        agent_id: str,
        stage_name: str,
        artifact_type: str,
        original_content: Any,
        feedback: str,
        agent: Any,
        original_task: Any,
        workflow_adapter: Any
    ) -> bool:
        """
        Start a revision cycle for rejected content.
        
        Args:
            original_review_id: ID of the original review
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact being revised
            original_content: Original content to be revised
            feedback: Feedback from the reviewer
            agent: The agent that will perform the revision
            original_task: The original task
            workflow_adapter: The workflow adapter
            
        Returns:
            True if revision cycle was started successfully
        """
        try:
            # Define callback for when revision is complete
            def on_revision_complete(revised_content: Any, status: str):
                # Create a new review request for the revised content
                revision_request = HumanReviewRequest(
                    agent_id=agent_id,
                    stage_name=f"{stage_name} (Revision)",
                    artifact_type=artifact_type,
                    content=revised_content,
                    context={
                        "original_review_id": original_review_id,
                        "workflow_adapter": workflow_adapter,
                        "original_task": original_task,
                        "agent": agent,
                        "revision": True,
                        "task_description": original_task.description
                    }
                )
                
                # Use a prefix to identify revision review requests
                revision_request.id = f"revision_{revision_request.id}"
                
                # Define callback for the revision review
                def on_revision_review_complete(approved: bool, feedback: str):
                    if approved:
                        logger.info(f"Revision approved for {stage_name}")
                        
                        # Reset cycle count since the revision was successful
                        self.cycle_limiter.reset(agent_id, stage_name)
                        
                        # Call the original callback that was registered for the original review
                        original_callback = self.callbacks.get(original_review_id)
                        if original_callback:
                            try:
                                logger.info(f"Executing callback for original review {original_review_id}")
                                original_callback(True, "Approved after revision")
                                # Remove the original callback
                                del self.callbacks[original_review_id]
                            except Exception as e:
                                logger.error(f"Error executing original callback: {e}")
                        
                        # Save artifact if integrated with artifact system
                        if hasattr(workflow_adapter, "artifact_manager") and workflow_adapter.artifact_manager:
                            try:
                                product_idea_name = workflow_adapter.product_idea_name
                                if product_idea_name:
                                    filepath = workflow_adapter.artifact_manager.save_artifact(
                                        product_idea_name,
                                        artifact_type,
                                        revised_content
                                    )
                                    logger.info(f"Saved revised artifact to {filepath}")
                            except Exception as e:
                                logger.error(f"Error saving revised artifact: {e}")
                        
                        # Handle JIRA integration if needed (similar to original workflow code)
                        if (hasattr(workflow_adapter, "jira_connector") and
                            workflow_adapter.jira_connector and 
                            workflow_adapter.jira_enabled and 
                            artifact_type == "JIRA epics and stories"):
                            try:
                                logger.info("Creating JIRA epics and stories from revision...")
                                results = workflow_adapter.jira_connector.create_epics_and_stories(revised_content)
                                if results["success"]:
                                    logger.info(f"Created {len(results.get('epics', []))} epics and {len(results.get('stories', []))} stories in JIRA")
                                else:
                                    logger.warning(f"Failed to create JIRA items: {results.get('error', 'Unknown error')}")
                            except Exception as e:
                                logger.error(f"Error creating JIRA items from revision: {e}")
                    else:
                        logger.info(f"Revision rejected for {stage_name} with feedback: {feedback}")
                        
                        # Check cycle limits before starting another revision
                        cycle_status = self.cycle_limiter.get_status(agent_id, stage_name)
                        
                        if cycle_status["limit_reached"]:
                            logger.warning(
                                f"Maximum revision cycles reached for {agent_id} in {stage_name}. "
                                f"Auto-approving to continue workflow."
                            )
                            
                            # Force approval to continue workflow
                            original_callback = self.callbacks.get(original_review_id)
                            if original_callback:
                                try:
                                    logger.info(f"Auto-approving after max revisions for {original_review_id}")
                                    original_callback(True, "Auto-approved after maximum revision cycles")
                                    # Remove the original callback
                                    del self.callbacks[original_review_id]
                                except Exception as e:
                                    logger.error(f"Error executing forced approval callback: {e}")
                        else:
                            # Start another revision cycle
                            self._start_revision_cycle(
                                original_review_id,
                                agent_id,
                                stage_name,
                                artifact_type,
                                revised_content,
                                feedback,
                                agent,
                                original_task,
                                workflow_adapter
                            )
                
                # Register the revision review request
                review_id = self.request_review(revision_request)
                self.register_callback(review_id, on_revision_review_complete)
                
                print(f"\n[!] Revised content sent for human review. ID: {review_id}")
                print(f"Run 'python cli.py review {review_id}' to review the revision.")
                
                logger.info(f"Revision complete and sent for review. ID: {review_id}")
            
            # Start the revision cycle
            revision_result = self.revision_cycle.start_revision(
                agent=agent,
                original_task=original_task,
                stage_name=stage_name,
                artifact_type=artifact_type,
                feedback=feedback,
                original_content=original_content,
                callback=on_revision_complete
            )
            
            # Store revision information
            revision_key = revision_result["revision_key"]
            self.revision_requests[revision_key] = {
                "original_review_id": original_review_id,
                "agent_id": agent_id,
                "stage_name": stage_name,
                "cycle_status": revision_result["cycle_status"]
            }
            
            # Execute the revision task
            try:
                print(f"\n[!] Starting revision cycle for {stage_name}...")
                
                # Execute the task and get the result
                revised_content = revision_result["task"].execute()
                
                # Complete the revision cycle
                self.revision_cycle.complete_revision(
                    revision_key=revision_key,
                    revised_content=revised_content
                )
                
                return True
            except Exception as e:
                logger.error(f"Error executing revision task: {e}")
                return False
        except Exception as e:
            logger.error(f"Error in revision cycle: {e}")
            return False
    
    def get_active_revisions(self) -> List[Dict[str, Any]]:
        """
        Get information about all active revisions.
        
        Returns:
            List of dictionaries with revision information
        """
        return self.revision_cycle.get_active_revisions()
