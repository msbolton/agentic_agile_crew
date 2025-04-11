"""
Human Review Manager for Agentic Agile Crew

This module manages human-in-the-loop review requests and responses,
allowing for human oversight at critical stages of the workflow.
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
    """
    def __init__(self, storage_dir=".agentic_crew"):
        """
        Initialize the human review manager.
        
        Args:
            storage_dir: Directory to store persistent data
        """
        self.storage_dir = storage_dir
        self._ensure_storage_exists()
        self.pending_reviews: List[HumanReviewRequest] = []
        self.completed_reviews: List[Dict[str, Any]] = []
        self.callbacks: Dict[str, Callable] = {}
        
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
        
        # Execute callback if available
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
