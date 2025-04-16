"""
TaskOutputSaver - A utility for saving task outputs as artifacts.

This approach doesn't modify CrewAI's internal structures but instead
directly monitors task outputs and saves them as artifacts.
"""

import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger("task_output_saver")

class TaskOutputSaver:
    """
    A utility class for saving task outputs as artifacts.
    
    This class is designed to be used directly after task execution
    rather than through callbacks, which can be unreliable.
    """
    
    def __init__(self, artifact_service=None, jira_connector=None, with_jira=False):
        """
        Initialize the task output saver.
        
        Args:
            artifact_service: The artifact service to use for saving artifacts
            jira_connector: Optional JIRA connector for JIRA integration
            with_jira: Whether JIRA integration is enabled
        """
        self.artifact_service = artifact_service
        self.jira_connector = jira_connector
        self.with_jira = with_jira
        
        # Map of task descriptions to artifact types
        self.task_to_artifact_map = {}
        
        logger.info("Initialized TaskOutputSaver")
    
    def register_task(self, task_description, artifact_type, task_name=None):
        """
        Register a task for saving its output.
        
        Args:
            task_description: The description of the task (used for matching)
            artifact_type: The type of artifact to save
            task_name: Optional name for the task for display purposes
        """
        self.task_to_artifact_map[task_description] = {
            'artifact_type': artifact_type,
            'task_name': task_name or task_description[:20]
        }
        
        logger.info(f"Registered task for output saving: {task_description[:50]}...")
    
    def register_tasks(self, task_to_artifact):
        """
        Register multiple tasks for output saving.
        
        Args:
            task_to_artifact: List of (task, artifact_type, task_name) tuples
        """
        for task, artifact_type, task_name in task_to_artifact:
            self.register_task(task.description, artifact_type, task_name)
    
    def _extract_content(self, output):
        """
        Extract string content from various output formats.
        
        Args:
            output: The output from a task execution
            
        Returns:
            String content extracted from the output
        """
        try:
            # Handle different output formats
            if output is None:
                return "No output provided"
            
            if isinstance(output, str):
                return output
            
            # Handle CrewAI task output objects - avoid recursion
            if hasattr(output, 'raw_output'):
                raw_output = output.raw_output
                if isinstance(raw_output, str):
                    return raw_output
                else:
                    return str(raw_output)
            
            if hasattr(output, 'output'):
                output_attr = output.output
                if isinstance(output_attr, str):
                    return output_attr
                else:
                    return str(output_attr)
            
            if hasattr(output, 'result'):
                result = output.result
                if isinstance(result, str):
                    return result
                else:
                    return str(result)
            
            if hasattr(output, 'response'):
                response = output.response
                if isinstance(response, str):
                    return response
                else:
                    return str(response)
            
            if hasattr(output, 'content'):
                content = output.content
                if isinstance(content, str):
                    return content
                else:
                    return str(content)
            
            if hasattr(output, 'text'):
                text = output.text
                if isinstance(text, str):
                    return text
                else:
                    return str(text)
            
            # Check for task object - avoid recursion
            if hasattr(output, 'task'):
                task = output.task
                if hasattr(task, 'output') and task.output is not None:
                    task_output = task.output
                    if isinstance(task_output, str):
                        return task_output
                    else:
                        return str(task_output)
            
            # For objects that have a usable string representation
            return str(output)
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return f"Error extracting content: {e}"
    
    def save_output(self, task_description, output):
        """
        Save a task's output as an artifact.
        
        Args:
            task_description: The description of the task
            output: The output of the task
            
        Returns:
            The path to the saved artifact, or None if saving failed
        """
        if task_description not in self.task_to_artifact_map:
            logger.warning(f"Task description not registered: {task_description[:50]}...")
            return None
        
        if not self.artifact_service:
            logger.warning("No artifact service available")
            return None
        
        task_info = self.task_to_artifact_map[task_description]
        artifact_type = task_info['artifact_type']
        task_name = task_info['task_name']
        
        try:
            logger.info(f"Saving output for task: {task_name}")
            print(f"\nSaving artifact for {task_name}: {artifact_type}")
            
            # Extract content from the output
            content = self._extract_content(output)
            if not content:
                logger.warning(f"Empty content extracted for task: {task_name}")
                content = f"Empty content for {task_name}"
            
            # Save the artifact using the artifact service
            filepath = None
            if self.artifact_service:
                filepath = self.artifact_service.save_artifact(artifact_type, content)
                
                if filepath:
                    logger.info(f"Artifact saved to: {filepath}")
                    print(f"Artifact saved to: {filepath}")
                else:
                    logger.warning("Failed to save artifact")
                    print("Failed to save artifact")
                
                # Handle JIRA integration if needed
                if self.with_jira and self.jira_connector and artifact_type == "JIRA epics and stories":
                    try:
                        logger.info("Creating JIRA epics and stories...")
                        results = self.jira_connector.create_epics_and_stories(content)
                        if results["success"]:
                            logger.info(f"Created {len(results.get('epics', []))} epics and {len(results.get('stories', []))} stories in JIRA")
                        else:
                            logger.warning(f"Failed to create JIRA items: {results.get('error', 'Unknown error')}")
                    except Exception as e:
                        logger.error(f"Error creating JIRA items: {e}")
                
                return filepath
            
        except Exception as e:
            logger.error(f"Error saving artifact: {e}")
            print(f"Error saving artifact: {e}")
        
        return None
