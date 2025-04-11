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

## Usage

1. Define your product idea in the `examples/example_product_idea.md` file or provide it when prompted
2. The agents will collaborate to analyze, plan, and implement your software project
3. Check your JIRA instance for created epics and user stories

## Configuration

Edit the settings in `config/settings.py` to customize:

- LLM settings (model, temperature, etc.)
- JIRA connection details
- Agent parameters
