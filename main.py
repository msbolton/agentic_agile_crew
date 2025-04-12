#!/usr/bin/env python3
"""
Agentic Agile Crew - Main Application
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Initialize Pydantic compatibility settings to suppress warnings
from src.utils.pydantic_compat import init as init_pydantic_compat
init_pydantic_compat()

from crewai import Agent, Task, Crew, Process

# Add the project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config.settings import (
    LLM_MODEL, 
    LLM_TEMPERATURE, 
    CREW_VERBOSE,
    AGENT_MEMORY,
    AGENT_ALLOW_DELEGATION,
    USE_OPENROUTER,
    OPENROUTER_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_BUSINESS_ANALYST_MODEL,
    OPENROUTER_PROJECT_MANAGER_MODEL,
    OPENROUTER_ARCHITECT_MODEL,
    OPENROUTER_PRODUCT_OWNER_MODEL,
    OPENROUTER_SCRUM_MASTER_MODEL,
    OPENROUTER_DEVELOPER_MODEL
)

# Import agents
from src.agents.business_analyst import create_business_analyst
from src.agents.project_manager import create_project_manager
from src.agents.architect import create_architect
from src.agents.product_owner import create_product_owner
from src.agents.scrum_master import create_scrum_master
from src.agents.developer import create_developer

# Import tasks
from src.tasks import (
    create_business_analysis_task,
    create_prd_creation_task,
    create_architecture_design_task,
    create_task_list_creation_task,
    create_jira_creation_task,
    create_development_task
)

# Import human-in-the-loop components
from src.human_loop.manager import HumanReviewManager
from src.human_loop.workflow import WorkflowAdapter
from src.artifacts.service import ArtifactService
from src.utils.task_output_saver import TaskOutputSaver

def load_product_idea(product_idea=None):
    """Load the product idea from examples, parameter, or ask the user for input."""
    if product_idea:
        print("Using provided product idea")
        return product_idea
        
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

def main(product_idea=None, with_human_review=False, with_jira=False, use_openrouter=False):
    # Set OpenRouter flag if passed from command line
    if use_openrouter:
        global USE_OPENROUTER
        USE_OPENROUTER = True
        
        # Ensure environment variables are properly set for OpenAI client library
        os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY.strip()
        os.environ["OPENAI_API_BASE"] = OPENROUTER_BASE_URL
        
        print("\n===== OpenRouter Configuration =====")
        print(f"OpenRouter API key prefix: {OPENROUTER_API_KEY[:10]}...")
        print(f"OpenRouter base URL: {OPENROUTER_BASE_URL}")
        print(f"Default model for all agents: {OPENROUTER_MODEL}")
        
        print("\nAgent-specific models (will use default if same as above):")
        for agent_type, model in {
            "Business Analyst": OPENROUTER_BUSINESS_ANALYST_MODEL,
            "Project Manager": OPENROUTER_PROJECT_MANAGER_MODEL,
            "Architect": OPENROUTER_ARCHITECT_MODEL,
            "Product Owner": OPENROUTER_PRODUCT_OWNER_MODEL,
            "Scrum Master": OPENROUTER_SCRUM_MASTER_MODEL,
            "Developer": OPENROUTER_DEVELOPER_MODEL
        }.items():
            if model == OPENROUTER_MODEL:
                print(f"  {agent_type}: [using default]")
            else:
                print(f"  {agent_type}: {model}")
        print("===================================\n")
    """
    Main application function.
    
    Args:
        product_idea: Optional product idea text. If not provided, will load from file or prompt.
        with_human_review: Whether to include human-in-the-loop reviews.
        with_jira: Whether to enable JIRA integration.
    """
    print("\n===== Agentic Agile Crew =====\n")
    
    # Initialize managers
    review_manager = None
    workflow_adapter = None
    artifact_manager = None
    artifact_service = None
    jira_connector = None
    
    # Set up artifact management
    try:
        from src.artifacts.manager import ArtifactManager
        artifact_manager = ArtifactManager()
        artifact_service = ArtifactService(artifact_manager)
        print("Artifact management enabled.")
    except ImportError:
        print("Artifact management not available.")
    
    # Set up JIRA integration if requested
    if with_jira:
        try:
            from src.artifacts.jira_connector import JiraConnector
            jira_connector = JiraConnector()
            
            if jira_connector.is_available():
                if jira_connector.connect():
                    print("JIRA integration enabled and connected.")
                else:
                    print("Warning: JIRA integration enabled but failed to connect.")
            else:
                print("Warning: JIRA integration requested but configuration missing.")
                with_jira = False
        except ImportError:
            print("Warning: JIRA integration requested but module not available.")
            with_jira = False
    
    # Initialize human review manager if needed
    if with_human_review:
        print("Human-in-the-loop mode enabled.")
        review_manager = HumanReviewManager(storage_dir=".agentic_crew")
        workflow_adapter = WorkflowAdapter(
            review_manager=review_manager,
            artifact_manager=artifact_manager,
            artifact_service=artifact_service,
            jira_connector=jira_connector,
            jira_enabled=with_jira
        )
    
    # Load the product idea
    product_idea_text = load_product_idea(product_idea)
    
    # Extract product name for artifact organization
    product_name = "Unknown Project"
    if artifact_manager:
        product_name = artifact_manager.extract_product_name(product_idea_text)
        print(f"\nProject Name: {product_name}")
    
    # Set the product idea name for artifact management
    if workflow_adapter and artifact_manager:
        workflow_adapter.set_product_idea_name(product_name)
        
    # Set the product name for the artifact service
    if artifact_service:
        artifact_service.set_product_name(product_name)
    
    # Extract preferences from the product idea
    print("\nExtracting preferences from product idea...")
    business_analyst_prefs = None
    project_manager_prefs = None
    architect_prefs = None
    product_owner_prefs = None
    scrum_master_prefs = None
    developer_prefs = None
    
    try:
        from src.utils.extractors.preference_extractor import extract_all_preferences, format_preferences_for_agent
        all_preferences = extract_all_preferences(product_idea_text)
        
        # Format preferences for each agent type
        business_analyst_prefs = format_preferences_for_agent(all_preferences, "business_analyst")
        project_manager_prefs = format_preferences_for_agent(all_preferences, "project_manager")
        architect_prefs = format_preferences_for_agent(all_preferences, "architect") 
        product_owner_prefs = format_preferences_for_agent(all_preferences, "product_owner")
        scrum_master_prefs = format_preferences_for_agent(all_preferences, "scrum_master")
        developer_prefs = format_preferences_for_agent(all_preferences, "developer")
        
        print("Successfully extracted and formatted preferences for all agent types")
        if architect_prefs != "No specific preferences found.":
            print("✅ Found technical preferences for architect")
        if business_analyst_prefs != "No specific preferences found.":
            print("✅ Found business requirements for business analyst")
    except Exception as e:
        print(f"Warning: Failed to extract preferences from product idea: {e}")
    
    print("\nInitializing agents...")
    
    # Create agents
    business_analyst = create_business_analyst()
    project_manager = create_project_manager()
    architect = create_architect()
    product_owner = create_product_owner()
    scrum_master = create_scrum_master()
    developer = create_developer()
    
    print("Creating tasks...")
    
    # Create tasks with extracted preferences
    business_analysis_task = create_business_analysis_task(
        business_analyst, product_idea_text, business_analyst_prefs
    )
    prd_creation_task = create_prd_creation_task(
        project_manager, [business_analysis_task], project_manager_prefs
    )
    architecture_design_task = create_architecture_design_task(
        architect, [business_analysis_task, prd_creation_task], architect_prefs
    )
    task_list_creation_task = create_task_list_creation_task(
        product_owner, [prd_creation_task, architecture_design_task], product_owner_prefs
    )
    jira_creation_task = create_jira_creation_task(
        scrum_master, [task_list_creation_task, architecture_design_task, prd_creation_task], scrum_master_prefs
    )
    development_task = create_development_task(
        developer, [jira_creation_task, architecture_design_task], developer_prefs
    )
    
    # Set up task output saver
    task_output_saver = None
    if artifact_service:
        task_output_saver = TaskOutputSaver(
            artifact_service=artifact_service,
            jira_connector=jira_connector,
            with_jira=with_jira
        )
        
        # Define artifact types for each task
        task_to_artifact = [
            (business_analysis_task, "requirements", "Business Analysis"),
            (prd_creation_task, "PRD document", "PRD Creation"),
            (architecture_design_task, "architecture document", "Architecture Design"),
            (task_list_creation_task, "task list", "Task Breakdown"),
            (jira_creation_task, "JIRA epics and stories", "Story Creation"),
            (development_task, "implementation code", "Implementation")
        ]
        
        # Register tasks for output saving
        task_output_saver.register_tasks(task_to_artifact)
        
        print("Automatic artifact saving enabled.")
        
        # Set up immediate artifact saving
        try:
            from src.utils.task_callbacks import create_callbacks_for_tasks
            print("Setting up immediate artifact saving...")
            
            # Create callbacks for tasks
            create_callbacks_for_tasks(
                task_to_artifact,
                artifact_service,
                jira_connector,
                with_jira
            )
            
            print("✅ Immediate artifact saving enabled")
        except Exception as e:
            print(f"Warning: Failed to set up immediate artifact saving: {e}")
    
    # Apply human-in-the-loop wrappers if needed
    if with_human_review and workflow_adapter:
        print("Adding human review checkpoints...")
        
        # Wrap tasks with human review
        workflow_adapter.wrap_task(
            business_analysis_task, 
            "business_analysis", 
            "requirements"
        )
        
        workflow_adapter.wrap_task(
            prd_creation_task, 
            "prd_creation", 
            "PRD document"
        )
        
        workflow_adapter.wrap_task(
            architecture_design_task, 
            "architecture_design", 
            "architecture document"
        )
        
        workflow_adapter.wrap_task(
            task_list_creation_task, 
            "task_breakdown", 
            "task list"
        )
        
        workflow_adapter.wrap_task(
            jira_creation_task, 
            "story_creation", 
            "JIRA epics and stories"
        )
        
        workflow_adapter.wrap_task(
            development_task, 
            "implementation", 
            "implementation code"
        )
    
    print("Assembling the crew...")
    
    # Create the crew with the original tasks
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
    
    if with_human_review:
        print("NOTE: The process will pause at each stage for human review.")
        print("Use the CLI to review and approve/reject each stage's output.")
        print("Run 'python cli.py list-reviews' to see pending reviews.")
    
    # Run the crew
    result = development_crew.kickoff()
    
    print("\n===== Development Process Complete =====\n")
    
    # Print the final result summary
    print(result)
    
    # We no longer need to save artifacts here since we're using immediate artifact saving
    # with task callbacks, but keep this as a fallback method
    if not with_human_review and task_output_saver and not hasattr(task_output_saver, '_callbacks_attached'):
        print("\n===== Saving Artifacts (Fallback Method) =====\n")
        
        # Get all task outputs from the crew result
        if hasattr(result, 'tasks_output') and result.tasks_output:
            print(f"Found {len(result.tasks_output)} task outputs in crew result")
            
            for task_output in result.tasks_output:
                if task_output and hasattr(task_output, 'task') and hasattr(task_output, 'raw_output'):
                    task = task_output.task
                    if task and hasattr(task, 'description'):
                        # Save this task's output as an artifact
                        task_output_saver.save_output(task.description, task_output.raw_output)
        else:
            # Fallback: Try to get outputs directly from task objects
            print("Using fallback method to get task outputs")
            completed_tasks = []
            for task in development_crew.tasks:
                if hasattr(task, 'output') and task.output:
                    completed_tasks.append(task)
                    
                    # Save this task's output as an artifact
                    task_output_saver.save_output(task.description, task.output)
        
        print(f"Saved artifacts for {len(completed_tasks)} completed tasks.")
    
    return result

if __name__ == "__main__":
    # Create an argument parser with comprehensive help information
    parser = argparse.ArgumentParser(
        description="""
        Agentic Agile Crew - AI-powered software development workflow
        
        This application creates an AI-powered agile software development team using
        specialized agents for each development role. The agents collaborate to transform
        a high-level product idea into a fully-defined software project.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --idea "Build a task management app with AI assistance"
  python main.py --idea-file examples/example_product_idea.md --with-human-review
  python main.py --with-jira --with-human-review
  python main.py --with-openrouter --idea "Build a chat application with AI features"
  
Agent Roles:
  • Business Analyst: Refines product ideas into business requirements
  • Project Manager: Creates detailed Product Requirements Documents (PRDs)
  • Architect: Designs technical architecture with reasoning for decisions
  • Product Owner: Creates granular, sequenced tasks
  • Scrum Master: Creates epics and user stories for JIRA
  • Developer: Implements user stories based on specifications

For more commands, try the CLI interface:
  python cli.py --help
        """
    )
    
    # Add arguments
    parser.add_argument(
        "--idea", 
        help="Specify a product idea directly as a string"
    )
    
    parser.add_argument(
        "--idea-file", 
        help="Path to a file containing the product idea"
    )
    
    parser.add_argument(
        "--with-human-review", 
        action="store_true",
        help="Enable human-in-the-loop review at each stage"
    )
    
    parser.add_argument(
        "--with-jira", 
        action="store_true",
        help="Enable JIRA integration for creating epics and stories"
    )
    
    parser.add_argument(
        "--with-openrouter", 
        action="store_true",
        help="Use OpenRouter instead of OpenAI for LLM access"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="Agentic Agile Crew v1.0.0",
        help="Show the application version and exit"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load product idea from file if specified
    product_idea = None
    if args.idea:
        product_idea = args.idea
    elif args.idea_file:
        try:
            with open(args.idea_file, 'r') as f:
                product_idea = f.read()
        except FileNotFoundError:
            print(f"Error: Product idea file '{args.idea_file}' not found.")
            sys.exit(1)
    
    # Run the main function with parsed arguments
    main(
        product_idea=product_idea,
        with_human_review=args.with_human_review,
        with_jira=args.with_jira,
        use_openrouter=args.with_openrouter
    )
