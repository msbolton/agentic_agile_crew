#!/usr/bin/env python3
"""
Command Line Interface for Agentic Agile Crew with Human-in-the-Loop

This CLI allows users to interact with the Agentic Agile Crew system,
providing commands for starting projects, reviewing outputs, and managing
the workflow.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import human-in-the-loop components
from src.human_loop.manager import HumanReviewManager
from src.human_loop.formatter import (
    format_title, format_heading, format_subheading,
    format_key_value, format_separator, format_content,
    success_message, error_message, warning_message,
    format_approval_status, Colors
)

# Try to import artifact manager
try:
    from src.artifacts.manager import ArtifactManager
    artifact_manager = ArtifactManager()
    ARTIFACTS_AVAILABLE = True
except ImportError:
    artifact_manager = None
    ARTIFACTS_AVAILABLE = False

# Try to import JIRA connector
try:
    from src.artifacts.jira_connector import JiraConnector
    jira_connector = JiraConnector()
    JIRA_AVAILABLE = jira_connector.is_available()
except ImportError:
    jira_connector = None
    JIRA_AVAILABLE = False

# Create human review manager
review_manager = HumanReviewManager(storage_dir=".agentic_crew")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def start_project(args):
    """Start a new project with the given product idea file"""
    if not os.path.exists(args.idea_file):
        print(error_message(f"Error: File not found: {args.idea_file}"))
        return
    
    try:
        with open(args.idea_file, 'r') as f:
            product_idea = f.read()
        
        if not product_idea.strip():
            print(error_message("Error: Product idea file is empty."))
            return
        
        # Check JIRA availability if requested
        if hasattr(args, 'with_jira') and args.with_jira and not JIRA_AVAILABLE:
            print(warning_message("Warning: JIRA integration requested but not available."))
            print(warning_message("Make sure JIRA configuration is set up correctly."))
            
            # Ask for confirmation
            if input("Continue without JIRA integration? (y/n): ").lower() not in ["y", "yes"]:
                return
            args.with_jira = False
        
        # Launch the main application with the product idea
        print(success_message(f"Starting project with product idea from {args.idea_file}"))
        
        # Invoke the main application
        from main import main
        
        # Extract product name for user feedback
        product_name = "Unknown Project"
        if ARTIFACTS_AVAILABLE:
            product_name = artifact_manager.extract_product_name(product_idea)
            print(f"Project name: {product_name}")
            print(f"Artifacts will be saved in: artifacts/{artifact_manager.sanitize_directory_name(product_name)}/")
        
        # Pass the product idea to the main function
        with_jira = hasattr(args, 'with_jira') and args.with_jira
        result = main(product_idea=product_idea, with_human_review=True, with_jira=with_jira)
        
        print(success_message("Project started!"))
        print("Use 'python cli.py list-reviews' to see pending reviews.")
    except Exception as e:
        print(error_message(f"Error starting project: {e}"))

def list_reviews(args):
    """List all pending review items"""
    pending = review_manager.get_pending_reviews()
    
    if not pending:
        print("\nNo pending reviews.")
        return
    
    print("\n" + format_title("Pending Reviews"))
    print(format_separator())
    
    for i, review in enumerate(pending, 1):
        status_str = format_approval_status(review.status)
        agent_str = f"{Colors.BOLD}{review.agent_id}{Colors.RESET}"
        
        print(f"{i}. [{status_str}] {agent_str} - {review.stage_name}")
        print(f"   ID: {review.id}")
        print(f"   Artifact: {review.artifact_type}")
        print(f"   Created: {review.timestamp}")
        print(format_separator("-"))
    
    print("\nUse 'python cli.py review <ID>' to review a specific item.")

def review_item(args):
    """Review a specific item by its ID"""
    # Get the review request
    review_request = review_manager.get_review_by_id(args.review_id)
    
    if not review_request:
        print(error_message(f"Error: Review request with ID {args.review_id} not found."))
        print("Use 'python cli.py list-reviews' to see all pending reviews.")
        return
    
    # Clear screen for better readability
    clear_screen()
    
    # Display review request details
    print("\n" + format_title(f"Review Request: {review_request.stage_name}"))
    print(format_separator())
    
    print(format_key_value("ID", review_request.id))
    print(format_key_value("Agent", review_request.agent_id))
    print(format_key_value("Artifact Type", review_request.artifact_type))
    print(format_key_value("Created", review_request.timestamp))
    print(format_separator())
    
    # Display context information if available
    if review_request.context:
        print("\n" + format_heading("Context"))
        for key, value in review_request.context.items():
            if isinstance(value, str) and len(value) > 100:
                print(format_key_value(key, value[:100] + "..."))
            else:
                print(format_key_value(key, value))
        print(format_separator())
    
    # Display content for review
    print("\n" + format_heading("Content to Review"))
    print(format_content(review_request.content))
    print("\n" + format_separator())
    
    # Get feedback from user
    print("\n" + format_heading("Your Review"))
    
    # Ask for approval
    approval_input = input("Do you approve this item? (yes/no): ").strip().lower()
    approved = approval_input in ["yes", "y", "true", "t", "1"]
    
    # Get feedback text
    if approved:
        print(success_message("\nItem Approved"))
        feedback = input("Optional feedback: ").strip()
    else:
        print(warning_message("\nItem Rejected"))
        feedback = input("Please provide feedback for revision: ").strip()
    
    # Submit feedback
    success = review_manager.submit_feedback(review_request.id, approved, feedback)
    
    if success:
        print(success_message("\nFeedback submitted successfully!"))
        if approved:
            print("The workflow will continue to the next stage.")
        else:
            print("The item will be sent back for revision.")
    else:
        print(error_message("\nError submitting feedback."))

def project_status(args):
    """Show the current project status"""
    # In a real application, we would load this from a project status file
    # For this example, we'll create a simple status display based on completed reviews
    
    completed_reviews = review_manager.get_completed_reviews()
    pending_reviews = review_manager.get_pending_reviews()
    
    # Define workflow stages
    stages = [
        "business_analysis",
        "prd_creation",
        "architecture_design",
        "task_breakdown",
        "story_creation",
        "implementation"
    ]
    
    # Initialize status
    status = {}
    for stage in stages:
        status[stage] = {
            "completed": False,
            "in_progress": False,
            "status": "Not started",
            "approved": False
        }
    
    # Update status based on completed reviews
    for review in completed_reviews:
        stage = review.get("stage_name")
        if stage in status:
            status[stage]["completed"] = True
            status[stage]["approved"] = review.get("status") == "approved"
            if status[stage]["approved"]:
                status[stage]["status"] = "Completed and approved"
            else:
                status[stage]["status"] = "Completed but rejected"
    
    # Update status based on pending reviews
    for review in pending_reviews:
        stage = review.stage_name
        if stage in status:
            status[stage]["in_progress"] = True
            if not status[stage]["completed"]:
                status[stage]["status"] = "Awaiting review"
    
    # Display status
    print("\n" + format_title("Project Status"))
    print(format_separator())
    
    for stage in stages:
        details = status[stage]
        
        if details["completed"] and details["approved"]:
            emoji = "✅"
            color = Colors.GREEN
        elif details["completed"] and not details["approved"]:
            emoji = "⚠️"
            color = Colors.YELLOW
        elif details["in_progress"]:
            emoji = "⏳"
            color = Colors.CYAN
        else:
            emoji = "⏹️"
            color = Colors.RESET
        
        stage_name = stage.replace("_", " ").title()
        print(f"{emoji} {color}{stage_name}{Colors.RESET}: {details['status']}")
    
    print(format_separator())

def list_completed(args):
    """List all completed reviews"""
    completed = review_manager.get_completed_reviews()
    
    if not completed:
        print("\nNo completed reviews.")
        return
    
    print("\n" + format_title("Completed Reviews"))
    print(format_separator())
    
    for i, review in enumerate(completed, 1):
        status_str = format_approval_status(review.get("status", "pending"))
        agent_str = f"{Colors.BOLD}{review.get('agent_id', 'Unknown')}{Colors.RESET}"
        
        print(f"{i}. [{status_str}] {agent_str} - {review.get('stage_name', 'Unknown')}")
        print(f"   ID: {review.get('id', 'Unknown')}")
        print(f"   Artifact: {review.get('artifact_type', 'Unknown')}")
        print(f"   Completed: {review.get('completed_at', 'Unknown')}")
        
        if review.get("feedback"):
            print(f"   Feedback: {review.get('feedback')[:100]}...")
        
        print(format_separator("-"))

def list_artifacts(args):
    """List artifacts for a project"""
    if not ARTIFACTS_AVAILABLE:
        print(error_message("Artifact management is not available."))
        return
    
    # List all projects if no project name provided
    if not hasattr(args, 'project_name') or not args.project_name:
        if not os.path.exists(artifact_manager.base_dir):
            print("\nNo artifacts found.")
            return
        
        # List all project directories
        projects = [d for d in os.listdir(artifact_manager.base_dir) 
                  if os.path.isdir(os.path.join(artifact_manager.base_dir, d))]
        
        if not projects:
            print("\nNo project artifacts found.")
            return
        
        print("\n" + format_title("Available Projects"))
        print(format_separator())
        
        for i, project in enumerate(projects, 1):
            project_dir = os.path.join(artifact_manager.base_dir, project)
            artifact_count = len([f for f in os.listdir(project_dir) 
                              if os.path.isfile(os.path.join(project_dir, f))])
            
            print(f"{i}. {Colors.BOLD}{project.replace('_', ' ').title()}{Colors.RESET}")
            print(f"   Artifacts: {artifact_count}")
            print(format_separator("-"))
        
        print("\nUse 'python cli.py list-artifacts <project_name>' to view artifacts for a specific project.")
        return
    
    # List artifacts for a specific project
    project_dir = os.path.join(artifact_manager.base_dir, args.project_name)
    if not os.path.exists(project_dir):
        print(error_message(f"Error: Project '{args.project_name}' not found."))
        return
    
    # Get all files in the project directory
    artifacts = [f for f in os.listdir(project_dir) 
              if os.path.isfile(os.path.join(project_dir, f))]
    
    if not artifacts:
        print(f"\nNo artifacts found for project '{args.project_name}'.")
        return
    
    print("\n" + format_title(f"Artifacts for {args.project_name.replace('_', ' ').title()}"))
    print(format_separator())
    
    for i, artifact in enumerate(artifacts, 1):
        artifact_path = os.path.join(project_dir, artifact)
        artifact_size = os.path.getsize(artifact_path)
        artifact_modified = datetime.fromtimestamp(os.path.getmtime(artifact_path))
        
        print(f"{i}. {Colors.BOLD}{artifact}{Colors.RESET}")
        print(f"   Size: {artifact_size // 1024} KB")
        print(f"   Modified: {artifact_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print(format_separator("-"))
    
    print("\nUse 'python cli.py view-artifact <project_name> <artifact_name>' to view an artifact.")

def view_artifact(args):
    """View the content of an artifact"""
    if not ARTIFACTS_AVAILABLE:
        print(error_message("Artifact management is not available."))
        return
    
    # Check if project exists
    project_dir = os.path.join(artifact_manager.base_dir, args.project_name)
    if not os.path.exists(project_dir):
        print(error_message(f"Error: Project '{args.project_name}' not found."))
        return
    
    # Check if artifact exists
    artifact_path = os.path.join(project_dir, args.artifact_name)
    if not os.path.exists(artifact_path):
        print(error_message(f"Error: Artifact '{args.artifact_name}' not found."))
        return
    
    # Read and display the artifact
    try:
        with open(artifact_path, 'r') as f:
            content = f.read()
        
        clear_screen()
        print("\n" + format_title(f"Artifact: {args.artifact_name}"))
        print(format_separator())
        print(f"Project: {args.project_name.replace('_', ' ').title()}")
        print(f"Path: {artifact_path}")
        print(format_separator())
        
        print("\n" + format_heading("Content"))
        print(format_content(content))
        print("\n" + format_separator())
    except Exception as e:
        print(error_message(f"Error reading artifact: {e}"))

def export_artifacts(args):
    """Export artifacts to a specified directory"""
    if not ARTIFACTS_AVAILABLE:
        print(error_message("Artifact management is not available."))
        return
    
    # Check if project exists
    project_dir = os.path.join(artifact_manager.base_dir, args.project_name)
    if not os.path.exists(project_dir):
        print(error_message(f"Error: Project '{args.project_name}' not found."))
        return
    
    # Create export directory
    export_dir = args.export_dir
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Copy all artifacts
    try:
        copied_files = 0
        artifacts = [f for f in os.listdir(project_dir) 
                  if os.path.isfile(os.path.join(project_dir, f))]
        
        for artifact in artifacts:
            src_path = os.path.join(project_dir, artifact)
            dst_path = os.path.join(export_dir, artifact)
            shutil.copy2(src_path, dst_path)
            copied_files += 1
        
        print(success_message(f"Successfully exported {copied_files} artifacts to {export_dir}"))
    except Exception as e:
        print(error_message(f"Error exporting artifacts: {e}"))

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic Agile Crew CLI - AI-powered software development with human oversight"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    # Start project command
    start_parser = subparsers.add_parser("start", help="Start a new project with a product idea file")
    start_parser.add_argument("idea_file", help="Path to the product idea file")
    start_parser.add_argument("--with-jira", action="store_true", help="Enable JIRA integration")
    start_parser.set_defaults(func=start_project)
    
    # List reviews command
    list_parser = subparsers.add_parser("list-reviews", help="List all pending review items")
    list_parser.set_defaults(func=list_reviews)
    
    # Review item command
    review_parser = subparsers.add_parser("review", help="Review a specific item by its ID")
    review_parser.add_argument("review_id", help="ID of the review to examine")
    review_parser.set_defaults(func=review_item)
    
    # Project status command
    status_parser = subparsers.add_parser("status", help="Show the current project status")
    status_parser.set_defaults(func=project_status)
    
    # List completed reviews command
    completed_parser = subparsers.add_parser("list-completed", help="List all completed reviews")
    completed_parser.set_defaults(func=list_completed)
    
    # Artifact commands (if available)
    if ARTIFACTS_AVAILABLE:
        # List artifacts command
        artifacts_parser = subparsers.add_parser("list-artifacts", help="List artifacts for a project")
        artifacts_parser.add_argument("project_name", nargs="?", help="Name of the project (optional)")
        artifacts_parser.set_defaults(func=list_artifacts)
        
        # View artifact command
        view_parser = subparsers.add_parser("view-artifact", help="View the content of an artifact")
        view_parser.add_argument("project_name", help="Name of the project")
        view_parser.add_argument("artifact_name", help="Name of the artifact to view")
        view_parser.set_defaults(func=view_artifact)
        
        # Export artifacts command
        export_parser = subparsers.add_parser("export-artifacts", help="Export artifacts to a directory")
        export_parser.add_argument("project_name", help="Name of the project")
        export_parser.add_argument("export_dir", help="Directory to export artifacts to")
        export_parser.set_defaults(func=export_artifacts)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate function
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
