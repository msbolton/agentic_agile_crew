"""
Pytest configuration and fixtures
"""

import pytest
import sys
from unittest.mock import MagicMock

# Mock the external dependencies
sys.modules['crewai'] = MagicMock()
sys.modules['langchain_openai'] = MagicMock()


@pytest.fixture
def mock_agent():
    """Mock Agent to avoid CrewAI initialization during testing"""
    agent_mock = MagicMock()
    agent_mock.name = "MockAgent"
    
    agent_class_mock = MagicMock(return_value=agent_mock)
    
    return agent_class_mock


@pytest.fixture
def sample_tools():
    """Sample tools for testing"""
    tool1 = MagicMock()
    tool1.name = "sample_tool_1"
    
    tool2 = MagicMock()
    tool2.name = "sample_tool_2"
    
    return [tool1, tool2]
