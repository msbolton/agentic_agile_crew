"""
Unit tests for the ArtifactService class.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.artifacts.service import ArtifactService

class TestArtifactService(unittest.TestCase):
    """Test cases for the ArtifactService class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock artifact manager
        self.mock_manager = MagicMock()
        self.mock_manager.save_artifact.return_value = "/path/to/artifact.md"
        
        # Create service with mock manager
        self.service = ArtifactService(artifact_manager=self.mock_manager)
        
        # Set a product name for testing
        self.product_name = "Test Product"
        self.service.set_product_name(self.product_name)
    
    def test_init_with_manager(self):
        """Test initialization with artifact manager."""
        self.assertEqual(self.service.artifact_manager, self.mock_manager)
        self.assertFalse(self.service._callbacks_attached)
    
    def test_init_without_manager(self):
        """Test initialization without artifact manager."""
        service = ArtifactService()
        self.assertIsNone(service.artifact_manager)
    
    def test_set_product_name(self):
        """Test setting product name."""
        name = "New Product Name"
        self.service.set_product_name(name)
        self.assertEqual(self.service.product_name, name)
    
    def test_save_artifact_success(self):
        """Test successful artifact saving."""
        artifact_type = "requirements"
        content = "Test content"
        
        filepath = self.service.save_artifact(artifact_type, content)
        
        # Check that manager's save_artifact was called with correct parameters
        self.mock_manager.save_artifact.assert_called_once_with(
            self.product_name,
            artifact_type,
            content
        )
        
        # Check that the returned filepath is correct
        self.assertEqual(filepath, "/path/to/artifact.md")
    
    def test_save_artifact_no_manager(self):
        """Test saving artifact without manager."""
        service = ArtifactService()
        service.set_product_name("Test")
        
        filepath = service.save_artifact("requirements", "content")
        
        self.assertIsNone(filepath)
    
    def test_save_artifact_no_product_name(self):
        """Test saving artifact without product name."""
        service = ArtifactService(self.mock_manager)
        
        filepath = service.save_artifact("requirements", "content")
        
        self.assertIsNone(filepath)
        self.mock_manager.save_artifact.assert_not_called()
    
    def test_ensure_string_with_string(self):
        """Test _ensure_string with string input."""
        content = "Test string"
        result = self.service._ensure_string(content)
        self.assertEqual(result, content)
    
    def test_ensure_string_with_none(self):
        """Test _ensure_string with None input."""
        result = self.service._ensure_string(None)
        self.assertEqual(result, "None")
    
    def test_ensure_string_with_raw_output(self):
        """Test _ensure_string with object having raw_output."""
        obj = MagicMock()
        obj.raw_output = "Raw output content"
        
        result = self.service._ensure_string(obj)
        
        self.assertEqual(result, "Raw output content")
    
    def test_ensure_string_with_output(self):
        """Test _ensure_string with object having output."""
        obj = MagicMock()
        obj.raw_output = None
        obj.output = "Output content"
        
        result = self.service._ensure_string(obj)
        
        self.assertEqual(result, "Output content")
    
    def test_ensure_string_with_result(self):
        """Test _ensure_string with object having result."""
        obj = MagicMock()
        obj.raw_output = None
        obj.output = None
        obj.result = "Result content"
        
        result = self.service._ensure_string(obj)
        
        self.assertEqual(result, "Result content")
    
    def test_ensure_string_with_response(self):
        """Test _ensure_string with object having response."""
        obj = MagicMock()
        obj.raw_output = None
        obj.output = None
        obj.result = None
        obj.response = "Response content"
        
        result = self.service._ensure_string(obj)
        
        self.assertEqual(result, "Response content")
    
    def test_ensure_string_with_content(self):
        """Test _ensure_string with object having content."""
        obj = MagicMock()
        obj.raw_output = None
        obj.output = None
        obj.result = None
        obj.response = None
        obj.content = "Content attribute"
        
        result = self.service._ensure_string(obj)
        
        self.assertEqual(result, "Content attribute")
    
    def test_ensure_string_with_other_object(self):
        """Test _ensure_string with generic object."""
        obj = MagicMock()
        obj.__str__.return_value = "String representation"
        
        result = self.service._ensure_string(obj)
        
        self.assertEqual(result, "String representation")
    
    def test_ensure_string_with_exception(self):
        """Test _ensure_string when an exception occurs."""
        obj = MagicMock()
        obj.__str__.side_effect = Exception("Test exception")
        
        result = self.service._ensure_string(obj)
        
        self.assertTrue(result.startswith("Error converting content to string:"))

if __name__ == '__main__':
    unittest.main()
