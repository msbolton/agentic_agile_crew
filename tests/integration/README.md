# Integration Tests for Agentic Agile Crew

This directory contains integration tests for the Agentic Agile Crew project, focusing on the human-in-the-loop functionality.

## Test Categories

### CLI Integration Tests (`test_cli_integration.py`)

Tests the integration between the CLI interface and the human review system:

- Verifies that the CLI correctly displays pending reviews
- Tests the review process for both approval and rejection scenarios
- Validates project status display with various review states

### Human Loop Workflow Tests (`test_human_loop_workflow.py`)

Tests the integration of human-in-the-loop functionality with the workflow:

- Simulates a workflow where all reviews are approved
- Tests rejection and revision scenarios
- Verifies complex workflows with multiple rounds of human intervention

### Main Application Integration Tests (`test_main_integration.py`)

Tests the integration of human review with the main application:

- Verifies that human review components can be properly integrated
- Tests complete workflow with simulated review process
- Validates that workflow behavior changes correctly when human review is enabled/disabled

## Running Tests

To run all integration tests:

```bash
cd /path/to/agentic_agile_crew
source venv/bin/activate
python -m pytest tests/integration/ -v
```

To run a specific test file:

```bash
python -m pytest tests/integration/test_cli_integration.py -v
```

## Test Design

These integration tests use mocks to simulate the CrewAI components and focus on testing the human-in-the-loop functionality. They validate that:

1. The review process works correctly at each stage
2. Feedback is properly communicated back to agents
3. Rejected outputs can be revised and resubmitted
4. The workflow handles both approval and rejection paths correctly

The tests avoid making actual LLM API calls by using mock agents and tasks, while still exercising the actual human review code paths.
