"""
JIRA Creation Task for the Agentic Agile Crew
"""

from crewai import Task

def create_jira_creation_task(agent, dependent_tasks):
    """
    Creates a task for the Scrum Master to create epics and user stories in JIRA
    based on the task list, architecture document, and PRD.
    
    Args:
        agent (Agent): The Scrum Master agent.
        dependent_tasks (list): Tasks this task depends on, typically task list, architecture, and PRD tasks.
        
    Returns:
        Task: A CrewAI Task for JIRA creation.
    """
    return Task(
        description="""
        Create well-structured epics and user stories suitable for JIRA based on the 
        task list, architecture document, and PRD provided.
        
        Your task is to transform the granular task list into properly formatted epics 
        and user stories that follow agile best practices. These should be ready for 
        implementation in JIRA.
        
        Include the following in your JIRA stories document:
        
        1. Epic Structure:
           - Create epics that group related functionality
           - Provide epic descriptions that outline the broader goal
           - Assign priorities to epics based on business value
           
        2. User Story Format:
           - Write stories in the format: "As a [user role], I want [goal], so that [benefit]"
           - Ensure stories are independent, negotiable, valuable, estimable, small, and testable
           - Link each story to its parent epic
           
        3. Acceptance Criteria:
           - Define clear, testable acceptance criteria for each story
           - Include edge cases and exception handling criteria
           - Specify any performance or non-functional requirements
           
        4. Technical Details:
           - Include relevant technical details from the architecture document
           - Reference specific data models and API endpoints
           - Link to relevant sections of documentation
           
        5. Story Points and Priority:
           - Assign story points reflecting complexity and effort
           - Set priority based on business value and dependencies
           - Flag blockers or dependencies between stories
           
        6. Additional Fields:
           - Suggest appropriate labels for categorization
           - Recommend components based on technical architecture
           - Include notes on any implementation considerations
           
        Format your output as a structured document that could be directly imported 
        into JIRA or used by a team to manually create the tickets. Organize stories 
        within their parent epics for clarity.
        """,
        expected_output="A well-structured document containing epics and user stories ready for JIRA, with acceptance criteria, technical details, and proper organization.",
        agent=agent,
        depends_on=dependent_tasks
    )
