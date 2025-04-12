"""
Task Callbacks for Agentic Agile Crew

This module provides callbacks for task execution to enable immediate artifact
saving and other post-task actions without waiting for the entire workflow to complete.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Callable
import inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("task_callbacks")

class ImmediateArtifactCallback:
    """
    Callback that saves artifacts immediately upon task completion.
    
    This class creates callbacks that capture task outputs and save them
    as artifacts as soon as they are produced, rather than waiting for
    the entire workflow to finish.
    """
    
    def __init__(self, task, artifact_service, artifact_type, stage_name, jira_connector=None, with_jira=False):
        """
        Initialize the immediate artifact callback.
        
        Args:
            task: The task object this callback is associated with
            artifact_service: Service for saving artifacts
            artifact_type: Type of artifact (e.g., "requirements", "architecture")
            stage_name: Name of the workflow stage
            jira_connector: Optional connector for JIRA integration
            with_jira: Whether JIRA integration is enabled
        """
        self.task = task
        self.artifact_service = artifact_service
        self.artifact_type = artifact_type
        self.stage_name = stage_name
        self.jira_connector = jira_connector
        self.with_jira = with_jira
    
    def __call__(self, task_output):
        """
        The callback function executed when the task completes.
        
        Args:
            task_output: The output from the task
            
        Returns:
            The original task output (to allow chaining callbacks)
        """
        logger.info(f"Task '{self.stage_name}' completed, saving artifact...")
        
        # Extract the output content from various possible formats
        content = self._extract_content(task_output)
        
        if content and self.artifact_service:
            try:
                # Save the artifact
                filepath = self.artifact_service.save_artifact(self.artifact_type, content)
                logger.info(f"Saved '{self.stage_name}' artifact to {filepath}")
                print(f"✅ Saved artifact for '{self.stage_name}'")
                
                # Special handling for JIRA if needed
                if (self.with_jira and 
                    self.jira_connector and 
                    self.artifact_type == "JIRA epics and stories"):
                    try:
                        logger.info(f"Creating JIRA items from '{self.stage_name}' output")
                        results = self.jira_connector.create_epics_and_stories(content)
                        if results.get("success"):
                            logger.info(
                                f"Created {len(results.get('epics', []))} epics and "
                                f"{len(results.get('stories', []))} stories in JIRA"
                            )
                            print(f"✅ Created JIRA items from '{self.stage_name}' output")
                        else:
                            logger.warning(f"Failed to create JIRA items: {results.get('error')}")
                            print(f"❌ Failed to create JIRA items: {results.get('error')}")
                    except Exception as e:
                        logger.error(f"Error creating JIRA items: {e}")
                        print(f"❌ Error creating JIRA items: {e}")
            except Exception as e:
                logger.error(f"Error saving artifact for '{self.stage_name}': {e}")
                print(f"❌ Failed to save artifact for '{self.stage_name}': {e}")
        
        # Return the original output to allow callback chaining
        return task_output
    
    def _extract_content(self, task_output):
        """
        Extract content from various task output formats.
        
        Args:
            task_output: The output from the task
            
        Returns:
            The extracted content as a string, or None if extraction fails
        """
        try:
            # Log the type of task_output for debugging
            logger.info(f"Task output type: {type(task_output)}")
            
            # Handle different potential formats
            if task_output is None:
                return "No output provided"
                
            if isinstance(task_output, str):
                logger.info("Task output is already a string")
                return task_output
            
            # Handle different attributes - avoid recursion
            if hasattr(task_output, 'raw_output'):
                raw_output = task_output.raw_output
                logger.info("Extracted content from raw_output attribute")
                if isinstance(raw_output, str):
                    return raw_output
                else:
                    return str(raw_output)
            
            elif hasattr(task_output, 'output'):
                output_attr = task_output.output
                logger.info("Extracted content from output attribute")
                if isinstance(output_attr, str):
                    return output_attr
                else:
                    return str(output_attr)
            
            elif hasattr(task_output, 'result'):
                result = task_output.result
                logger.info("Extracted content from result attribute")
                if isinstance(result, str):
                    return result
                else:
                    return str(result)
            
            elif hasattr(task_output, 'response'):
                response = task_output.response
                logger.info("Extracted content from response attribute")
                if isinstance(response, str):
                    return response
                else:
                    return str(response)
            
            elif hasattr(task_output, 'content'):
                content_attr = task_output.content
                logger.info("Extracted content from content attribute")
                if isinstance(content_attr, str):
                    return content_attr
                else:
                    return str(content_attr)
            
            # Try string conversion
            content = str(task_output)
            logger.info(f"Converted task output to string: {type(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from task output: {e}")
            return f"Error extracting content from task output: {e}"

def create_callbacks_for_tasks(tasks, artifact_service, jira_connector=None, with_jira=False):
    """
    Create and attach immediate artifact saving callbacks for a list of tasks.
    
    Args:
        tasks: List of (task, artifact_type, stage_name) tuples
        artifact_service: Service for saving artifacts
        jira_connector: Optional connector for JIRA integration
        with_jira: Whether JIRA integration is enabled
        
    Returns:
        List of tasks with callbacks attached
    """
    logger.info(f"Creating immediate artifact saving callbacks for {len(tasks)} tasks")
    
    # Flag to track if callbacks were added successfully
    callbacks_attached = False
    
    for task_info in tasks:
        task = task_info[0]
        artifact_type = task_info[1]
        stage_name = task_info[2]
        
        # Create the callback
        callback = ImmediateArtifactCallback(
            task=task,
            artifact_service=artifact_service,
            artifact_type=artifact_type,
            stage_name=stage_name,
            jira_connector=jira_connector,
            with_jira=with_jira
        )
        
        # Try different methods to attach the callback
        attached = False
        
        # Method 1: Use add_callback method if available
        if hasattr(task, 'add_callback') and callable(getattr(task, 'add_callback')):
            try:
                task.add_callback(callback)
                logger.info(f"Added callback to task '{stage_name}' using add_callback method")
                attached = True
                callbacks_attached = True
            except Exception as e:
                logger.warning(f"Failed to add callback using add_callback method: {e}")
        
        # Method 2: Append to callbacks list if available
        if not attached and hasattr(task, 'callbacks') and isinstance(task.callbacks, list):
            try:
                task.callbacks.append(callback)
                logger.info(f"Added callback to task '{stage_name}' using callbacks list")
                attached = True
                callbacks_attached = True
            except Exception as e:
                logger.warning(f"Failed to add callback using callbacks list: {e}")
        
        # Method 3: Use on_output handler if available
        if not attached and hasattr(task, 'on_output'):
            try:
                original_on_output = task.on_output
                def combined_handler(output):
                    result = original_on_output(output) if callable(original_on_output) else output
                    return callback(result)
                task.on_output = combined_handler
                logger.info(f"Added callback to task '{stage_name}' using on_output handler")
                attached = True
                callbacks_attached = True
            except Exception as e:
                logger.warning(f"Failed to add callback using on_output handler: {e}")
        
        # Method 4: Try to patch the execute method as a last resort
        if not attached:
            try:
                # Get the original execute method if it exists
                if hasattr(task, 'execute') and callable(getattr(task, 'execute')):
                    original_execute = task.execute
                    
                    # Define patched execute method
                    def patched_execute(*args, **kwargs):
                        result = original_execute(*args, **kwargs)
                        logger.info(f"Execute method intercepted for '{stage_name}'")
                        processed_result = callback(result)
                        return processed_result
                    
                    # Replace the execute method
                    task.execute = patched_execute
                    logger.info(f"Added callback to task '{stage_name}' by monkey patching execute method")
                    attached = True
                    callbacks_attached = True
            except Exception as e:
                logger.warning(f"Failed to patch execute method: {e}")
        
        if not attached:
            logger.error(f"Could not attach callback to task '{stage_name}'")
    
    if callbacks_attached:
        # Mark the TaskOutputSaver as having callbacks attached
        if artifact_service and hasattr(artifact_service, '_callbacks_attached'):
            artifact_service._callbacks_attached = True
        logger.info("Successfully attached callbacks to tasks")
    else:
        logger.warning("Failed to attach callbacks to any tasks")
    
    return [task_info[0] for task_info in tasks]
