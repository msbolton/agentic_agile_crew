"""
Artifact Saving Service for Agentic Agile Crew

This module provides a service for saving artifacts produced by
the different agents in the workflow, independent of the human review process.
"""

from typing import Optional, Any

from src.artifacts.manager import ArtifactManager
from src.utils.logger import setup_logger

# Configure logger
logger = setup_logger("artifact_service")

class ArtifactService:
    """
    Service for saving artifacts produced during the development workflow.
    """
    
    def __init__(self, artifact_manager: Optional[ArtifactManager] = None):
        """
        Initialize the artifact service.
        
        Args:
            artifact_manager: The artifact manager to use for saving artifacts
        """
        self.artifact_manager = artifact_manager
        self.product_name = None
        # Flag to track whether callbacks are attached
        self._callbacks_attached = False
        
        logger.info("Initialized ArtifactService")
        if artifact_manager:
            logger.debug(f"Using ArtifactManager with base directory: {artifact_manager.base_dir}")
        else:
            logger.warning("No ArtifactManager provided, artifacts won't be saved")
    
    def set_product_name(self, name: str):
        """
        Set the product name for artifact organization.
        
        Args:
            name: The product name
        """
        self.product_name = name
        logger.info(f"Set product name: {name}")
    
    def save_artifact(self, artifact_type: str, content: Any) -> Optional[str]:
        """
        Save an artifact.
        
        Args:
            artifact_type: The type of artifact
            content: The content of the artifact (string or object with string representation)
            
        Returns:
            The path to the saved artifact, or None if saving failed
        """
        if not self.artifact_manager:
            logger.warning("Artifact manager not available, skipping save")
            return None
        
        if not self.product_name:
            logger.warning("Product name not set, skipping save")
            return None
        
        try:
            # Ensure content is a string
            content_str = self._ensure_string(content)
            
            if not content_str:
                logger.error("Failed to convert content to string")
                return None
            
            logger.info(f"Saving artifact of type '{artifact_type}' with {len(content_str)} characters")
            
            filepath = self.artifact_manager.save_artifact(
                self.product_name,
                artifact_type,
                content_str
            )
            logger.info(f"Saved artifact: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving artifact: {e}", exc_info=True)
            return None
    
    def _ensure_string(self, content: Any) -> str:
        """
        Ensure content is a string.
        
        Args:
            content: The content to convert to a string
            
        Returns:
            String representation of the content
        """
        # Handle None case
        if content is None:
            logger.debug("Converting None content to string")
            return "None"
            
        # Already a string
        if isinstance(content, str):
            logger.debug("Content is already a string")
            return content
        
        # Handle various object types - avoid recursion
        try:
            logger.debug(f"Converting object of type {type(content).__name__} to string")
            
            # Direct checks for specific attributes to avoid recursion
            if hasattr(content, 'raw_output'):
                raw_output = content.raw_output
                logger.debug("Using 'raw_output' attribute")
                if isinstance(raw_output, str):
                    return raw_output
                else:
                    return str(raw_output)
                    
            elif hasattr(content, 'output'):
                output = content.output
                logger.debug("Using 'output' attribute")
                if isinstance(output, str):
                    return output
                else:
                    return str(output)
                    
            elif hasattr(content, 'result'):
                result = content.result
                logger.debug("Using 'result' attribute")
                if isinstance(result, str):
                    return result
                else:
                    return str(result)
                    
            elif hasattr(content, 'response'):
                response = content.response
                logger.debug("Using 'response' attribute")
                if isinstance(response, str):
                    return response
                else:
                    return str(response)
                    
            elif hasattr(content, 'content'):
                content_attr = content.content
                logger.debug("Using 'content' attribute")
                if isinstance(content_attr, str):
                    return content_attr
                else:
                    return str(content_attr)
            
            # Fallback to string conversion
            logger.debug("Using fallback str() conversion")
            return str(content)
            
        except Exception as e:
            logger.error(f"Error converting content to string: {e}", exc_info=True)
            return f"Error converting content: {e}"
