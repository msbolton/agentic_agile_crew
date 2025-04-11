# Agentic Agile Crew

An intelligent agentic development team built with CrewAI that simulates an agile software development workflow, now with human-in-the-loop capabilities.

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

## Usage

### Standard Mode

1. Define your product idea in the `examples/example_product_idea.md` file or provide it when prompted
2. The agents will collaborate to analyze, plan, and implement your software project
3. Check your JIRA instance for created epics and user stories

### Human-in-the-Loop Mode

The system now supports human review at each stage of the workflow. This allows you to:
- Review and approve/reject the output of each agent
- Provide feedback for improvements
- Ensure quality and correctness at each step

To use human-in-the-loop mode:

1. Start a project with a product idea file:
   ```
   python cli.py start examples/example_product_idea.md
   ```

2. List pending reviews:
   ```
   python cli.py list-reviews
   ```

3. Review a specific item:
   ```
   python cli.py review <review_id>
   ```

4. Check project status:
   ```
   python cli.py status
   ```

5. View completed reviews:
   ```
   python cli.py list-completed
   ```

You can also run the main application with human review enabled:
```
python main.py --with-human-review
```

## Configuration

Edit the settings in `config/settings.py` to customize:

- LLM settings (model, temperature, etc.)
- JIRA connection details
- Agent parameters

## Human Review CLI Commands

| Command | Description |
|---------|-------------|
| `start <file> [--with-jira]` | Start a new project with a product idea file. Optionally enable JIRA integration |
| `list-reviews` | List all pending review items |
| `review <id>` | Review a specific item by its ID |
| `status` | Show the current project status |
| `list-completed` | List all completed reviews |

## Artifact Management

The system now organizes all agent outputs into artifacts that are saved for future reference. Artifacts are organized by project name and categorized by type.

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

| Command | Description |
|---------|-------------|
| `list-artifacts [project_name]` | List all artifacts or artifacts for a specific project |
| `view-artifact <project_name> <artifact_name>` | View the content of a specific artifact |
| `export-artifacts <project_name> <export_dir>` | Export all artifacts for a project to a directory |

### JIRA Integration

When JIRA integration is enabled with `--with-jira`, the system will automatically create epics and stories in JIRA based on the "JIRA epics and stories" artifact. To use this feature, you need to set the following environment variables:

- `JIRA_URL`: URL of your JIRA instance
- `JIRA_USER`: Your JIRA username or email
- `JIRA_API_TOKEN`: Your JIRA API token
- `JIRA_PROJECT_KEY`: The key of the JIRA project
