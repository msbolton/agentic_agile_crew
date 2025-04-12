"""
PRD Creation Task for the Agentic Agile Crew
"""

from crewai import Task

def create_prd_creation_task(agent, dependent_tasks):
    """
    Creates a task for the Project Manager to create a detailed
    Product Requirements Document (PRD) based on business requirements.
    
    Args:
        agent (Agent): The Project Manager agent.
        dependent_tasks (list): Tasks this task depends on, typically the business analysis task.
        
    Returns:
        Task: A CrewAI Task for PRD creation.
    """
    return Task(
        description="""
        Based on the business requirements provided by the Business Analyst, create a comprehensive 
        Product Requirements Document (PRD).
        
        Your task is to transform business requirements into a detailed PRD that will guide the 
        development team. Please include the following sections:
        
        1. Executive Summary:
           - Brief overview of the product
           - Business objectives and value proposition
           - Key stakeholders
        
        2. Product Overview:
           - Product vision and goals
           - User personas and target audience
           - Key scenarios and use cases
        
        3. Functional Requirements:
           - Detailed description of all features
           - User flows and interactions
           - Input/output specifications
           - Error handling requirements
        
        4. Non-Functional Requirements:
           - Performance criteria
           - Security requirements
           - Scalability considerations
           - Usability and accessibility standards
           - Compatibility requirements
        
        5. Constraints and Assumptions:
           - Technical constraints
           - Business constraints
           - Assumptions made during planning
        
        6. Project Timeline:
           - High-level milestones
           - Dependencies between components
           - Potential risks and mitigations
        
        7. Success Criteria:
           - Metrics for measuring success
           - Acceptance criteria for key features
        
        Present your PRD in a clear, well-structured format that developers, designers, and stakeholders 
        can easily understand. Ask clarifying questions about any ambiguous requirements before finalizing.
        """,
        expected_output="A detailed Product Requirements Document (PRD) that clearly specifies all functional and non-functional requirements for the product.",
        agent=agent,
        depends_on=dependent_tasks
    )
