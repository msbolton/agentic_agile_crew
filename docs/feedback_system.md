# Feedback-Driven Agent Refinement Loop

The Agentic Agile Crew now includes a feedback-driven revision system that automatically routes human feedback back to agents for revision until approval is granted. This document explains how the system works and how to use it.

## Overview

When human reviewers reject an agent's output with feedback, the system:

1. Parses the feedback into structured, actionable items
2. Reformulates the original task with the feedback incorporated
3. Sends the task back to the original agent for revision
4. Submits the revised output for another human review
5. Repeats as needed until approved or max cycles reached

## Key Components

The feedback-driven revision system consists of the following components:

### 1. Feedback Parser

Converts unstructured human feedback into structured, actionable items:

- Automatically categorizes feedback by type (add, change, remove, clarify)
- Identifies affected sections of the document
- Sets priority levels for feedback items
- Formats feedback for agent consumption

### 2. Feedback Memory

Stores revision history and feedback across multiple review cycles:

- Records all versions of an artifact
- Tracks feedback for each revision
- Provides context for subsequent revisions
- Preserves the entire history for later reference

### 3. Cycle Limiter

Prevents infinite revision loops:

- Sets maximum number of revision cycles (default: 5)
- Tracks cycle count for each agent/stage
- Can auto-approve after reaching the limit
- Provides status information for the UI

### 4. Revision Cycle

Orchestrates the revision process:

- Creates specialized revision tasks based on feedback
- Manages communication between human reviewers and agents
- Handles transitions between review and revision
- Maintains the continuity of the development workflow

## Using the Revision System

The revision system is automatically integrated into the existing human review workflow. When a reviewer rejects an output with feedback, the system will automatically start a revision cycle.

### CLI Commands

The following new CLI commands are available:

```bash
# List active revision cycles
python cli.py list-revisions

# View revision history for a specific agent/stage
python cli.py revision-history <agent_id> <stage_name>
```

### Workflow

1. Review an item as normal with `python cli.py review <id>`
2. If you reject it, provide clear, detailed feedback
3. The system will automatically route the feedback to the agent
4. The agent will revise the output based on your feedback
5. You'll receive a notification about the new revision to review
6. Review the revision and either approve or provide additional feedback

### Best Practices for Providing Feedback

To get the best results from the revision system:

1. **Be specific**: Clearly state what needs to be changed
2. **Reference sections**: Mention the specific part of the document that needs revision
3. **Suggest improvements**: Don't just identify problems, suggest solutions
4. **Prioritize issues**: Focus on the most important changes first
5. **Use clear directives**: Start feedback with action words (add, change, remove, clarify)

Example: "Add a section on security considerations" or "The Architecture section needs to include database schema details"

## Configuration

The maximum number of revision cycles can be configured in the main application:

```python
# In main.py
review_manager = HumanReviewManager(storage_dir=".agentic_crew", max_revision_cycles=3)
```

## Technical Details

The revision system is implemented in the `src/human_loop/feedback` directory:

- `parser.py`: Feedback parsing and formatting
- `memory.py`: Revision history storage
- `limiter.py`: Cycle counting and limiting
- `cycle.py`: Revision cycle orchestration

Integration with the existing system is handled in:

- `src/human_loop/manager.py`: Manages revision requests
- `src/human_loop/workflow.py`: Connects revisions to the workflow

## Future Enhancements

Planned enhancements for the revision system:

1. Specialized revision agents for different types of feedback
2. More sophisticated feedback parsing with NLP
3. Feedback templates for common revision patterns
4. Visual diff views between revisions
5. Automated feedback based on quality rules
