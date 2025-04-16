"""
Integration tests for CLI interface with artifact management.

These tests verify that the CLI correctly interacts with the artifact
management components.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from unittest import TestCase, mock
import pytest
from typing import List, Dict, Any, Optional
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our CLI
import cli


class TestCLIIntegration(TestCase):
    """Integration tests for CLI interface with artifact management"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test product idea file
        self.idea_file = os.path.join(self.temp_dir, "test_idea.md")
        with open(self.idea_file, "w") as f:
            f.write("# Test Product Idea\n\nThis is a test product idea for unit testing.")
        
        # Save original state to restore in tearDown
        self.original_artifact_manager = cli.artifact_manager
        self.original_artifact_available = cli.ARTIFACTS_AVAILABLE
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original state
        cli.artifact_manager = self.original_artifact_manager
        cli.ARTIFACTS_AVAILABLE = self.original_artifact_available
        
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)
    
    def test_start_project_calls_main(self):
        """Test that start_project correctly calls the main function"""
        # Mock the main function
        with mock.patch('main.main') as mock_main:
            mock_main.return_value = "Test result"
            
            # Set up the CLI to use our test directory
            cli.ARTIFACTS_AVAILABLE = True
            mock_artifact_manager = mock.MagicMock()
            mock_artifact_manager.extract_product_name.return_value = "Test Project"
            mock_artifact_manager.sanitize_directory_name.return_value = "test_project"
            cli.artifact_manager = mock_artifact_manager
            
            # Call start_project
            with mock.patch("builtins.print"):
                args = argparse.Namespace(
                    idea_file=self.idea_file,
                    with_jira=False,
                    with_openrouter=False
                )
                cli.start_project(args)
            
            # Verify main was called with the right arguments
            mock_main.assert_called_once()
            args, kwargs = mock_main.call_args
            self.assertIn("product_idea", kwargs)
            self.assertIn("with_jira", kwargs)
            self.assertIn("use_openrouter", kwargs)
            self.assertFalse(kwargs["with_jira"])
            self.assertFalse(kwargs["use_openrouter"])
    
    def test_list_artifacts_with_no_projects(self):
        """Test listing artifacts when no projects exist"""
        # Set up the CLI to use our test directory
        cli.ARTIFACTS_AVAILABLE = True
        mock_artifact_manager = mock.MagicMock()
        mock_artifact_manager.base_dir = self.temp_dir
        cli.artifact_manager = mock_artifact_manager
        
        # Call list_artifacts
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace()
            cli.list_artifacts(args)
            
            # Verify output message about no projects
            mock_print.assert_any_call("\nNo project artifacts found.")
    
    def test_list_artifacts_with_projects(self):
        """Test listing artifacts when projects exist"""
        # Create a test project directory
        project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(project_dir)
        
        # Create test artifact files
        with open(os.path.join(project_dir, "requirements.md"), "w") as f:
            f.write("Test requirements")
        
        # Set up the CLI to use our test directory
        cli.ARTIFACTS_AVAILABLE = True
        mock_artifact_manager = mock.MagicMock()
        mock_artifact_manager.base_dir = self.temp_dir
        cli.artifact_manager = mock_artifact_manager
        
        # Call list_artifacts
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace()
            cli.list_artifacts(args)
            
            # Verify output contains project information
            mock_print.assert_any_call("\nAvailable Projects:")
            
            # Verify project info was printed
            prints = [call[0][0] for call in mock_print.call_args_list if isinstance(call[0][0], str)]
            self.assertTrue(any("Test Project" in p for p in prints))
            self.assertTrue(any("Artifacts: 1" in p for p in prints))
    
    def test_view_artifact(self):
        """Test viewing an artifact"""
        # Create a test project directory
        project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(project_dir)
        
        # Create test artifact file
        artifact_content = "# Test Requirements\n\nThis is a test artifact."
        with open(os.path.join(project_dir, "requirements.md"), "w") as f:
            f.write(artifact_content)
        
        # Set up the CLI to use our test directory
        cli.ARTIFACTS_AVAILABLE = True
        mock_artifact_manager = mock.MagicMock()
        mock_artifact_manager.base_dir = self.temp_dir
        cli.artifact_manager = mock_artifact_manager
        
        # Call view_artifact
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace(
                project_name="test_project",
                artifact_name="requirements.md"
            )
            cli.view_artifact(args)
            
            # Verify artifact content was printed
            prints = [call[0][0] for call in mock_print.call_args_list if isinstance(call[0][0], str)]
            
            # Check that the content is in the output
            content_printed = False
            for p in prints:
                if artifact_content in p:
                    content_printed = True
                    break
            
            self.assertTrue(content_printed)
    
    def test_export_artifacts(self):
        """Test exporting artifacts"""
        # Create a test project directory
        project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(project_dir)
        
        # Create test artifact files
        with open(os.path.join(project_dir, "requirements.md"), "w") as f:
            f.write("Test requirements")
        
        with open(os.path.join(project_dir, "architecture.md"), "w") as f:
            f.write("Test architecture")
        
        # Create export directory
        export_dir = os.path.join(self.temp_dir, "export")
        os.makedirs(export_dir)
        
        # Set up the CLI to use our test directory
        cli.ARTIFACTS_AVAILABLE = True
        mock_artifact_manager = mock.MagicMock()
        mock_artifact_manager.base_dir = self.temp_dir
        cli.artifact_manager = mock_artifact_manager
        
        # Call export_artifacts
        with mock.patch("builtins.print") as mock_print:
            args = argparse.Namespace(
                project_name="test_project",
                export_dir=export_dir
            )
            cli.export_artifacts(args)
            
            # Verify files were exported
            export_files = os.listdir(export_dir)
            self.assertIn("requirements.md", export_files)
            self.assertIn("architecture.md", export_files)
            
            # Verify success message was printed
            success_message_printed = False
            for call in mock_print.call_args_list:
                if len(call[0]) > 0 and isinstance(call[0][0], str) and "Successfully exported" in call[0][0]:
                    success_message_printed = True
                    break
            
            self.assertTrue(success_message_printed)