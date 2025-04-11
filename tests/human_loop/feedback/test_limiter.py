"""
Unit tests for the CycleLimiter module
"""

import pytest
from src.human_loop.feedback.limiter import CycleLimiter

class TestCycleLimiter:
    """
    Test cases for the CycleLimiter class
    """
    
    def test_initialization(self):
        """Test initializing a cycle limiter"""
        limiter = CycleLimiter(max_cycles=3, auto_approve_after_max=True)
        
        assert limiter.max_cycles == 3
        assert limiter.auto_approve_after_max is True
        assert limiter.cycle_counts == {}
    
    def test_get_key(self):
        """Test key generation for tracking cycles"""
        limiter = CycleLimiter()
        
        key = limiter._get_key("agent1", "stage1")
        assert key == "agent1_stage1"
    
    def test_track_cycle_first_cycle(self):
        """Test tracking a cycle for the first time"""
        limiter = CycleLimiter(max_cycles=3)
        
        result = limiter.track_cycle("agent1", "stage1")
        
        assert "agent1_stage1" in limiter.cycle_counts
        assert limiter.cycle_counts["agent1_stage1"] == 1
        
        assert result["cycle_count"] == 1
        assert result["max_cycles"] == 3
        assert result["limit_reached"] is False
        assert result["auto_approve"] is False
    
    def test_track_cycle_multiple_cycles(self):
        """Test tracking multiple cycles"""
        limiter = CycleLimiter(max_cycles=3)
        
        # First cycle
        limiter.track_cycle("agent1", "stage1")
        
        # Second cycle
        result = limiter.track_cycle("agent1", "stage1")
        
        assert limiter.cycle_counts["agent1_stage1"] == 2
        assert result["cycle_count"] == 2
        assert result["limit_reached"] is False
        
        # Third cycle
        result = limiter.track_cycle("agent1", "stage1")
        
        assert limiter.cycle_counts["agent1_stage1"] == 3
        assert result["cycle_count"] == 3
        assert result["limit_reached"] is True
        assert result["auto_approve"] is True  # Default is True
    
    def test_track_cycle_with_auto_approve_false(self):
        """Test tracking cycles with auto-approve disabled"""
        limiter = CycleLimiter(max_cycles=2, auto_approve_after_max=False)
        
        # First cycle
        limiter.track_cycle("agent1", "stage1")
        
        # Second cycle (limit reached)
        result = limiter.track_cycle("agent1", "stage1")
        
        assert result["limit_reached"] is True
        assert result["auto_approve"] is False  # Auto-approve disabled
    
    def test_track_cycle_different_agents(self):
        """Test tracking cycles for different agents/stages"""
        limiter = CycleLimiter(max_cycles=3)
        
        # Track different agent/stage combinations
        limiter.track_cycle("agent1", "stage1")
        limiter.track_cycle("agent1", "stage1")
        limiter.track_cycle("agent2", "stage1")
        limiter.track_cycle("agent1", "stage2")
        
        assert limiter.cycle_counts["agent1_stage1"] == 2
        assert limiter.cycle_counts["agent2_stage1"] == 1
        assert limiter.cycle_counts["agent1_stage2"] == 1
    
    def test_reset(self):
        """Test resetting the cycle count"""
        limiter = CycleLimiter()
        
        # Add some cycles
        limiter.track_cycle("agent1", "stage1")
        limiter.track_cycle("agent1", "stage1")
        limiter.track_cycle("agent2", "stage2")
        
        # Reset one agent/stage
        limiter.reset("agent1", "stage1")
        
        assert "agent1_stage1" not in limiter.cycle_counts
        assert "agent2_stage2" in limiter.cycle_counts
        
        # Reset non-existent key (should not error)
        limiter.reset("unknown", "unknown")
    
    def test_get_status_no_cycles(self):
        """Test getting status with no previous cycles"""
        limiter = CycleLimiter(max_cycles=5)
        
        status = limiter.get_status("agent1", "stage1")
        
        assert status["cycle_count"] == 0
        assert status["max_cycles"] == 5
        assert status["remaining_cycles"] == 5
        assert status["limit_reached"] is False
    
    def test_get_status_with_cycles(self):
        """Test getting status with existing cycles"""
        limiter = CycleLimiter(max_cycles=3)
        
        # Add cycles
        limiter.track_cycle("agent1", "stage1")
        limiter.track_cycle("agent1", "stage1")
        
        status = limiter.get_status("agent1", "stage1")
        
        assert status["cycle_count"] == 2
        assert status["max_cycles"] == 3
        assert status["remaining_cycles"] == 1
        assert status["limit_reached"] is False
    
    def test_get_status_limit_reached(self):
        """Test getting status when limit is reached"""
        limiter = CycleLimiter(max_cycles=2)
        
        # Add cycles to reach limit
        limiter.track_cycle("agent1", "stage1")
        limiter.track_cycle("agent1", "stage1")
        
        status = limiter.get_status("agent1", "stage1")
        
        assert status["cycle_count"] == 2
        assert status["remaining_cycles"] == 0
        assert status["limit_reached"] is True
    
    def test_get_status_after_reset(self):
        """Test getting status after reset"""
        limiter = CycleLimiter()
        
        # Add cycles
        limiter.track_cycle("agent1", "stage1")
        
        # Reset
        limiter.reset("agent1", "stage1")
        
        status = limiter.get_status("agent1", "stage1")
        
        assert status["cycle_count"] == 0
        assert status["remaining_cycles"] == limiter.max_cycles
        assert status["limit_reached"] is False
