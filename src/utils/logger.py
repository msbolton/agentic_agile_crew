"""
Logger module for Agentic Agile Crew

Provides centralized logging configuration with rotating file handlers
and console output.
"""

import os
import logging
import logging.handlers
import sys
from datetime import datetime
from typing import Optional

# Default log directory
LOG_DIR = "logs"

# Log levels from environment variable or default to INFO
LOG_LEVEL_NAME = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

# Log file settings
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Singleton to track if logger is already configured
_logger_configured = False

def setup_logger(name: str, log_file: Optional[str] = None, level: int = LOG_LEVEL) -> logging.Logger:
    """
    Set up a logger with both console and file handlers using rotation.
    
    Args:
        name: Logger name
        log_file: Log file path (optional, will use name if not provided)
        level: Logging level (default based on environment variable or INFO)
        
    Returns:
        Configured logger instance
    """
    global _logger_configured
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create formatters
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if not log_file:
        # Create logs directory if it doesn't exist
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        # Use logger name for file name
        safe_name = name.replace(".", "_").lower()
        log_file = os.path.join(LOG_DIR, f"{safe_name}.log")
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Log initial message
    if not _logger_configured:
        logger.info(f"Logging initialized at {datetime.now().strftime(DATE_FORMAT)}")
        logger.info(f"Log level set to {LOG_LEVEL_NAME}")
        _logger_configured = True
    
    return logger

# Create a default logger for imports
logger = setup_logger("agentic_agile_crew")

# Example usage:
# from src.utils.logger import setup_logger
# logger = setup_logger(__name__)
