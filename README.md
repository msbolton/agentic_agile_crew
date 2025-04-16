# Agentic Agile Crew

An intelligent agentic development team built with CrewAI that simulates an agile software development workflow.

## Overview

This application uses CrewAI to create an automated software development workflow with specialized agents for each role:

- **Business Analyst**: Refines product ideas into requirements
- **Project Manager**: Creates comprehensive PRDs with clarifying questions
- **Architect**: Designs complete technical architecture with reasoning
- **Product Owner**: Creates granular, sequenced task lists
- **Scrum Master**: Creates epics and user stories in JIRA
- **Developer**: Implements user stories according to specifications

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your API keys
4. Run the application: `python main.py`

### LLM Configuration

The application supports two LLM providers:

#### OpenAI (Default)

1. Sign up for an account at [OpenAI](https://platform.openai.com/)
2. Generate an API key from the [API keys page](https://platform.openai.com/api-keys)
3. Set the `OPENAI_API_KEY` variable in your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

#### OpenRouter (Alternative)

You can also use [OpenRouter](https://openrouter.ai/) to access a variety of models from different providers:

1. Sign up for an account at [OpenRouter](https://openrouter.ai/)
2. Generate an API key from the dashboard
3. Set the following variables in your `.env` file:
   ```
   # Basic OpenRouter Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   USE_OPENROUTER=true
   OPENROUTER_MODEL=anthropic/claude-3-haiku  # Default model for all agents
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   
   # Optional: Agent-specific models (all will fallback to OPENROUTER_MODEL if not set)
   OPENROUTER_BUSINESS_ANALYST_MODEL=anthropic/claude-3-5-sonnet
   OPENROUTER_PROJECT_MANAGER_MODEL=anthropic/claude-3-5-sonnet
   OPENROUTER_ARCHITECT_MODEL=anthropic/claude-3-opus
   OPENROUTER_PRODUCT_OWNER_MODEL=anthropic/claude-3-5-sonnet
   OPENROUTER_SCRUM_MASTER_MODEL=openai/gpt-4o
   OPENROUTER_DEVELOPER_MODEL=meta-llama/codellama-70b-instruct
   ```

To enable OpenRouter from the command line, use the `--with-openrouter` flag:
```
python main.py --with-openrouter
```

The system uses different temperature settings for different agent roles:
- **Architect** (0.3): Higher temperature for more creative solutions
- **Developer** (0.1): Lower temperature for precise code generation
- **Other roles** (0.2): Balanced temperature for standard tasks

By default without OpenRouter, the system will use the GPT-4 model for all agents to ensure high-quality outputs across the entire development workflow.

## Usage

### Using the Main Application

1. Define your product idea in the `examples/example_product_idea.md` file or provide it when prompted
2. The agents will collaborate to analyze, plan, and implement your software project
3. Check your JIRA instance for created epics and user stories

You can run the application with various options:

```bash
# Run with the default configuration
python main.py

# Provide a product idea directly
python main.py --idea "Build a task management app with AI assistance"

# Provide a product idea file
python main.py --idea-file examples/example_product_idea.md

# Enable JIRA integration
python main.py --with-jira

# Use OpenRouter instead of OpenAI
python main.py --with-openrouter
```

### Using OpenRouter

To use OpenRouter instead of OpenAI:

1. Ensure you have set up the OpenRouter API key in your `.env` file
2. Run the application with the OpenRouter flag:
   ```
   python main.py --with-openrouter
   ```

3. You can configure models for each agent type in your `.env` file:
   
   ```
   # Set a default model for all agents
   OPENROUTER_MODEL=anthropic/claude-3-haiku
   
   # Then override specific agents as needed
   OPENROUTER_ARCHITECT_MODEL=anthropic/claude-3-opus
   OPENROUTER_DEVELOPER_MODEL=meta-llama/codellama-70b-instruct
   ```
   
   Each agent's model will fall back to the default `OPENROUTER_MODEL` if not explicitly set. This allows you to maintain a consistent model across most agents while optimizing specific roles with specialized models.

## Configuration

Edit the settings in `config/settings.py` to customize:

- LLM settings (model, temperature, etc.)
- JIRA connection details
- Agent parameters

## Artifact Management

The system organizes all agent outputs into artifacts that are saved for future reference. Artifacts are organized by project name and categorized by type.

### Artifact Directory Structure

```
artifacts/
├── smart_task_manager_app/              # Sanitized product name
│   ├── business_requirements.md         # Business Analyst output
│   ├── prd_document.md                  # Project Manager output
│   ├── architecture_document.md         # Architect output
│   ├── task_list.md                     # Product Owner output
│   ├── jira_stories.md                  # Scrum Master output
│   └── implementation_code.md           # Developer output
└── [other_project_name]/
    └── ...
```

### Artifact CLI Commands

The CLI provides commands for working with artifacts:

```bash
# Start a new project with a product idea file
python cli.py start examples/example_product_idea.md

# List all projects with artifacts
python cli.py list-artifacts

# List artifacts for a specific project
python cli.py list-artifacts smart_task_manager_app

# View the content of a specific artifact
python cli.py view-artifact smart_task_manager_app business_requirements.md

# Export all artifacts for a project to a directory
python cli.py export-artifacts smart_task_manager_app ./export
```

### JIRA Integration

When JIRA integration is enabled with `--with-jira`, the system will automatically create epics and stories in JIRA based on the "JIRA epics and stories" artifact. To use this feature, you need to set the following environment variables:

- `JIRA_URL`: URL of your JIRA instance
- `JIRA_USER`: Your JIRA username or email
- `JIRA_API_TOKEN`: Your JIRA API token
- `JIRA_PROJECT_KEY`: The key of the JIRA project
