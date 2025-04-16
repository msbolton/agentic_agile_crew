#!/usr/bin/env python3
"""
Command Line Interface for Agentic Agile Crew

Simple CLI providing access to artifacts and running the main application.
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def start_project(args):
    """Start a new project with the given product idea file"""
    if not os.path.exists(args.idea_file):
        print(f"Error: File not found: {args.idea_file}")
        return
    
    try:
        with open(args.idea_file, 'r') as f:
            product_idea = f.read()
        
        if not product_idea.strip():
            print("Error: Product idea file is empty.")
            return
        
        # Check JIRA availability if requested
        if hasattr(args, 'with_jira') and args.with_jira and not JIRA_AVAILABLE:
            print("Warning: JIRA integration requested but not available.")
            print("Make sure JIRA configuration is set up correctly.")
            
            # Ask for confirmation
            if input("Continue without JIRA integration? (y/n): ").lower() not in ["y", "yes"]:
                return
            args.with_jira = False
        
        # Launch the main application with the product idea
        print(f"Starting project with product idea from {args.idea_file}")
        
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
        result = main(
            product_idea=product_idea, 
            with_jira=with_jira,
            use_openrouter=args.with_openrouter if hasattr(args, 'with_openrouter') else False
        )
        
        print("Project completed!")
        
    except Exception as e:
        print(f"Error starting project: {e}")

def list_artifacts(args):
    """List artifacts for a project"""
    if not ARTIFACTS_AVAILABLE:
        print("Artifact management is not available.")
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
        
        print("\nAvailable Projects:")
        print("------------------")
        
        for i, project in enumerate(projects, 1):
            project_dir = os.path.join(artifact_manager.base_dir, project)
            artifact_count = len([f for f in os.listdir(project_dir) 
                              if os.path.isfile(os.path.join(project_dir, f))])
            
            print(f"{i}. {project.replace('_', ' ').title()}")
            print(f"   Artifacts: {artifact_count}")
            print("   ------------------")
        
        print("\nUse 'python cli.py list-artifacts <project_name>' to view artifacts for a specific project.")
        return
    
    # List artifacts for a specific project
    project_dir = os.path.join(artifact_manager.base_dir, args.project_name)
    if not os.path.exists(project_dir):
        print(f"Error: Project '{args.project_name}' not found.")
        return
    
    # Get all files in the project directory
    artifacts = [f for f in os.listdir(project_dir) 
              if os.path.isfile(os.path.join(project_dir, f))]
    
    if not artifacts:
        print(f"\nNo artifacts found for project '{args.project_name}'.")
        return
    
    print(f"\nArtifacts for {args.project_name.replace('_', ' ').title()}:")
    print("------------------")
    
    for i, artifact in enumerate(artifacts, 1):
        artifact_path = os.path.join(project_dir, artifact)
        artifact_size = os.path.getsize(artifact_path)
        artifact_modified = datetime.fromtimestamp(os.path.getmtime(artifact_path))
        
        print(f"{i}. {artifact}")
        print(f"   Size: {artifact_size // 1024} KB")
        print(f"   Modified: {artifact_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ------------------")
    
    print("\nUse 'python cli.py view-artifact <project_name> <artifact_name>' to view an artifact.")

def view_artifact(args):
    """View the content of an artifact"""
    if not ARTIFACTS_AVAILABLE:
        print("Artifact management is not available.")
        return
    
    # Check if project exists
    project_dir = os.path.join(artifact_manager.base_dir, args.project_name)
    if not os.path.exists(project_dir):
        print(f"Error: Project '{args.project_name}' not found.")
        return
    
    # Check if artifact exists
    artifact_path = os.path.join(project_dir, args.artifact_name)
    if not os.path.exists(artifact_path):
        print(f"Error: Artifact '{args.artifact_name}' not found.")
        return
    
    # Read and display the artifact
    try:
        with open(artifact_path, 'r') as f:
            content = f.read()
        
        print(f"\nArtifact: {args.artifact_name}")
        print("------------------")
        print(f"Project: {args.project_name.replace('_', ' ').title()}")
        print(f"Path: {artifact_path}")
        print("------------------")
        
        print("\nContent:")
        print(content)
        print("------------------")
    except Exception as e:
        print(f"Error reading artifact: {e}")

def export_artifacts(args):
    """Export artifacts to a specified directory"""
    if not ARTIFACTS_AVAILABLE:
        print("Artifact management is not available.")
        return
    
    # Check if project exists
    project_dir = os.path.join(artifact_manager.base_dir, args.project_name)
    if not os.path.exists(project_dir):
        print(f"Error: Project '{args.project_name}' not found.")
        return
    
    # Create export directory
    export_dir = args.export_dir
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Copy all artifacts
    try:
        import shutil
        copied_files = 0
        artifacts = [f for f in os.listdir(project_dir) 
                  if os.path.isfile(os.path.join(project_dir, f))]
        
        for artifact in artifacts:
            src_path = os.path.join(project_dir, artifact)
            dst_path = os.path.join(export_dir, artifact)
            shutil.copy2(src_path, dst_path)
            copied_files += 1
        
        print(f"Successfully exported {copied_files} artifacts to {export_dir}")
    except Exception as e:
        print(f"Error exporting artifacts: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic Agile Crew CLI - AI-powered software development workflow"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    # Start project command
    start_parser = subparsers.add_parser("start", help="Start a new project with a product idea file")
    start_parser.add_argument("idea_file", help="Path to the product idea file")
    start_parser.add_argument("--with-jira", action="store_true", help="Enable JIRA integration")
    start_parser.add_argument("--with-openrouter", action="store_true", help="Use OpenRouter instead of OpenAI")
    start_parser.set_defaults(func=start_project)
    
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