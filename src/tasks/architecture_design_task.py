"""
Architecture Design Task for the Agentic Agile Crew
"""

from crewai import Task

def create_architecture_design_task(agent, dependent_tasks):
    """
    Creates a task for the Architect to design a technical architecture
    based on the business requirements and PRD.
    
    Args:
        agent (Agent): The Architect agent.
        dependent_tasks (list): Tasks this task depends on, typically business analysis and PRD tasks.
        
    Returns:
        Task: A CrewAI Task for architecture design.
    """
    return Task(
        description="""
        Design a comprehensive technical architecture for the product based on the 
        business requirements and PRD provided.
        
        Your task is to create a detailed technical architecture document that guides 
        implementation. For each significant architectural decision, consider at least 
        three alternatives and provide reasoning for your final choice.
        
        Include the following components in your architecture document:
        
        1. Architecture Overview:
           - High-level architecture diagram
           - Key components and their relationships
           - Design patterns and principles applied
        
        2. Technology Stack:
           - Frontend technologies (frameworks, libraries)
           - Backend technologies (languages, frameworks)
           - Database selection and schema design
           - Third-party services and integrations
        
        3. Data Architecture:
           - Data models and relationships
           - Database schema design
           - Data flow diagrams
           - Data storage and retrieval strategies
        
        4. API Design:
           - API endpoints and their specifications
           - Authentication and authorization mechanisms
           - Request/response formats
           - Error handling strategies
        
        5. Security Infrastructure:
           - Authentication and authorization framework
           - Data encryption strategies
           - Security controls and compliance measures
           - Vulnerability management approach
        
        6. Scalability and Performance:
           - Scalability strategies
           - Caching mechanisms
           - Performance optimization approaches
           - Load balancing strategies
        
        7. Deployment Architecture:
           - Infrastructure requirements
           - Deployment pipelines
           - Monitoring and logging solutions
           - Disaster recovery strategies
        
        8. Decision Records:
           - Document major architectural decisions
           - Include alternatives considered
           - Provide clear reasoning for each choice
        
        Your architecture should be well-reasoned, technically sound, and aligned with 
        the business requirements and PRD. Document any assumptions made during the 
        architecture design process.
        """,
        expected_output="A comprehensive technical architecture document with technology choices, data models, API specifications, security infrastructure, and detailed reasoning for all decisions.",
        agent=agent,
        depends_on=dependent_tasks
    )
