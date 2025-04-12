"""
Development Task for the Agentic Agile Crew
"""

from crewai import Task

def create_development_task(agent, dependent_tasks):
    """
    Creates a task for the Developer to implement user stories based on
    the JIRA epics/stories and architecture document.
    
    Args:
        agent (Agent): The Developer agent.
        dependent_tasks (list): Tasks this task depends on, typically JIRA and architecture tasks.
        
    Returns:
        Task: A CrewAI Task for development implementation.
    """
    return Task(
        description="""
        Implement a high-quality prototype implementation based on the JIRA stories
        and architecture document provided.
        
        Your task is to develop clean, maintainable code that implements the key 
        functionality described in the user stories. Focus on the core features and
        demonstrate good software development practices.
        
        Include the following in your implementation:
        
        1. Project Structure:
           - Create a well-organized directory structure
           - Set up the proper configuration files
           - Include appropriate package management
           
        2. Core Functionality:
           - Implement the essential features from the user stories
           - Follow the architecture guidelines strictly
           - Use the specified technology stack
           
        3. Documentation:
           - Add clear comments explaining complex logic
           - Include a README with setup instructions
           - Document any assumptions or limitations
           
        4. Quality Assurance:
           - Implement basic error handling
           - Add input validation for critical functions
           - Include unit tests for key components
           
        5. Best Practices:
           - Follow language-specific coding standards
           - Use design patterns appropriately
           - Implement proper separation of concerns
           
        Your implementation should be clean, well-documented, and follow the
        architecture guidelines. Focus on delivering a solid foundation that demonstrates
        the key functionality rather than implementing every feature completely.
        """,
        expected_output="A high-quality code implementation that demonstrates the core functionality described in the user stories, following the architecture guidelines and best practices.",
        agent=agent,
        depends_on=dependent_tasks
    )
