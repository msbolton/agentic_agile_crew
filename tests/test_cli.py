"""
Unit tests for the CLI interface
"""

import os
import tempfile
import shutil
import sys
from unittest import TestCase, mock
import pytest
import argparse

# We need to import the CLI module but avoid executing main()
# Save the original argv and patch sys.argv
original_argv = sys.argv
sys.argv = ["cli.py"]

# Import CLI module
import cli

# Restore original argv
sys.argv = original_argv


class TestCLI(TestCase):
    """Test cases for CLI interface"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test product idea file
        self.idea_file = os.path.join(self.temp_dir, "test_idea.md")
        with open(self.idea_file, "w") as f:
            f.write("# Test Product Idea\n\nThis is a test product idea for unit testing.")
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_cli_parser(self):
        """Test the CLI argument parser"""
        # Test with no arguments
        with mock.patch("sys.argv", ["cli.py"]):
            with mock.patch("argparse.ArgumentParser.print_help") as mock_help:
                cli.main()
                # When no arguments are provided, print_help should be called
                mock_help.assert_called_once()
    
    def test_clear_screen(self):
        """Test the clear_screen function"""
        with mock.patch("os.system") as mock_system:
            cli.clear_screen()
            # Should call os.system with clear command
            mock_system.assert_called_once()
    
    def test_list_reviews_empty(self):
        """Test listing reviews when none exist"""
        # Mock review_manager.get_pending_reviews to return empty list
        with mock.patch.object(cli.review_manager, "get_pending_reviews", return_value=[]):
            with mock.patch("builtins.print") as mock_print:
                args = argparse.Namespace()
                cli.list_reviews(args)
                
                # Verify "No pending reviews" message
                mock_print.assert_any_call("\nNo pending reviews.")
    
    def test_list_completed_empty(self):
        """Test listing completed reviews when none exist"""
        # Mock review_manager.get_completed_reviews to return empty list
        with mock.patch.object(cli.review_manager, "get_completed_reviews", return_value=[]):
            with mock.patch("builtins.print") as mock_print:
                args = argparse.Namespace()
                cli.list_completed(args)
                
                # Verify "No completed reviews" message
                mock_print.assert_any_call("\nNo completed reviews.")
    
    def test_project_status(self):
        """Test project status display"""
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace()
            cli.project_status(args)
            
            # Verify status display
            mock_print.assert_any_call(mock.ANY)  # Title
            mock_print.assert_any_call(mock.ANY)  # Separator
