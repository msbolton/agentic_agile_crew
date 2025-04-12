"""
Unit tests for OpenRouter integration
"""
import os
import unittest
from unittest.mock import patch, MagicMock

# Import the functions to test
from config import get_llm_config, get_agent_llm
from langchain_openai import ChatOpenAI


class TestOpenRouterIntegration(unittest.TestCase):
    """Tests for OpenRouter LLM integration"""
    
    @patch('config.USE_OPENROUTER', True)
    @patch('config.OPENROUTER_API_KEY', 'test-key')
    @patch('config.OPENROUTER_MODEL', 'test/model')
    @patch('langchain_openai.ChatOpenAI')
    def test_get_llm_config_with_openrouter(self, mock_chat_openai):
        """Test that get_llm_config correctly uses OpenRouter when enabled"""
        # Configure the mock
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        
        # Call the function
        result = get_llm_config(temperature=0.5)
        
        # Assert that ChatOpenAI was correctly initialized with OpenRouter config
        mock_chat_openai.assert_called_once()
        args, kwargs = mock_chat_openai.call_args
        
        # Check that the correct model was used
        self.assertEqual(kwargs['model'], 'test/model')
        
        # Check that the API key was passed
        self.assertEqual(kwargs['api_key'], 'test-key')
        
        # Check that the temperature was set correctly
        self.assertEqual(kwargs['temperature'], 0.5)
        
        # Check that the base URL was set correctly
        self.assertIn('base_url', kwargs)
    
    @patch('config.USE_OPENROUTER', True)
    @patch('config.OPENROUTER_API_KEY', 'test-key')
    @patch('config.OPENROUTER_ARCHITECT_MODEL', 'anthropic/test-architect-model')
    @patch('langchain_openai.ChatOpenAI')
    def test_get_agent_llm_for_architect(self, mock_chat_openai):
        """Test that get_agent_llm returns the correct model for the architect role"""
        # Configure the mocks
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        
        # Call the function
        result = get_agent_llm('architect')
        
        # Assert that ChatOpenAI was correctly initialized with the architect model
        mock_chat_openai.assert_called_once()
        args, kwargs = mock_chat_openai.call_args
        
        # Check that the architect-specific model was used
        self.assertEqual(kwargs['model'], 'anthropic/test-architect-model')
        
        # Check that the temperature was set to 0.3 for the architect
        self.assertEqual(kwargs['temperature'], 0.3)
    
    @patch('config.USE_OPENROUTER', True)
    @patch('config.OPENROUTER_API_KEY', 'test-key')
    @patch('config.OPENROUTER_DEVELOPER_MODEL', 'meta-llama/test-developer-model')
    @patch('langchain_openai.ChatOpenAI')
    def test_get_agent_llm_for_developer(self, mock_chat_openai):
        """Test that get_agent_llm returns the correct model for the developer role"""
        # Configure the mocks
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        
        # Call the function
        result = get_agent_llm('developer')
        
        # Assert that ChatOpenAI was correctly initialized with the developer model
        mock_chat_openai.assert_called_once()
        args, kwargs = mock_chat_openai.call_args
        
        # Check that the developer-specific model was used
        self.assertEqual(kwargs['model'], 'meta-llama/test-developer-model')
        
        # Check that the temperature was set to 0.1 for the developer
        self.assertEqual(kwargs['temperature'], 0.1)
    
    @patch('config.USE_OPENROUTER', True)
    @patch('config.OPENROUTER_API_KEY', 'test-key')
    @patch('config.OPENROUTER_BUSINESS_ANALYST_MODEL', 'anthropic/test-ba-model')
    @patch('langchain_openai.ChatOpenAI')
    def test_get_agent_llm_for_business_analyst(self, mock_chat_openai):
        """Test that get_agent_llm returns the correct model for the business analyst role"""
        # Configure the mocks
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        
        # Call the function
        result = get_agent_llm('business_analyst')
        
        # Assert that ChatOpenAI was correctly initialized with the business analyst model
        mock_chat_openai.assert_called_once()
        args, kwargs = mock_chat_openai.call_args
        
        # Check that the business analyst model was used
        self.assertEqual(kwargs['model'], 'anthropic/test-ba-model')
        
        # Check that the temperature was set to 0.2 for the business analyst
        self.assertEqual(kwargs['temperature'], 0.2)


    @patch('config.USE_OPENROUTER', True)
    @patch('config.OPENROUTER_API_KEY', 'test-key')
    @patch('config.OPENROUTER_MODEL', 'default-test-model')
    @patch('langchain_openai.ChatOpenAI')
    def test_get_agent_llm_for_unknown_agent(self, mock_chat_openai):
        """Test that get_agent_llm returns the default model for unknown agent types"""
        # Configure the mocks
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        
        # Call the function with an unknown agent type
        result = get_agent_llm('unknown_agent_type')
        
        # Assert that ChatOpenAI was correctly initialized with the default model
        mock_chat_openai.assert_called_once()
        args, kwargs = mock_chat_openai.call_args
        
        # Check that the default model was used
        self.assertEqual(kwargs['model'], 'default-test-model')
        
        # Check that the temperature was set to default (0.2)
        self.assertEqual(kwargs['temperature'], 0.2)

if __name__ == '__main__':
    unittest.main()
