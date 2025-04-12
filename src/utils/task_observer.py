"""
Task observer pattern for tracking task execution and saving artifacts.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from crewai import Task

logger = logging.getLogger("task_observer")

class TaskWrapper:
    """
    Wrapper for a Task that delegates to the original task but adds a callback.
    
    This approach avoids modifying the Task object directly, which is a Pydantic model
    and doesn't allow setting attributes that aren't defined fields.
    """
    
    def __init__(self, original_task: Task, callback: Callable[[str], None], name: str = None):
        """
        Initialize the task wrapper.
        
        Args:
            original_task: The original task to wrap
            callback: The callback to invoke when the task completes
            name: Optional name for the task for logging
        """
        self.original_task = original_task
        self.callback = callback
        self.name = name or f"Task {id(original_task)}"
        
        # Copy all attributes from the original task
        for attr in dir(original_task):
            if not attr.startswith('_') and attr != 'execute' and not callable(getattr(original_task, attr)):
                setattr(self, attr, getattr(original_task, attr))
    
    def execute(self, *args, **kwargs):
        """
        Execute the original task and then invoke the callback.
        """
        logger.info(f"Executing wrapped task: {self.name}")
        
        # Execute the original task
        result = self.original_task.execute(*args, **kwargs)
        
        logger.info(f"Task completed: {self.name}")
        
        # Call the callback with the result
        try:
            self.callback(result)
        except Exception as e:
            logger.error(f"Error in task callback: {e}")
        
        # Return the original result
        return result


class TaskObserver:
    """
    Observer for task execution that can trigger actions when tasks complete.
    
    Follows the Observer pattern to decouple task execution from artifact saving.
    """
    
    def __init__(self):
        """Initialize the task observer"""
        self.wrapped_tasks = {}
    
    def wrap_task(self, task: Task, callback: Callable[[str], None], task_name: str = None) -> TaskWrapper:
        """
        Create a wrapped version of the task with an associated callback.
        
        Args:
            task: The task to wrap
            callback: The callback to invoke when the task completes
            task_name: Optional name for the task for logging
            
        Returns:
            The wrapped task
        """
        task_id = id(task)
        task_display_name = task_name or f"Task {task_id}"
        
        # Create a wrapper for the task
        wrapped_task = TaskWrapper(task, callback, task_display_name)
        
        # Store the wrapped task for reference
        self.wrapped_tasks[task_id] = wrapped_task
        
        logger.info(f"Created wrapper for task: {task_display_name}")
        
        return wrapped_task
