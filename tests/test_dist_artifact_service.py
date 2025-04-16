"""
Test the DistArtifactService for saving artifacts to the dist/ directory.
"""

import os
import shutil
import tempfile
import unittest
from src.artifacts.dist_artifact_service import DistArtifactService


class TestDistArtifactService(unittest.TestCase):
    """Test the DistArtifactService"""

    def setUp(self):
        # Create a temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.service = DistArtifactService(base_dir=self.test_dir)
        
    def tearDown(self):
        # Clean up the test directory
        shutil.rmtree(self.test_dir)
        
    def test_set_product_name(self):
        """Test setting the product name"""
        self.service.set_product_name("Test Product")
        self.assertEqual(self.service.product_name, "Test Product")
        
        # Verify the directory was created
        product_dir = os.path.join(self.test_dir, "test_product")
        self.assertTrue(os.path.exists(product_dir), f"Directory {product_dir} should exist")
        
    def test_save_artifact(self):
        """Test saving an artifact"""
        self.service.set_product_name("Test Product")
        
        # Save a test artifact
        content = "Test artifact content"
        artifact_type = "test_artifact"
        
        filepath = self.service.save_artifact(artifact_type, content)
        self.assertIsNotNone(filepath)
        
        # Verify the file was created with the correct content
        self.assertTrue(os.path.exists(filepath), f"File {filepath} should exist")
        
        with open(filepath, 'r') as f:
            saved_content = f.read()
            
        self.assertEqual(saved_content, content, "Saved content should match the original")
        
    def test_save_known_artifact_type(self):
        """Test saving a known artifact type with predefined filename"""
        self.service.set_product_name("Test Product")
        
        # Save a known artifact type
        content = "# Business Requirements\n- Requirement 1\n- Requirement 2"
        artifact_type = "requirements"
        
        filepath = self.service.save_artifact(artifact_type, content)
        self.assertIsNotNone(filepath)
        
        # Check if the expected filename was used
        expected_filename = os.path.join(self.test_dir, "test_product", "business_requirements.md")
        self.assertEqual(filepath, expected_filename)
        
        # Verify the file was created with the correct content
        with open(filepath, 'r') as f:
            saved_content = f.read()
            
        self.assertEqual(saved_content, content)
        
    def test_save_implementation_code(self):
        """Test saving implementation code artifact"""
        self.service.set_product_name("Test Product")
        
        # Save implementation code
        content = "# Implementation Code\n```python\ndef hello():\n    print('Hello')\n```"
        artifact_type = "implementation code"
        
        filepath = self.service.save_artifact(artifact_type, content)
        self.assertIsNotNone(filepath)
        
        # Check that the implementation code directory was created
        code_dir = os.path.join(self.test_dir, "test_product", "implementation_code")
        self.assertTrue(os.path.exists(code_dir), f"Directory {code_dir} should exist")
        
        # Verify the file was created with the correct content
        with open(filepath, 'r') as f:
            saved_content = f.read()
            
        self.assertEqual(saved_content, content)
        
    def test_ensure_string_conversion(self):
        """Test string conversion of different inputs"""
        self.service.set_product_name("Test Product")
        
        # Test with various input types
        class TestObject:
            def __str__(self):
                return "TestObject string representation"
        
        test_inputs = [
            # Regular string
            ("Simple string", "Simple string"),
            # None
            (None, "None"),
            # Object with string representation
            (TestObject(), "TestObject string representation"),
            # Object with raw_output
            (type("TestRawOutput", (), {"raw_output": "Raw output content"})(), "Raw output content"),
            # Object with output
            (type("TestOutput", (), {"output": "Output content"})(), "Output content"),
            # Object with result
            (type("TestResult", (), {"result": "Result content"})(), "Result content"),
            # Object with response
            (type("TestResponse", (), {"response": "Response content"})(), "Response content"),
            # Object with content
            (type("TestContent", (), {"content": "Content content"})(), "Content content"),
        ]
        
        # Test each input type
        for input_val, expected_output in test_inputs:
            content = self.service._ensure_string(input_val)
            self.assertEqual(content, expected_output)


if __name__ == "__main__":
    unittest.main()