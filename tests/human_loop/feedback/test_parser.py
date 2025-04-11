"""
Unit tests for the FeedbackParser module
"""

import pytest
from src.human_loop.feedback.parser import FeedbackParser, FeedbackItem

class TestFeedbackParser:
    """
    Test cases for the FeedbackParser class
    """
    
    def test_parse_empty_feedback(self):
        """Test parsing empty feedback returns empty list"""
        result = FeedbackParser.parse("")
        assert isinstance(result, list)
        assert len(result) == 0
        
        result = FeedbackParser.parse(None)
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_parse_simple_feedback(self):
        """Test parsing simple feedback text"""
        feedback = "Please add a section on security considerations."
        result = FeedbackParser.parse(feedback)
        
        assert len(result) == 1
        assert result[0].type == "add"
        assert "security considerations" in result[0].description
    
    def test_parse_multiline_feedback(self):
        """Test parsing multiline feedback text"""
        feedback = """
        Please add a section on security considerations.
        The architecture section needs to be improved with database schema details.
        Remove the duplicate information in the introduction.
        """
        result = FeedbackParser.parse(feedback)
        
        assert len(result) == 3
        
        # Check types are correctly identified
        types = [item.type for item in result]
        assert "add" in types
        assert "change" in types  # "needs to be improved" should trigger "change" type
        assert "remove" in types
    
    def test_determine_type(self):
        """Test type determination from text"""
        add_text = "Add more details about API authorization"
        change_text = "The security section should be improved with more details"
        remove_text = "Remove the redundant explanation in section 3"
        clarify_text = "Please clarify how the authentication works"
        
        assert FeedbackParser._determine_type(add_text) == "add"
        assert FeedbackParser._determine_type(change_text) == "change"
        assert FeedbackParser._determine_type(remove_text) == "remove"
        assert FeedbackParser._determine_type(clarify_text) == "clarify"
        
        # Default case
        assert FeedbackParser._determine_type("This looks good overall") == "change"
    
    def test_extract_section(self):
        """Test section extraction from feedback text"""
        text1 = "In the Architecture section, add more details about caching"
        text2 = "Under Security Considerations, explain the authentication flow"
        text3 = "The section 'Database Schema' needs more details"
        text4 = "This heading needs to be more specific"  # No section name mentioned
        text5 = "The heading 'Introduction' is too long"
        
        assert FeedbackParser._extract_section(text1) == "Architecture"
        assert FeedbackParser._extract_section(text2) == "Security Considerations"
        assert FeedbackParser._extract_section(text3) == "Database Schema"
        assert FeedbackParser._extract_section(text4) is None
        assert FeedbackParser._extract_section(text5) == "Introduction"
    
    def test_format_for_agent(self):
        """Test formatting feedback items for agent consumption"""
        feedback_items = [
            FeedbackItem("add", "Add a section on security", "Architecture", 1),
            FeedbackItem("change", "Improve the database schema", "Database", 2),
            FeedbackItem("remove", "Remove the redundant information", None, 3)
        ]
        
        formatted = FeedbackParser.format_for_agent(feedback_items)
        
        # Check for sections and content
        assert "# Feedback for Revision" in formatted
        assert "## Section-Specific Feedback" in formatted
        assert "### Architecture" in formatted
        assert "### Database" in formatted
        assert "## General Feedback" in formatted
        
        # Check priority sorting (highest priority first)
        architecture_index = formatted.find("### Architecture")
        database_index = formatted.find("### Database")
        assert architecture_index < database_index
        
        # Check for feedback types in uppercase
        assert "ADD:" in formatted
        assert "CHANGE:" in formatted
        assert "REMOVE:" in formatted
    
    def test_format_for_agent_empty(self):
        """Test formatting with no feedback items"""
        formatted = FeedbackParser.format_for_agent([])
        assert "No specific feedback provided" in formatted

class TestFeedbackItem:
    """
    Test cases for the FeedbackItem class
    """
    
    def test_feedback_item_creation(self):
        """Test creating feedback items"""
        item = FeedbackItem("add", "Add security details", "Security", 1)
        
        assert item.type == "add"
        assert item.description == "Add security details"
        assert item.section == "Security"
        assert item.priority == 1
    
    def test_feedback_item_to_dict(self):
        """Test converting feedback item to dictionary"""
        item = FeedbackItem("change", "Improve the API docs", "API", 2)
        item_dict = item.to_dict()
        
        assert item_dict["type"] == "change"
        assert item_dict["description"] == "Improve the API docs"
        assert item_dict["section"] == "API"
        assert item_dict["priority"] == 2
    
    def test_feedback_item_string(self):
        """Test string representation of feedback item"""
        item1 = FeedbackItem("add", "Add security details", "Security", 1)
        item2 = FeedbackItem("change", "Improve clarity", None, 2)
        
        str1 = str(item1)
        str2 = str(item2)
        
        assert "ADD" in str1
        assert "in 'Security'" in str1
        assert "!" * item1.priority in str1
        
        assert "CHANGE" in str2
        assert "in " not in str2  # No section
        assert "!" * item2.priority in str2
