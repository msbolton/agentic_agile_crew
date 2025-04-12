"""
Task List Creation Task for the Agentic Agile Crew
"""

from crewai import Task

def create_task_list_creation_task(agent, dependent_tasks, product_owner_preferences=None):
    """
    Creates a task for the Product Owner to create a granular, sequenced task list
    based on the PRD and architecture documents.
    
    Args:
        agent (Agent): The Product Owner agent.
        dependent_tasks (list): Tasks this task depends on, typically PRD and architecture tasks.
        product_owner_preferences (str, optional): Extracted preferences for the Product Owner.
        
    Returns:
        Task: A CrewAI Task for task list creation.
    """
    # Add product owner preferences section if provided
    po_prefs_section = ""
    if product_owner_preferences:
        po_prefs_section = f"""
        IMPORTANT - Consider these Product Owner Preferences in your task breakdown:
        
        {product_owner_preferences}
        
        These preferences have been extracted directly from the product idea and should
        be carefully incorporated into your task list creation.
        """
    
    return Task(
        description=f"""
        Create a detailed, granular, and sequenced task list based on the PRD and 
        technical architecture provided.
        
        {po_prefs_section}
        
        Your task is to break down the project into specific, actionable tasks that 
        will guide the development team. The task list should be comprehensive, 
        leaving no steps out, and sequenced in the order they should be completed.
        
        Include the following in your task list:
        
        1. Task Breakdown:
           - Break down features into granular, implementable tasks
           - Each task should have a clear definition of done
           - Estimate effort required for each task (using story points or time)
           
        2. Task Sequencing:
           - Arrange tasks in the order they should be completed
           - Identify dependencies between tasks
           - Group related tasks together
           
        3. Priority Assignment:
           - Assign priority levels to tasks (Critical, High, Medium, Low)
           - Identify the minimum viable product (MVP) tasks
           - Flag tasks that can be deferred to later iterations
           
        4. Resource Considerations:
           - Identify specialized skills needed for specific tasks
           - Highlight tasks that might need external resources
           - Note tasks that require specific domain knowledge
           
        5. Risk Assessment:
           - Identify high-risk tasks that might cause delays
           - Suggest mitigation strategies for risky tasks
           - Note assumptions made during task planning
           
        Your task list should be structured, detailed, and comprehensive, providing 
        clear guidance for the development team. Each task should align with the 
        requirements in the PRD and follow the architecture guidelines.
        """,
        expected_output="A detailed, granular, and sequenced task list that breaks down the project into actionable tasks with priorities, dependencies, and effort estimates.",
        agent=agent,
        depends_on=dependent_tasks
    )
