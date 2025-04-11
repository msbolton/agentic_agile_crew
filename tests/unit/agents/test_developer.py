"""
Unit tests for the Developer agent
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
from src.agents.developer import create_developer


def test_create_developer_without_tools():
    """Test creating a developer agent without tools"""
    # Arrange
    agent_mock = MagicMock()
    
    with patch('src.agents.developer.Agent', return_value=agent_mock) as mock_agent_class:
        with patch('src.agents.developer.ChatOpenAI') as mock_chat_openai:
            # Act
            agent = create_developer()
            
            # Assert
            mock_agent_class.assert_called_once()
            
            # Check expected parameters
            args, kwargs = mock_agent_class.call_args
            assert kwargs['role'] == "Software Developer"
            assert "Implement user stories" in kwargs['goal']
            assert kwargs['verbose'] is True
            assert kwargs['tools'] == []
            
            # Check LLM temperature
            mock_chat_openai.assert_called_once()
            llm_args, llm_kwargs = mock_chat_openai.call_args
            assert llm_kwargs['temperature'] == max(0.1, 0.2 - 0.1)  # Lower temperature


def test_create_developer_with_tools():
    """Test creating a developer agent with tools"""
    # Arrange
    agent_mock = MagicMock()
    tools = [MagicMock(), MagicMock()]
    
    with patch('src.agents.developer.Agent', return_value=agent_mock) as mock_agent_class:
        with patch('src.agents.developer.ChatOpenAI'):
            # Act
            agent = create_developer(tools=tools)
            
            # Assert
            mock_agent_class.assert_called_once()
            
            # Check that the agent was created with the correct parameters
            args, kwargs = mock_agent_class.call_args
            assert kwargs['tools'] == tools
