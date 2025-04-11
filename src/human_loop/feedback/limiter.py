"""
Cycle Limiter for the Human-in-the-Loop review process.

This module prevents infinite revision cycles by setting maximum
iterations and tracking cycle metrics.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("human_review.cycle_limiter")

class CycleLimiter:
    """
    Prevents infinite revision cycles by enforcing limits on revisions.
    """
    
    def __init__(self, max_cycles=5, auto_approve_after_max=True):
        """
        Initialize the cycle limiter.
        
        Args:
            max_cycles: Maximum number of revision cycles allowed
            auto_approve_after_max: Whether to auto-approve after max cycles
        """
        self.max_cycles = max_cycles
        self.auto_approve_after_max = auto_approve_after_max
        self.cycle_counts = {}
    
    def _get_key(self, agent_id: str, stage_name: str) -> str:
        """Generate a unique key for tracking cycles"""
        return f"{agent_id}_{stage_name}"
    
    def track_cycle(self, agent_id: str, stage_name: str) -> Dict[str, Any]:
        """
        Track a revision cycle and check if limits have been reached.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            
        Returns:
            Dictionary with cycle information
        """
        key = self._get_key(agent_id, stage_name)
        
        if key not in self.cycle_counts:
            self.cycle_counts[key] = 0
        
        self.cycle_counts[key] += 1
        current_count = self.cycle_counts[key]
        
        result = {
            "cycle_count": current_count,
            "max_cycles": self.max_cycles,
            "limit_reached": current_count >= self.max_cycles,
            "auto_approve": self.auto_approve_after_max and current_count >= self.max_cycles
        }
        
        if result["limit_reached"]:
            logger.warning(
                f"Revision cycle limit reached for {agent_id} in {stage_name}. "
                f"Count: {current_count}/{self.max_cycles}"
            )
            
            if result["auto_approve"]:
                logger.info(
                    f"Auto-approving revision for {agent_id} in {stage_name} "
                    f"after reaching maximum cycles"
                )
        
        return result
    
    def reset(self, agent_id: str, stage_name: str):
        """
        Reset the cycle count for an agent/stage.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
        """
        key = self._get_key(agent_id, stage_name)
        if key in self.cycle_counts:
            logger.info(f"Resetting cycle count for {agent_id} in {stage_name}")
            del self.cycle_counts[key]
    
    def get_status(self, agent_id: str, stage_name: str) -> Dict[str, Any]:
        """
        Get current cycle status.
        
        Args:
            agent_id: ID of the agent
            stage_name: Name of the workflow stage
            
        Returns:
            Dictionary with cycle status
        """
        key = self._get_key(agent_id, stage_name)
        current_count = self.cycle_counts.get(key, 0)
        
        return {
            "cycle_count": current_count,
            "max_cycles": self.max_cycles,
            "remaining_cycles": max(0, self.max_cycles - current_count),
            "limit_reached": current_count >= self.max_cycles
        }
