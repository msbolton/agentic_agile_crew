"""
Integration tests for the main application.

These tests verify that the main application correctly handles
different components of the system.
"""

import os
import sys
import tempfile
import shutil
from unittest import TestCase, mock
import pytest
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Use mocks to work around module imports
sys.modules['src.tasks.business_analysis_task'] = mock.MagicMock()
sys.modules['src.tasks.prd_creation_task'] = mock.MagicMock()
sys.modules['src.tasks.architecture_design_task'] = mock.MagicMock()
sys.modules['src.tasks.task_list_creation_task'] = mock.MagicMock()
sys.modules['src.tasks.jira_creation_task'] = mock.MagicMock()
sys.modules['src.tasks.development_task'] = mock.MagicMock()
sys.modules['config.settings'] = mock.MagicMock()

# Mock task classes for testing
class MockTask:
    """Mock task for testing"""
    def __init__(self, description, agent):
        self.description = description
        self.agent = agent
        self.output = None
    
    def execute(self):
        """Execute the task"""
        self.output = f"Output from {self.description}"
        return self.output

class MockCrew:
    """Mock crew for testing"""
    def __init__(self, agents, tasks):
        self.agents = agents
        self.tasks = tasks
        self.tasks_output = []
    
    def kickoff(self):
        """Kickoff the crew"""
        for task in self.tasks:
            output = task.execute()
            self.tasks_output.append(MockTaskOutput(task, output))
        return self

class MockTaskOutput:
    """Mock task output for testing"""
    def __init__(self, task, raw_output):
        self.task = task
        self.raw_output = raw_output

class TestMainIntegrationBase(TestCase):
    """Base class for main application integration tests"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test product idea
        self.product_idea = """# Test Product
        
        Create a simple note-taking application with the following features:
        - User authentication
        - Create, edit, and delete notes
        - Share notes with other users
        - Search functionality
        """
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir)

class TestMainIntegration(TestMainIntegrationBase):
    """Integration tests for main application"""
    
    @mock.patch('src.agents.business_analyst.create_business_analyst')
    @mock.patch('src.agents.project_manager.create_project_manager')
    @mock.patch('src.agents.architect.create_architect')
    @mock.patch('src.agents.product_owner.create_product_owner')
    @mock.patch('src.agents.scrum_master.create_scrum_master')
    @mock.patch('src.agents.developer.create_developer')
    @mock.patch('crewai.Crew')
    @mock.patch('src.tasks.create_business_analysis_task')
    @mock.patch('src.tasks.create_prd_creation_task')
    @mock.patch('src.tasks.create_architecture_design_task')
    @mock.patch('src.tasks.create_task_list_creation_task')
    @mock.patch('src.tasks.create_jira_creation_task')
    @mock.patch('src.tasks.create_development_task')
    def test_basic_workflow(
        self,
        mock_create_dev_task, mock_create_jira_task, mock_create_task_list_task,
        mock_create_arch_task, mock_create_prd_task, mock_create_ba_task,
        mock_crew_class, mock_dev, mock_sm, mock_po, mock_arch, mock_pm, mock_ba
    ):
        """Test the basic workflow execution"""
        # Set up mocks for agents
        mock_ba.return_value = mock.MagicMock(name="BusinessAnalyst")
        mock_pm.return_value = mock.MagicMock(name="ProjectManager")
        mock_arch.return_value = mock.MagicMock(name="Architect")
        mock_po.return_value = mock.MagicMock(name="ProductOwner")
        mock_sm.return_value = mock.MagicMock(name="ScrumMaster")
        mock_dev.return_value = mock.MagicMock(name="Developer")
        
        # Set up mocks for tasks
        ba_task = MockTask("Analyze the product idea", mock_ba.return_value)
        prd_task = MockTask("Create a PRD document", mock_pm.return_value)
        arch_task = MockTask("Design the system architecture", mock_arch.return_value)
        task_list_task = MockTask("Create a task list", mock_po.return_value)
        jira_task = MockTask("Create JIRA stories", mock_sm.return_value)
        dev_task = MockTask("Implement the code", mock_dev.return_value)
        
        mock_create_ba_task.return_value = ba_task
        mock_create_prd_task.return_value = prd_task
        mock_create_arch_task.return_value = arch_task
        mock_create_task_list_task.return_value = task_list_task
        mock_create_jira_task.return_value = jira_task
        mock_create_dev_task.return_value = dev_task
        
        # Set up mock for Crew
        mock_crew = MockCrew(
            agents=[
                mock_ba.return_value,
                mock_pm.return_value,
                mock_arch.return_value,
                mock_po.return_value,
                mock_sm.return_value,
                mock_dev.return_value
            ],
            tasks=[ba_task, prd_task, arch_task, task_list_task, jira_task, dev_task]
        )
        mock_crew_class.return_value = mock_crew
        
        # Import main after mocks are set up
        from main import main
        
        # Run the main function with test data
        result = main(product_idea=self.product_idea)
        
        # Verify the workflow executed correctly
        self.assertEqual(len(result.tasks_output), 6)
        
        # Verify task outputs contain expected content
        self.assertEqual(result.tasks_output[0].raw_output, "Output from Analyze the product idea")
        self.assertEqual(result.tasks_output[1].raw_output, "Output from Create a PRD document")
        self.assertEqual(result.tasks_output[2].raw_output, "Output from Design the system architecture")
        self.assertEqual(result.tasks_output[3].raw_output, "Output from Create a task list")
        self.assertEqual(result.tasks_output[4].raw_output, "Output from Create JIRA stories")
        self.assertEqual(result.tasks_output[5].raw_output, "Output from Implement the code")
    
    @mock.patch('src.agents.business_analyst.create_business_analyst')
    @mock.patch('src.agents.project_manager.create_project_manager')
    @mock.patch('main.ArtifactManager')
    @mock.patch('main.ArtifactService')
    @mock.patch('main.TaskOutputSaver')
    def test_artifact_saving(
        self, mock_saver_class, mock_service_class, mock_manager_class,
        mock_pm, mock_ba
    ):
        """Test that artifacts are correctly saved"""
        # Set up mocks
        mock_ba.return_value = mock.MagicMock(name="BusinessAnalyst")
        mock_pm.return_value = mock.MagicMock(name="ProjectManager")
        
        mock_manager = mock.MagicMock()
        mock_manager.extract_product_name.return_value = "Test Product"
        mock_manager_class.return_value = mock_manager
        
        mock_service = mock.MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_saver = mock.MagicMock()
        mock_saver_class.return_value = mock_saver
        
        # Import main after mocks are set up
        with mock.patch('main.Crew') as mock_crew_class:
            mock_crew = mock.MagicMock()
            mock_crew.kickoff.return_value = mock_crew
            mock_crew.tasks_output = [MockTaskOutput(mock.MagicMock(), "Task output")]
            mock_crew_class.return_value = mock_crew
            
            from main import main
            
            # Run the main function with test data
            result = main(product_idea=self.product_idea)
            
            # Verify artifact manager was used
            mock_manager.extract_product_name.assert_called_with(mock.ANY)
            
            # Verify task output saver was used
            mock_saver.register_tasks.assert_called_once()
            self.assertGreaterEqual(mock_saver.save_output.call_count, 1)