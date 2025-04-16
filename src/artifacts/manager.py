"""
Artifact Manager for Agentic Agile Crew

This module provides functionality to save and manage artifacts produced by
the different agents in the workflow.
"""

import os
import re
import shutil
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Import the logger setup
from src.utils.logger import setup_logger

# Configure logger
logger = setup_logger("artifact_manager")

class ArtifactManager:
    """
    Manages artifacts produced during the development workflow.
    
    Handles storage, retrieval, and organization of artifacts in a structured
    directory hierarchy based on product idea name.
    """
    
    # Mapping of artifact types to file names
    ARTIFACT_FILE_MAPPING = {
        "requirements": "business_requirements.md",
        "PRD document": "prd_document.md",
        "architecture document": "architecture_document.md",
        "task list": "task_list.md",
        "JIRA epics and stories": "jira_stories.md",
        "implementation code": "implementation_code.md"
    }
    
    def __init__(self, base_dir: str = "dist"):
        """
        Initialize the artifact manager.
        
        Args:
            base_dir: Base directory for artifact storage
        """
        self.base_dir = base_dir
        self._ensure_base_dir_exists()
        logger.info(f"Initialized ArtifactManager with base directory: {self.base_dir}")
    
    def _ensure_base_dir_exists(self):
        """Create the base directory if it doesn't exist"""
        if not os.path.exists(self.base_dir):
            try:
                os.makedirs(self.base_dir)
                logger.info(f"Created artifact base directory: {self.base_dir}")
                print(f"Created artifact directory: {os.path.abspath(self.base_dir)}")
            except Exception as e:
                logger.error(f"Failed to create artifact directory: {e}")
                print(f"Error creating artifact directory: {e}")
    
    def sanitize_directory_name(self, name: str) -> str:
        """
        Convert a product idea name to a valid directory name.
        
        Args:
            name: The original product idea name
            
        Returns:
            A sanitized directory name
        """
        # Extract the first line if it's a multi-line text
        if "\n" in name:
            first_line = name.split("\n")[0]
            # If it looks like a markdown heading, extract the text
            if first_line.startswith("#"):
                name = first_line.lstrip("# ")
            else:
                name = first_line
                
        # Remove special characters, replace spaces with underscores
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        
        # Ensure we don't have trailing underscores
        sanitized = sanitized.strip('_')
        
        logger.debug(f"Sanitized directory name from '{name}' to '{sanitized.lower()}'")
        return sanitized.lower()
    
    def create_project_directory(self, product_idea_name: str) -> str:
        """
        Create a directory for the project artifacts.
        
        Args:
            product_idea_name: Name of the product idea
            
        Returns:
            Path to the project directory
        """
        dir_name = self.sanitize_directory_name(product_idea_name)
        project_dir = os.path.join(self.base_dir, dir_name)
        
        if not os.path.exists(project_dir):
            try:
                os.makedirs(project_dir)
                logger.info(f"Created project directory: {project_dir}")
            except Exception as e:
                logger.error(f"Failed to create project directory: {e}")
        else:
            logger.debug(f"Project directory already exists: {project_dir}")
        
        return project_dir
    
    def save_artifact(self, product_idea_name: str, artifact_type: str, content: str) -> str:
        """
        Save an artifact to the project directory.
        
        Args:
            product_idea_name: Name of the product idea
            artifact_type: Type of artifact (e.g., "requirements", "PRD document")
            content: Content of the artifact
            
        Returns:
            Path to the saved artifact
        """
        logger.info(f"Saving artifact of type '{artifact_type}' for '{product_idea_name}'")
        project_dir = self.create_project_directory(product_idea_name)
        
        # Determine filename based on artifact type
        if artifact_type in self.ARTIFACT_FILE_MAPPING:
            filename = self.ARTIFACT_FILE_MAPPING[artifact_type]
            logger.debug(f"Using predefined filename '{filename}' for artifact type '{artifact_type}'")
        else:
            # For unknown types, use a generic name
            sanitized_type = re.sub(r'[^\w\s-]', '', artifact_type)
            sanitized_type = re.sub(r'[\s-]+', '_', sanitized_type)
            filename = f"{sanitized_type.lower()}.md"
            logger.debug(f"Generated filename '{filename}' for unknown artifact type '{artifact_type}'")
        
        # Special handling for implementation code
        if artifact_type == "implementation code":
            # Create a directory for code if it doesn't exist
            code_dir = os.path.join(project_dir, "implementation_code")
            if not os.path.exists(code_dir):
                try:
                    os.makedirs(code_dir)
                    logger.debug(f"Created implementation code directory: {code_dir}")
                except Exception as e:
                    logger.error(f"Failed to create implementation code directory: {e}")
            
            # For now, save the outline in the parent directory
            filepath = os.path.join(project_dir, filename)
            
            # We could parse the content and save individual files in code_dir
            # This would require more complex parsing logic
        else:
            filepath = os.path.join(project_dir, filename)
        
        # Save the content
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"Saved artifact to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save artifact to {filepath}: {e}")
            raise
        
        return filepath
    
    def get_artifact_path(self, product_idea_name: str, artifact_type: str) -> str:
        """
        Get the path to an artifact.
        
        Args:
            product_idea_name: Name of the product idea
            artifact_type: Type of artifact
            
        Returns:
            Path to the artifact
        """
        project_dir = self.create_project_directory(product_idea_name)
        
        # Determine filename based on artifact type
        if artifact_type in self.ARTIFACT_FILE_MAPPING:
            filename = self.ARTIFACT_FILE_MAPPING[artifact_type]
        else:
            # For unknown types, use a generic name
            sanitized_type = re.sub(r'[^\w\s-]', '', artifact_type)
            sanitized_type = re.sub(r'[\s-]+', '_', sanitized_type)
            filename = f"{sanitized_type.lower()}.md"
        
        return os.path.join(project_dir, filename)
    
    def list_artifacts(self, product_idea_name: str) -> List[str]:
        """
        List all artifacts for a product idea.
        
        Args:
            product_idea_name: Name of the product idea
            
        Returns:
            List of artifact paths
        """
        project_dir = self.create_project_directory(product_idea_name)
        artifacts = []
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                artifacts.append(os.path.join(root, file))
        
        logger.info(f"Found {len(artifacts)} artifacts for '{product_idea_name}'")
        logger.debug(f"Artifacts: {artifacts}")
        
        return artifacts
    
    def read_artifact(self, product_idea_name: str, artifact_type: str) -> Optional[str]:
        """
        Read an artifact's content.
        
        Args:
            product_idea_name: Name of the product idea
            artifact_type: Type of artifact
            
        Returns:
            Content of the artifact or None if not found
        """
        filepath = self.get_artifact_path(product_idea_name, artifact_type)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                logger.debug(f"Read artifact: {filepath}")
                return content
            except Exception as e:
                logger.error(f"Failed to read artifact from {filepath}: {e}")
                return None
        else:
            logger.warning(f"Artifact not found: {filepath}")
            return None
    
    def extract_product_name(self, product_idea: str) -> str:
        """
        Extract a product name from the product idea text.
        
        Args:
            product_idea: The product idea text
            
        Returns:
            A name for the product
        """
        if not product_idea or not product_idea.strip():
            # Fallback to timestamp for empty input
            name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Empty product idea, using generated name: {name}")
            return name
        
        # Try to extract from markdown heading
        lines = product_idea.strip().split("\n")
        if lines and lines[0].startswith("#"):
            name = lines[0].lstrip("# ").strip()
            logger.debug(f"Extracted product name from markdown heading: {name}")
            return name
        
        # Try to find any markdown heading
        for line in lines:
            if line.startswith("#"):
                name = line.lstrip("# ").strip()
                logger.debug(f"Extracted product name from embedded markdown heading: {name}")
                return name
        
        # If no heading, use the first non-empty line
        for line in lines:
            if line.strip():
                name = line.strip()
                logger.debug(f"Extracted product name from first non-empty line: {name}")
                return name
        
        # Fallback to timestamp
        name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Could not extract name from product idea, using generated name: {name}")
        return name
