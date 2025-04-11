#!/usr/bin/env python3
"""
Agentic Agile Crew - Main Application
"""

import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Add the project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config.settings import (
    LLM_MODEL, 
    LLM_TEMPERATURE, 
    CREW_VERBOSE,
    AGENT_MEMORY,
    AGENT_ALLOW_DELEGATION
)

# Import agents
from src.agents.business_analyst import create_business_analyst
from src.agents.project_manager import create_project_manager
from src.agents.architect import create_architect
from src.agents.product_owner import create_product_owner
from src.agents.scrum_master import create_scrum_master
from src.agents.developer import create_developer

# Import tasks
from src.tasks.business_analysis_task import create_business_analysis_task
from src.tasks.prd_creation_task import create_prd_creation_task
from src.tasks.architecture_design_task import create_architecture_design_task
from src.tasks.task_list_creation_task import create_task_list_creation_task
from src.tasks.jira_creation_task import create_jira_creation_task
from src.tasks.development_task import create_development_task

def load_product_idea():
    """Load the product idea from examples or ask the user for input."""
    try:
        with open('examples/example_product_idea.md', 'r') as file:
            product_idea = file.read()
            
        if not product_idea.strip():
            raise FileNotFoundError
            
        print("Loaded product idea from examples/example_product_idea.md")
        return product_idea
    except FileNotFoundError:
        print("\nNo product idea found in examples. Please describe your product idea:")
        return input("> ")

def main():
    """Main application function."""
    print("\n===== Agentic Agile Crew =====\n")
    
    # Load the product idea
    product_idea = load_product_idea()
    print("\nInitializing agents...")
    
    # Create agents
    business_analyst = create_business_analyst()
    project_manager = create_project_manager()
    architect = create_architect()
    product_owner = create_product_owner()
    scrum_master = create_scrum_master()
    developer = create_developer()
    
    print("Creating tasks...")
    
    # Create tasks
    business_analysis_task = create_business_analysis_task(business_analyst, product_idea)
    prd_creation_task = create_prd_creation_task(project_manager, [business_analysis_task])
    architecture_design_task = create_architecture_design_task(
        architect, [business_analysis_task, prd_creation_task]
    )
    task_list_creation_task = create_task_list_creation_task(
        product_owner, [prd_creation_task, architecture_design_task]
    )
    jira_creation_task = create_jira_creation_task(
        scrum_master, [task_list_creation_task, architecture_design_task, prd_creation_task]
    )
    development_task = create_development_task(
        developer, [jira_creation_task, architecture_design_task]
    )
    
    print("Assembling the crew...")
    
    # Create the crew
    development_crew = Crew(
        agents=[
            business_analyst, 
            project_manager, 
            architect, 
            product_owner, 
            scrum_master, 
            developer
        ],
        tasks=[
            business_analysis_task,
            prd_creation_task, 
            architecture_design_task,
            task_list_creation_task,
            jira_creation_task,
            development_task
        ],
        verbose=CREW_VERBOSE,
        process=Process.sequential  # Tasks will be executed in order
    )
    
    print("\n===== Starting Development Process =====\n")
    
    # Run the crew
    result = development_crew.kickoff()
    
    print("\n===== Development Process Complete =====\n")
    
    # Print the final result summary
    print(result)
    
    return result

if __name__ == "__main__":
    main()
