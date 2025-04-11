"""
Feedback Memory for the Human-in-the-Loop review process.

This module enables agents to remember previous feedback and revisions
across multiple review cycles.
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

class RevisionHistory:
    """
    Records the history of revisions for a particular artifact.
    """
    def __init__(self, agent_id: str, stage_name: str, artifact_type: str):
        """
        Initialize a revision history.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact (e.g., "requirements", "PRD")
        """
        self.agent_id = agent_id
        self.stage_name = stage_name
        self.artifact_type = artifact_type
        self.revisions = []
    
    def add_revision(self, content: Any, feedback: str, status: str) -> int:
        """
        Add a new revision to the history.
        
        Args:
            content: The content of the revision
            feedback: Feedback provided for this revision
            status: Status of the revision (approved/rejected)
            
        Returns:
            The revision number
        """
        revision = {
            "version": len(self.revisions) + 1,
            "content": content,
            "feedback": feedback,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        self.revisions.append(revision)
        return revision["version"]
    
    def get_latest_revision(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest revision.
        
        Returns:
            The latest revision or None if no revisions exist
        """
        if not self.revisions:
            return None
        
        return self.revisions[-1]
    
    def get_revision(self, version: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific revision.
        
        Args:
            version: The revision version number
            
        Returns:
            The revision or None if not found
        """
        if version < 1 or version > len(self.revisions):
            return None
        
        return self.revisions[version - 1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "agent_id": self.agent_id,
            "stage_name": self.stage_name,
            "artifact_type": self.artifact_type,
            "revisions": self.revisions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RevisionHistory':
        """Create a RevisionHistory from a dictionary"""
        history = cls(
            agent_id=data["agent_id"],
            stage_name=data["stage_name"],
            artifact_type=data["artifact_type"]
        )
        history.revisions = data["revisions"]
        return history


class FeedbackMemory:
    """
    Memory system for storing revision history and feedback across multiple review cycles.
    """
    
    def __init__(self, storage_dir=".agentic_crew"):
        """
        Initialize the feedback memory.
        
        Args:
            storage_dir: Directory to store persistent data
        """
        self.storage_dir = storage_dir
        self._memory_file = os.path.join(storage_dir, "revision_history.json")
        self._histories: Dict[str, RevisionHistory] = {}
        
        # Create storage dir if needed
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        # Load existing histories
        self._load_histories()
    
    def _load_histories(self):
        """Load revision histories from storage"""
        if os.path.exists(self._memory_file):
            try:
                with open(self._memory_file, 'r') as f:
                    data = json.load(f)
                
                for key, history_data in data.items():
                    self._histories[key] = RevisionHistory.from_dict(history_data)
            except Exception as e:
                print(f"Error loading revision histories: {e}")
    
    def _save_histories(self):
        """Save revision histories to storage"""
        try:
            serializable = {k: v.to_dict() for k, v in self._histories.items()}
            with open(self._memory_file, 'w') as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            print(f"Error saving revision histories: {e}")
    
    def _get_key(self, agent_id: str, stage_name: str) -> str:
        """Generate a unique key for a history"""
        return f"{agent_id}_{stage_name}"
    
    def get_history(self, agent_id: str, stage_name: str) -> RevisionHistory:
        """
        Get the revision history for an agent/stage combination.
        Creates a new history if one doesn't exist.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            
        Returns:
            The revision history
        """
        key = self._get_key(agent_id, stage_name)
        
        if key not in self._histories:
            # Create a new history
            return RevisionHistory(agent_id, stage_name, "unknown")
        
        return self._histories[key]
    
    def record_revision(self, agent_id: str, stage_name: str, artifact_type: str, 
                      content: Any, feedback: str, status: str) -> int:
        """
        Record a new revision.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            artifact_type: Type of artifact being produced
            content: The content of the revision
            feedback: Feedback provided for this revision
            status: Status of the revision (approved/rejected)
            
        Returns:
            The revision number
        """
        key = self._get_key(agent_id, stage_name)
        
        if key not in self._histories:
            self._histories[key] = RevisionHistory(agent_id, stage_name, artifact_type)
        else:
            # Update artifact type in case it changed
            self._histories[key].artifact_type = artifact_type
        
        version = self._histories[key].add_revision(content, feedback, status)
        self._save_histories()
        
        return version
    
    def get_revision_context(self, agent_id: str, stage_name: str) -> Dict[str, Any]:
        """
        Get context for a new revision, including previous versions and feedback.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            
        Returns:
            Dictionary with context information
        """
        history = self.get_history(agent_id, stage_name)
        latest = history.get_latest_revision()
        
        context = {
            "revision_count": len(history.revisions),
            "previous_feedback": []
        }
        
        # Add the latest content if available
        if latest:
            context["previous_content"] = latest.get("content")
            
            # Add feedback from all previous revisions
            for revision in history.revisions:
                feedback = revision.get("feedback")
                if feedback:
                    context["previous_feedback"].append({
                        "version": revision["version"],
                        "feedback": feedback,
                        "status": revision["status"]
                    })
        
        return context
