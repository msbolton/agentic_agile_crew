"""
Unit tests for the formatter utilities in src.human_loop.formatter
"""

import os
import json
from unittest import TestCase, mock
import pytest

from src.human_loop.formatter import (
    Colors, get_terminal_width, format_title, format_heading,
    format_subheading, format_key_value, format_separator,
    format_content, truncate_str, success_message, error_message,
    warning_message, wrap_text, format_approval_status
)


class TestFormatter(TestCase):
    """Test cases for formatter utilities"""
    
    def test_colors_constants(self):
        """Test that color constants are defined"""
        # Verify some color constants
        self.assertTrue(hasattr(Colors, 'RESET'))
        self.assertTrue(hasattr(Colors, 'BOLD'))
        self.assertTrue(hasattr(Colors, 'GREEN'))
        self.assertTrue(hasattr(Colors, 'RED'))
    
    def test_get_terminal_width(self):
        """Test getting terminal width"""
        # Mock os.get_terminal_size
        with mock.patch('os.get_terminal_size', return_value=(80, 24)):
            width = get_terminal_width()
            self.assertEqual(width, 80)
        
        # Test fallback when terminal size can't be determined
        with mock.patch('os.get_terminal_size', side_effect=OSError):
            width = get_terminal_width()
            self.assertEqual(width, 80)  # Default value
    
    def test_format_title(self):
        """Test formatting a title"""
        title = "Test Title"
        formatted = format_title(title)
        
        # Verify formatting
        self.assertIn(Colors.BOLD, formatted)
        self.assertIn(Colors.CYAN, formatted)
        self.assertIn(title.upper(), formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_format_heading(self):
        """Test formatting a heading"""
        heading = "Test Heading"
        formatted = format_heading(heading)
        
        # Verify formatting
        self.assertIn(Colors.BOLD, formatted)
        self.assertIn(Colors.YELLOW, formatted)
        self.assertIn(heading, formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_format_subheading(self):
        """Test formatting a subheading"""
        subheading = "Test Subheading"
        formatted = format_subheading(subheading)
        
        # Verify formatting
        self.assertIn(Colors.BOLD, formatted)
        self.assertIn(subheading, formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_format_key_value(self):
        """Test formatting a key-value pair"""
        key = "Key"
        value = "Value"
        formatted = format_key_value(key, value)
        
        # Verify formatting
        self.assertIn(Colors.BOLD, formatted)
        self.assertIn(key, formatted)
        self.assertIn(value, formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_format_separator(self):
        """Test creating a separator line"""
        # Mock terminal width
        with mock.patch('src.human_loop.formatter.get_terminal_width', return_value=10):
            # Default separator
            separator = format_separator()
            self.assertEqual(separator, "-" * 10)
            
            # Custom separator
            separator = format_separator("=")
            self.assertEqual(separator, "=" * 10)
    
    def test_format_content_dict(self):
        """Test formatting dictionary content"""
        content = {"key": "value", "nested": {"foo": "bar"}}
        formatted = format_content(content)
        
        # Verify JSON formatting
        expected = json.dumps(content, indent=2)
        self.assertEqual(formatted, expected)
    
    def test_format_content_string(self):
        """Test formatting string content"""
        content = "Test string content"
        formatted = format_content(content)
        
        # Verify string is returned as is
        self.assertEqual(formatted, content)
    
    def test_format_content_other(self):
        """Test formatting other content types"""
        content = 123
        formatted = format_content(content)
        
        # Verify string conversion
        self.assertEqual(formatted, "123")
    
    def test_truncate_str(self):
        """Test truncating a string"""
        # String shorter than max length
        short_str = "Short string"
        truncated = truncate_str(short_str, 20)
        self.assertEqual(truncated, short_str)
        
        # String longer than max length
        long_str = "This is a very long string that needs truncation"
        truncated = truncate_str(long_str, 20)
        self.assertEqual(truncated, "This is a very long ...")
        self.assertEqual(len(truncated), 23)  # 20 chars + 3 for ellipsis
    
    def test_success_message(self):
        """Test formatting a success message"""
        message = "Success message"
        formatted = success_message(message)
        
        # Verify formatting
        self.assertIn(Colors.GREEN, formatted)
        self.assertIn(message, formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_error_message(self):
        """Test formatting an error message"""
        message = "Error message"
        formatted = error_message(message)
        
        # Verify formatting
        self.assertIn(Colors.RED, formatted)
        self.assertIn(message, formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_warning_message(self):
        """Test formatting a warning message"""
        message = "Warning message"
        formatted = warning_message(message)
        
        # Verify formatting
        self.assertIn(Colors.YELLOW, formatted)
        self.assertIn(message, formatted)
        self.assertIn(Colors.RESET, formatted)
    
    def test_wrap_text(self):
        """Test wrapping text"""
        # Create a long text
        long_text = "This is a very long text that needs to be wrapped to multiple lines to fit the terminal width."
        
        # Wrap with specific width
        wrapped = wrap_text(long_text, width=20)
        
        # Verify wrapping
        lines = wrapped.split('\n')
        self.assertGreater(len(lines), 1)
        self.assertLessEqual(max(len(line) for line in lines), 20)
        
        # Wrap with default width (using terminal width)
        with mock.patch('src.human_loop.formatter.get_terminal_width', return_value=40):
            wrapped = wrap_text(long_text)
            lines = wrapped.split('\n')
            self.assertLessEqual(max(len(line) for line in lines), 38)  # 40 - 2 margin
    
    def test_format_approval_status(self):
        """Test formatting approval status"""
        # Approved status
        approved = format_approval_status("approved")
        self.assertIn(Colors.GREEN, approved)
        self.assertIn("Approved", approved)
        
        # Rejected status
        rejected = format_approval_status("rejected")
        self.assertIn(Colors.RED, rejected)
        self.assertIn("Rejected", rejected)
        
        # Pending status
        pending = format_approval_status("pending")
        self.assertIn(Colors.YELLOW, pending)
        self.assertIn("Pending", pending)
        
        # Unknown status
        unknown = format_approval_status("unknown")
        self.assertIn(Colors.YELLOW, unknown)
        self.assertIn("Pending", unknown)
