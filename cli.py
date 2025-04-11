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
        
        # Launch the main application with the product idea
        print(success_message(f"Starting project with product idea from {args.idea_file}"))
        
        # Invoke the main application
        # In a real CLI, we might use subprocess or similar to launch the main app
        from main import main
        
        # Pass the product idea to the main function
        result = main(product_idea=product_idea, with_human_review=True)
        
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

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic Agile Crew CLI - AI-powered software development with human oversight"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    # Start project command
    start_parser = subparsers.add_parser("start", help="Start a new project with a product idea file")
    start_parser.add_argument("idea_file", help="Path to the product idea file")
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate function
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
