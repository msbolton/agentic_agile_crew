"""
Unit tests for the ArtifactManager class.
"""

import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from src.artifacts.manager import ArtifactManager

class TestArtifactManager(unittest.TestCase):
    """Test cases for the ArtifactManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a test directory for artifacts during tests
        self.test_base_dir = "test_artifacts"
        self.manager = ArtifactManager(base_dir=self.test_base_dir)
        
        # Create a product idea name for testing
        self.product_name = "Test Product Idea"
        self.expected_dir_name = "test_product_idea"
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove test directory after tests
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)
    
    def test_init_default_base_dir(self):
        """Test initialization with default base directory."""
        manager = ArtifactManager()
        self.assertEqual(manager.base_dir, "dist")
    
    def test_init_custom_base_dir(self):
        """Test initialization with custom base directory."""
        custom_dir = "custom_artifacts"
        manager = ArtifactManager(base_dir=custom_dir)
        self.assertEqual(manager.base_dir, custom_dir)
        
        # Clean up
        if os.path.exists(custom_dir):
            shutil.rmtree(custom_dir)
    
    def test_ensure_base_dir_exists(self):
        """Test that base directory is created."""
        self.assertTrue(os.path.exists(self.test_base_dir))
    
    def test_sanitize_directory_name(self):
        """Test directory name sanitization."""
        # Test with spaces and special characters
        name = "Test Product! With @#$ Special Characters"
        expected = "test_product_with_special_characters"
        self.assertEqual(self.manager.sanitize_directory_name(name), expected)
        
        # Test with markdown heading
        name = "# Product Heading"
        expected = "product_heading"
        self.assertEqual(self.manager.sanitize_directory_name(name), expected)
        
        # Test with multiline content
        name = "First Line\nSecond Line\nThird Line"
        expected = "first_line"
        self.assertEqual(self.manager.sanitize_directory_name(name), expected)
    
    def test_create_project_directory(self):
        """Test project directory creation."""
        project_dir = self.manager.create_project_directory(self.product_name)
        expected_path = os.path.join(self.test_base_dir, self.expected_dir_name)
        
        self.assertEqual(project_dir, expected_path)
        self.assertTrue(os.path.exists(project_dir))
    
    def test_save_artifact(self):
        """Test saving an artifact."""
        artifact_type = "requirements"
        content = "Test content for requirements"
        
        filepath = self.manager.save_artifact(self.product_name, artifact_type, content)
        expected_path = os.path.join(self.test_base_dir, self.expected_dir_name, "business_requirements.md")
        
        self.assertEqual(filepath, expected_path)
        self.assertTrue(os.path.exists(filepath))
        
        # Check content was written correctly
        with open(filepath, 'r') as f:
            saved_content = f.read()
        
        self.assertEqual(saved_content, content)
    
    def test_save_artifact_unknown_type(self):
        """Test saving an artifact with unknown type."""
        artifact_type = "custom_type"
        content = "Test content for custom type"
        
        filepath = self.manager.save_artifact(self.product_name, artifact_type, content)
        expected_path = os.path.join(self.test_base_dir, self.expected_dir_name, "custom_type.md")
        
        self.assertEqual(filepath, expected_path)
        self.assertTrue(os.path.exists(filepath))
    
    def test_get_artifact_path(self):
        """Test getting an artifact path."""
        artifact_type = "requirements"
        
        path = self.manager.get_artifact_path(self.product_name, artifact_type)
        expected_path = os.path.join(self.test_base_dir, self.expected_dir_name, "business_requirements.md")
        
        self.assertEqual(path, expected_path)
    
    def test_list_artifacts(self):
        """Test listing artifacts."""
        # Save a couple of artifacts
        self.manager.save_artifact(self.product_name, "requirements", "Requirements content")
        self.manager.save_artifact(self.product_name, "PRD document", "PRD content")
        
        artifacts = self.manager.list_artifacts(self.product_name)
        
        self.assertEqual(len(artifacts), 2)
        self.assertTrue(any("business_requirements.md" in a for a in artifacts))
        self.assertTrue(any("prd_document.md" in a for a in artifacts))
    
    def test_read_artifact(self):
        """Test reading an artifact."""
        artifact_type = "requirements"
        content = "Test content for requirements"
        
        # Save an artifact
        self.manager.save_artifact(self.product_name, artifact_type, content)
        
        # Read it back
        read_content = self.manager.read_artifact(self.product_name, artifact_type)
        
        self.assertEqual(read_content, content)
    
    def test_read_artifact_not_found(self):
        """Test reading a non-existent artifact."""
        artifact_type = "nonexistent"
        
        read_content = self.manager.read_artifact(self.product_name, artifact_type)
        
        self.assertIsNone(read_content)
    
    def test_extract_product_name_from_heading(self):
        """Test extracting product name from markdown heading."""
        product_idea = "# Test Product Heading\nSome description"
        
        name = self.manager.extract_product_name(product_idea)
        
        self.assertEqual(name, "Test Product Heading")
    
    def test_extract_product_name_from_text(self):
        """Test extracting product name from plain text."""
        product_idea = "Test Product Name\nSome description"
        
        name = self.manager.extract_product_name(product_idea)
        
        self.assertEqual(name, "Test Product Name")
    
    def test_extract_product_name_empty(self):
        """Test extracting product name from empty text."""
        product_idea = ""
        
        with patch('src.artifacts.manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250414_051000"
            name = self.manager.extract_product_name(product_idea)
            
            self.assertEqual(name, "project_20250414_051000")

if __name__ == '__main__':
    unittest.main()
