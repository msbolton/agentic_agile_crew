"""
Unit tests for the logger module.
"""

import unittest
import os
import shutil
import logging
import tempfile
from unittest.mock import patch, MagicMock
from src.utils.logger import setup_logger, LOG_DIR

class TestLogger(unittest.TestCase):
    """Test cases for the logger module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp()
        self.original_log_dir = LOG_DIR
        
        # Patch the LOG_DIR
        self.patcher = patch('src.utils.logger.LOG_DIR', self.test_log_dir)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        self.patcher.stop()
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
    
    def test_setup_logger_creates_log_dir(self):
        """Test that setup_logger creates the log directory if it doesn't exist."""
        # Remove the test log directory
        shutil.rmtree(self.test_log_dir)
        
        # Create logger
        logger = setup_logger("test_logger")
        
        # Check that directory was created
        self.assertTrue(os.path.exists(self.test_log_dir))
    
    def test_setup_logger_file_handler(self):
        """Test that setup_logger adds a file handler."""
        logger = setup_logger("test_file_handler")
        
        # Check that file handler was added
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        self.assertEqual(len(file_handlers), 1)
        
        # Check log file path
        expected_path = os.path.join(self.test_log_dir, "test_file_handler.log")
        self.assertEqual(file_handlers[0].baseFilename, expected_path)
    
    def test_setup_logger_console_handler(self):
        """Test that setup_logger adds a console handler."""
        logger = setup_logger("test_console_handler")
        
        # Check that console handler was added
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler)]
        self.assertEqual(len(console_handlers), 1)
    
    def test_setup_logger_log_level(self):
        """Test that setup_logger sets the correct log level."""
        logger = setup_logger("test_log_level", level=logging.DEBUG)
        
        self.assertEqual(logger.level, logging.DEBUG)
    
    def test_setup_logger_custom_log_file(self):
        """Test setup_logger with a custom log file path."""
        custom_path = os.path.join(self.test_log_dir, "custom.log")
        
        logger = setup_logger("test_custom_file", log_file=custom_path)
        
        # Check that file handler uses custom path
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        self.assertEqual(file_handlers[0].baseFilename, custom_path)
    
    def test_logger_writes_to_file(self):
        """Test that logger actually writes to the log file."""
        logger_name = "test_write"
        log_path = os.path.join(self.test_log_dir, f"{logger_name}.log")
        
        # Create logger and write a message
        logger = setup_logger(logger_name)
        test_message = "Test log message"
        logger.info(test_message)
        
        # Check that file exists and contains the message
        self.assertTrue(os.path.exists(log_path))
        
        with open(log_path, 'r') as f:
            content = f.read()
        
        self.assertIn(test_message, content)
    
    def test_rotation_settings(self):
        """Test that rotation settings are correctly applied."""
        logger = setup_logger("test_rotation")
        
        # Get the file handler
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        handler = file_handlers[0]
        
        # Check rotation settings
        self.assertEqual(handler.maxBytes, 10 * 1024 * 1024)  # 10 MB
        self.assertEqual(handler.backupCount, 5)

if __name__ == '__main__':
    unittest.main()
