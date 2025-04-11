"""
Storage utilities for human-in-the-loop functionality
"""

import os
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("human_review.storage")

class StorageManager:
    """
    Manages persistent storage for human-in-the-loop data
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize storage manager
        
        Args:
            base_dir: Base directory for storage
        """
        self.base_dir = base_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.base_dir, exist_ok=True)
        logger.debug(f"Ensured storage directory exists: {self.base_dir}")
    
    def save_json(self, filename: str, data: Any) -> bool:
        """
        Save data as JSON to the specified file
        
        Args:
            filename: Name of the file to save to
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.base_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            return False
    
    def load_json(self, filename: str, default: Any = None) -> Any:
        """
        Load JSON data from the specified file
        
        Args:
            filename: Name of the file to load from
            default: Default value to return if file doesn't exist
            
        Returns:
            Loaded data or default value
        """
        filepath = os.path.join(self.base_dir, filename)
        if not os.path.exists(filepath):
            logger.debug(f"File doesn't exist, returning default: {filepath}")
            return default
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.debug(f"Loaded data from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error loading data from {filepath}: {e}")
            return default
    
    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in the storage directory"""
        filepath = os.path.join(self.base_dir, filename)
        return os.path.exists(filepath)
    
    def list_files(self) -> List[str]:
        """List all files in the storage directory"""
        return [f for f in os.listdir(self.base_dir) if os.path.isfile(os.path.join(self.base_dir, f))]
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from the storage directory
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.base_dir, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Deleted file: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
            return False
