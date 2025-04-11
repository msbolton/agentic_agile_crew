"""
Unit tests for the Business Analyst agent
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Mock the imported modules
sys.modules['crewai'] = MagicMock()
sys.modules['langchain_openai'] = MagicMock()
sys.modules['config.settings'] = MagicMock(
    LLM_MODEL="gpt-4",
    LLM_TEMPERATURE=0.2,
    AGENT_MEMORY=True,
    AGENT_ALLOW_DELEGATION=True
)

# Now import the module under test
from src.agents.business_analyst import create_business_analyst


def test_create_business_analyst_without_tools():
    """Test creating a business analyst agent without tools"""
    # Arrange
    agent_mock = MagicMock()
    
    with patch('src.agents.business_analyst.Agent', return_value=agent_mock) as mock_agent_class:
        # Act
        agent = create_business_analyst()
        
        # Assert
        mock_agent_class.assert_called_once()
        
        # Check expected parameters
        args, kwargs = mock_agent_class.call_args
        assert kwargs['role'] == "Business Analyst"
        assert "Refine product ideas" in kwargs['goal']
        assert kwargs['verbose'] is True
        assert kwargs['tools'] == []


def test_create_business_analyst_with_tools():
    """Test creating a business analyst agent with tools"""
    # Arrange
    agent_mock = MagicMock()
    tools = [MagicMock(), MagicMock()]
    
    with patch('src.agents.business_analyst.Agent', return_value=agent_mock) as mock_agent_class:
        # Act
        agent = create_business_analyst(tools=tools)
        
        # Assert
        mock_agent_class.assert_called_once()
        
        # Check that the agent was created with the correct parameters
        args, kwargs = mock_agent_class.call_args
        assert kwargs['tools'] == tools
