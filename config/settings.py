import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Authentication
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "False").lower() == "true"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Agent-specific OpenRouter models - all default to the main OPENROUTER_MODEL
OPENROUTER_BUSINESS_ANALYST_MODEL = os.getenv("OPENROUTER_BUSINESS_ANALYST_MODEL", OPENROUTER_MODEL)
OPENROUTER_PROJECT_MANAGER_MODEL = os.getenv("OPENROUTER_PROJECT_MANAGER_MODEL", OPENROUTER_MODEL)
OPENROUTER_ARCHITECT_MODEL = os.getenv("OPENROUTER_ARCHITECT_MODEL", OPENROUTER_MODEL)
OPENROUTER_PRODUCT_OWNER_MODEL = os.getenv("OPENROUTER_PRODUCT_OWNER_MODEL", OPENROUTER_MODEL)
OPENROUTER_SCRUM_MASTER_MODEL = os.getenv("OPENROUTER_SCRUM_MASTER_MODEL", OPENROUTER_MODEL)
OPENROUTER_DEVELOPER_MODEL = os.getenv("OPENROUTER_DEVELOPER_MODEL", OPENROUTER_MODEL)

# JIRA Configuration
JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "PROJ")

# CrewAI Configuration
CREW_VERBOSE = os.getenv("CREW_VERBOSE", "True").lower() == "true"

# Agent Configuration
AGENT_MEMORY = True  # Whether agents should remember previous interactions
AGENT_ALLOW_DELEGATION = True  # Whether agents can delegate tasks to other agents
