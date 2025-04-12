"""
Configuration package for Agentic Agile Crew
"""

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Import directly to use OpenAI

# Load environment variables from .env file
load_dotenv()

# Import settings
from .settings import (
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    USE_OPENROUTER,
    OPENROUTER_MODEL,
    OPENROUTER_BASE_URL,
    OPENROUTER_BUSINESS_ANALYST_MODEL,
    OPENROUTER_PROJECT_MANAGER_MODEL,
    OPENROUTER_ARCHITECT_MODEL,
    OPENROUTER_PRODUCT_OWNER_MODEL,
    OPENROUTER_SCRUM_MASTER_MODEL,
    OPENROUTER_DEVELOPER_MODEL
)

def get_llm_config(temperature=0.2, model=None):
    """
    Configure and return an LLM client
    
    Args:
        temperature (float): Controls randomness in responses. Higher values (e.g., 0.8) make output more random,
                           lower values (e.g., 0.2) make it more deterministic.
        model (str): Optional model name to use. If None, uses default model.
        
    Returns:
        A configured LLM instance
    """
    # Check if we should use OpenRouter
    if USE_OPENROUTER:
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable not set. "
                "Please add your OpenRouter API key to the .env file."
            )
        
        # Use ChatOpenAI with OpenRouter base URL
        openrouter_model = model or OPENROUTER_MODEL
        
        # Ensure the model name doesn't have unnecessary prefixes
        if openrouter_model.startswith("openrouter/"):
            openrouter_model = openrouter_model[len("openrouter/"):]
        
        # Set up OpenRouter-specific headers
        headers = {
            "HTTP-Referer": "https://agentic-agile-crew",  # Required by OpenRouter
            "X-Title": "Agentic Agile Crew"  # Optional: identifies your app
        }
        
        # OpenRouter requires specific configuration to work with OpenAI client
        # Strip any whitespace from the API key
        cleaned_api_key = OPENROUTER_API_KEY.strip() if OPENROUTER_API_KEY else ""
        
        print(f"Using OpenRouter with model: {openrouter_model}")
        
        # Save the original OpenAI API key if it exists
        original_openai_key = os.environ.get("OPENAI_API_KEY", "")
        original_openai_base = os.environ.get("OPENAI_API_BASE", "")
        
        # For OpenRouter, we need to set environment variables to force the OpenAI client
        # to use the correct endpoint and API key
        os.environ["OPENAI_API_KEY"] = cleaned_api_key
        os.environ["OPENAI_API_BASE"] = OPENROUTER_BASE_URL
        
        # Set up a cleanup function to restore original variables after use
        def cleanup_env_vars():
            if original_openai_key:
                os.environ["OPENAI_API_KEY"] = original_openai_key
            if original_openai_base:
                os.environ["OPENAI_API_BASE"] = original_openai_base
        
        # Import here to ensure we get a fresh instance with the correct environment variables
        from langchain_openai import ChatOpenAI as OpenRouterChat
        
        # For debugging purposes
        print(f"Environment variables for OpenAI client:")
        print(f"  OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY')[:5]}...")
        print(f"  OPENAI_API_BASE: {os.environ.get('OPENAI_API_BASE')}")
        
        # Create a direct OpenAI client to test the configuration
        try:
            # Import the OpenAI client
            import openai
            
            # Configure it directly
            openai_client = openai.OpenAI(
                api_key=cleaned_api_key,
                base_url=OPENROUTER_BASE_URL
            )
            
            # Test if it works with a simple completion
            print("Testing direct OpenAI client with OpenRouter...")
            test_response = openai_client.chat.completions.create(
                model=openrouter_model,
                messages=[{"role": "user", "content": "Hello, this is a test"}],
                max_tokens=5
            )
            print(f"Test successful! Response: {test_response.choices[0].message.content}")
        except Exception as e:
            print(f"Error testing direct OpenAI client: {e}")
            
        # Option 1: Create an instance using environment variables
        # chatbot = OpenRouterChat(
        #     model=openrouter_model,
        #     temperature=temperature,
        #     default_headers=headers
        # )
        
        # Option 2: Create one with direct configuration (more reliable)
        chatbot = OpenRouterChat(
            api_key=cleaned_api_key,
            base_url=OPENROUTER_BASE_URL,
            model=openrouter_model,
            temperature=temperature,
            default_headers=headers
        )
        
        return chatbot
    else:
        # Check for OpenAI API key
        if not OPENAI_API_KEY:
            # Provide clear error message
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please add your OpenAI API key to the .env file."
            )
        
        # Default to GPT-4 if available, otherwise GPT-3.5
        openai_model = model or "gpt-4-turbo"
        
        # Simple direct approach - use OpenAI directly
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=openai_model,
            temperature=temperature
        )

def get_agent_llm(agent_type):
    """
    Get the appropriate LLM configuration for a specific agent type
    
    Args:
        agent_type (str): The type of agent ("architect", "developer", etc.)
        
    Returns:
        A configured LLM client with appropriate temperature settings
    """
    # Normalize agent type name
    agent_type = agent_type.lower()
    
    # Define temperature settings for different agent types
    temperature_settings = {
        "architect": 0.3,        # Higher temperature for more creative solutions
        "developer": 0.1,        # Lower temperature for precise code generation
        "business_analyst": 0.2, # Balanced for requirement analysis
        "project_manager": 0.2,  # Balanced for PRD creation
        "product_owner": 0.2,    # Balanced for task breakdown
        "scrum_master": 0.2      # Balanced for story creation
    }
    
    # Get the appropriate temperature (default to 0.2 if not specified)
    temperature = temperature_settings.get(agent_type, 0.2)
    
    # If using OpenRouter, select the appropriate model based on agent type
    if USE_OPENROUTER:
        # Map agent types to their corresponding model variables
        model_mapping = {
            "business_analyst": OPENROUTER_BUSINESS_ANALYST_MODEL,
            "project_manager": OPENROUTER_PROJECT_MANAGER_MODEL,
            "architect": OPENROUTER_ARCHITECT_MODEL,
            "product_owner": OPENROUTER_PRODUCT_OWNER_MODEL,
            "scrum_master": OPENROUTER_SCRUM_MASTER_MODEL,
            "developer": OPENROUTER_DEVELOPER_MODEL
        }
        
        # Get the appropriate model or fall back to the default
        model = model_mapping.get(agent_type, OPENROUTER_MODEL)
        
        # Log which model is being used
        if model == OPENROUTER_MODEL:
            print(f"Using default model {model} for {agent_type} agent (temperature: {temperature})")
        else:
            print(f"Using custom model {model} for {agent_type} agent (temperature: {temperature})")
        return get_llm_config(temperature=temperature, model=model)
    else:
        # When not using OpenRouter, just use the temperature setting
        return get_llm_config(temperature=temperature)
