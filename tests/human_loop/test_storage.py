"""
Unit tests for the StorageManager in src.human_loop.storage
"""

import os
import json
import tempfile
import shutil
from unittest import TestCase, mock
import pytest

from src.human_loop.storage import StorageManager


class TestStorageManager(TestCase):
    """Test cases for StorageManager class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = StorageManager(self.temp_dir)
        
    def tearDown(self):
        """Clean up temporary directory after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_init_creates_directory(self):
        """Test that the constructor creates the storage directory if it doesn't exist"""
        # Remove the directory created in setUp
        shutil.rmtree(self.temp_dir)
        
        # Verify directory doesn't exist
        self.assertFalse(os.path.exists(self.temp_dir))
        
        # Initialize the storage manager
        StorageManager(self.temp_dir)
        
        # Verify directory was created
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_save_json(self):
        """Test saving JSON data to a file"""
        # Test data
        data = {"key": "value", "nested": {"foo": "bar"}}
        filename = "test_save.json"
        
        # Save the data
        result = self.storage.save_json(filename, data)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the file exists
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        
        # Verify the content
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, data)
    
    def test_save_json_failure(self):
        """Test handling of errors when saving JSON"""
        # Set up mock to simulate write error
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("Simulated write error")
        
        # Test with the mock
        with mock.patch('builtins.open', mock_open):
            result = self.storage.save_json("test_error.json", {"data": "value"})
            
            # Verify the result
            self.assertFalse(result)
    
    def test_load_json(self):
        """Test loading JSON data from a file"""
        # Test data
        data = {"key": "value", "number": 42}
        filename = "test_load.json"
        
        # Write test data to file
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        # Load the data
        loaded_data = self.storage.load_json(filename)
        
        # Verify the loaded data
        self.assertEqual(loaded_data, data)
    
    def test_load_json_nonexistent_file(self):
        """Test loading from a file that doesn't exist"""
        # Try to load a file that doesn't exist
        default_value = {"default": "value"}
        loaded_data = self.storage.load_json("nonexistent.json", default_value)
        
        # Verify default value is returned
        self.assertEqual(loaded_data, default_value)
    
    def test_load_json_failure(self):
        """Test handling of errors when loading JSON"""
        # Create an invalid JSON file
        filename = "invalid.json"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write("{invalid json")
        
        # Try to load the invalid file
        default_value = {"default": "value"}
        loaded_data = self.storage.load_json(filename, default_value)
        
        # Verify default value is returned
        self.assertEqual(loaded_data, default_value)
    
    def test_file_exists(self):
        """Test checking if a file exists"""
        # Create a test file
        filename = "exists.json"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write("{}")
        
        # Check existing file
        self.assertTrue(self.storage.file_exists(filename))
        
        # Check non-existent file
        self.assertFalse(self.storage.file_exists("nonexistent.json"))
    
    def test_list_files(self):
        """Test listing files in the storage directory"""
        # Create test files
        files = ["file1.json", "file2.json", "file3.txt"]
        for filename in files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("")
        
        # List files
        listed_files = self.storage.list_files()
        
        # Verify all files are listed
        for filename in files:
            self.assertIn(filename, listed_files)
        
        # Verify count matches
        self.assertEqual(len(listed_files), len(files))
    
    def test_delete_file(self):
        """Test deleting a file"""
        # Create a test file
        filename = "to_delete.json"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write("{}")
        
        # Verify file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Delete the file
        result = self.storage.delete_file(filename)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify file no longer exists
        self.assertFalse(os.path.exists(filepath))
    
    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist"""
        # Try to delete a non-existent file
        result = self.storage.delete_file("nonexistent.json")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_delete_file_failure(self):
        """Test handling of errors when deleting a file"""
        # Create a test file
        filename = "error_delete.json"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write("{}")
        
        # Set up mock to simulate delete error
        with mock.patch('os.remove') as mock_remove:
            mock_remove.side_effect = OSError("Simulated delete error")
            
            # Try to delete the file
            result = self.storage.delete_file(filename)
            
            # Verify the result
            self.assertFalse(result)
