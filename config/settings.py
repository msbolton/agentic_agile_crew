import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Authentication
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

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
