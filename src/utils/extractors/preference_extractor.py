"""
Preference Extractor for Agentic Agile Crew

This module extracts specific preferences and details from product ideas
to be provided to specific agents in the workflow.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("preference_extractor")

def extract_business_requirements(product_idea: str) -> Dict[str, Any]:
    """
    Extract business-related requirements from a product idea.
    
    Args:
        product_idea: The product idea text
        
    Returns:
        Dictionary with business requirements information
    """
    # For now, a simple implementation that extracts common business requirement patterns
    business_info = {
        "target_audience": [],
        "business_goals": [],
        "market_considerations": [],
        "success_metrics": [],
        "constraints": []
    }
    
    # Extract target audience information
    audience_patterns = [
        r"(?i)target\s+(?:audience|users?|customers?)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:audience|users?|customers?)\s+(?:are|include|is)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in audience_patterns:
        matches = re.findall(pattern, product_idea)
        business_info["target_audience"].extend(matches)
    
    # Extract business goals
    goal_patterns = [
        r"(?i)(?:business|primary|main)\s+goals?[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)goals?(?:\s+of\s+the\s+(?:product|project|system))?[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in goal_patterns:
        matches = re.findall(pattern, product_idea)
        business_info["business_goals"].extend(matches)
    
    # Extract market considerations
    market_patterns = [
        r"(?i)market\s+(?:considerations?|needs?|requirements?)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:competitors?|competition)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in market_patterns:
        matches = re.findall(pattern, product_idea)
        business_info["market_considerations"].extend(matches)
    
    # Extract success metrics
    metric_patterns = [
        r"(?i)(?:success|key)\s+metrics?[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:measure|measuring)\s+success[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in metric_patterns:
        matches = re.findall(pattern, product_idea)
        business_info["success_metrics"].extend(matches)
    
    # Extract constraints
    constraint_patterns = [
        r"(?i)constraints?[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)limitations?[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in constraint_patterns:
        matches = re.findall(pattern, product_idea)
        business_info["constraints"].extend(matches)
    
    return business_info

def extract_technical_preferences(product_idea: str) -> Dict[str, Any]:
    """
    Extract technical preferences from a product idea.
    
    Args:
        product_idea: The product idea text
        
    Returns:
        Dictionary with technical preferences information
    """
    tech_preferences = {
        "frontend": [],
        "backend": [],
        "database": [],
        "infrastructure": [],
        "languages": [],
        "frameworks": [],
        "apis": [],
        "security": [],
        "other": []
    }
    
    # Extract frontend preferences
    frontend_patterns = [
        r"(?i)(?:frontend|front[\s-]end|ui|user\s+interface)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:use|using|prefer)\s+(?:react|angular|vue|svelte)[^\.]*",
    ]
    
    for pattern in frontend_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["frontend"].extend(matches)
    
    # Extract backend preferences
    backend_patterns = [
        r"(?i)(?:backend|back[\s-]end|server)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:use|using|prefer)\s+(?:node|django|flask|express|spring|rails)[^\.]*",
    ]
    
    for pattern in backend_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["backend"].extend(matches)
    
    # Extract database preferences
    database_patterns = [
        r"(?i)(?:database|data\s+storage|db)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:use|using|prefer)\s+(?:sql|mysql|postgresql|mongo|dynamodb|firebase)[^\.]*",
    ]
    
    for pattern in database_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["database"].extend(matches)
    
    # Extract infrastructure preferences
    infra_patterns = [
        r"(?i)(?:infrastructure|hosting|deployment|cloud)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:use|using|prefer)\s+(?:aws|azure|gcp|kubernetes|docker)[^\.]*",
    ]
    
    for pattern in infra_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["infrastructure"].extend(matches)
    
    # Extract programming language preferences
    language_patterns = [
        r"(?i)(?:language|programming\s+language)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:use|using|prefer)\s+(?:python|javascript|typescript|java|c\#|ruby|go)[^\.]*",
    ]
    
    for pattern in language_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["languages"].extend(matches)
    
    # Extract framework preferences 
    framework_patterns = [
        r"(?i)(?:framework|library)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:use|using|prefer)\s+(?:react|angular|vue|django|flask|spring|rails)[^\.]*",
    ]
    
    for pattern in framework_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["frameworks"].extend(matches)
    
    # Extract API preferences
    api_patterns = [
        r"(?i)(?:api|integrations?|external\s+services?)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["apis"].extend(matches)
    
    # Extract security preferences
    security_patterns = [
        r"(?i)(?:security|authentication|authorization)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in security_patterns:
        matches = re.findall(pattern, product_idea)
        tech_preferences["security"].extend(matches)
    
    # Look for any "tech stack" sections
    tech_stack_pattern = r"(?i)(?:tech(?:nical)?\s+stack|technologies?)[:\s]+(.*?)(?:\n\n|\n\d|\Z)"
    tech_stack_matches = re.findall(tech_stack_pattern, product_idea)
    
    for match in tech_stack_matches:
        tech_preferences["other"].append(match)
    
    return tech_preferences

def extract_project_management_preferences(product_idea: str) -> Dict[str, Any]:
    """
    Extract project management preferences from a product idea.
    
    Args:
        product_idea: The product idea text
        
    Returns:
        Dictionary with project management preferences information
    """
    pm_preferences = {
        "timeline": [],
        "milestones": [],
        "priority_features": [],
        "scope": [],
        "requirements": []
    }
    
    # Extract timeline information
    timeline_patterns = [
        r"(?i)(?:timeline|schedule|deadline)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:complete|finish|deliver)(?:\s+by|\s+in|\s+within)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in timeline_patterns:
        matches = re.findall(pattern, product_idea)
        pm_preferences["timeline"].extend(matches)
    
    # Extract milestone information
    milestone_patterns = [
        r"(?i)(?:milestone|phase)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in milestone_patterns:
        matches = re.findall(pattern, product_idea)
        pm_preferences["milestones"].extend(matches)
    
    # Extract priority feature information
    priority_patterns = [
        r"(?i)(?:priority|important|critical|key)\s+(?:feature|functionality)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:must\s+have|should\s+have)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in priority_patterns:
        matches = re.findall(pattern, product_idea)
        pm_preferences["priority_features"].extend(matches)
    
    # Extract scope information
    scope_patterns = [
        r"(?i)(?:scope|extent|boundary)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in scope_patterns:
        matches = re.findall(pattern, product_idea)
        pm_preferences["scope"].extend(matches)
    
    # Extract requirements
    requirement_patterns = [
        r"(?i)(?:requirements?|specifications?)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in requirement_patterns:
        matches = re.findall(pattern, product_idea)
        pm_preferences["requirements"].extend(matches)
    
    return pm_preferences

def extract_scrum_preferences(product_idea: str) -> Dict[str, Any]:
    """
    Extract Scrum and user story preferences from a product idea.
    
    Args:
        product_idea: The product idea text
        
    Returns:
        Dictionary with Scrum preferences information
    """
    scrum_preferences = {
        "user_stories": [],
        "epics": [],
        "acceptance_criteria": [],
        "sprint_details": [],
        "agile_specifics": []
    }
    
    # Extract user story information
    story_patterns = [
        r"(?i)(?:user\s+stor(?:y|ies))[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
        r"(?i)(?:as\s+a[n]?\s+.*?I\s+want\s+to[^\.]*)",
    ]
    
    for pattern in story_patterns:
        matches = re.findall(pattern, product_idea)
        scrum_preferences["user_stories"].extend(matches)
    
    # Extract epic information
    epic_patterns = [
        r"(?i)(?:epic)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in epic_patterns:
        matches = re.findall(pattern, product_idea)
        scrum_preferences["epics"].extend(matches)
    
    # Extract acceptance criteria
    criteria_patterns = [
        r"(?i)(?:acceptance\s+criteria|definition\s+of\s+done)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in criteria_patterns:
        matches = re.findall(pattern, product_idea)
        scrum_preferences["acceptance_criteria"].extend(matches)
    
    # Extract sprint details
    sprint_patterns = [
        r"(?i)(?:sprint)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in sprint_patterns:
        matches = re.findall(pattern, product_idea)
        scrum_preferences["sprint_details"].extend(matches)
    
    # Extract general agile specifics
    agile_patterns = [
        r"(?i)(?:agile|scrum|kanban)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in agile_patterns:
        matches = re.findall(pattern, product_idea)
        scrum_preferences["agile_specifics"].extend(matches)
    
    return scrum_preferences

def extract_development_preferences(product_idea: str) -> Dict[str, Any]:
    """
    Extract development-specific preferences from a product idea.
    
    Args:
        product_idea: The product idea text
        
    Returns:
        Dictionary with development preferences information
    """
    dev_preferences = {
        "coding_standards": [],
        "testing_requirements": [],
        "implementation_details": [],
        "performance_requirements": [],
        "accessibility_requirements": []
    }
    
    # Extract coding standards 
    code_patterns = [
        r"(?i)(?:coding\s+standards?|code\s+style)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in code_patterns:
        matches = re.findall(pattern, product_idea)
        dev_preferences["coding_standards"].extend(matches)
    
    # Extract testing requirements
    test_patterns = [
        r"(?i)(?:testing|tests?|quality\s+assurance)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in test_patterns:
        matches = re.findall(pattern, product_idea)
        dev_preferences["testing_requirements"].extend(matches)
    
    # Extract implementation details
    impl_patterns = [
        r"(?i)(?:implementation|development\s+details?)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in impl_patterns:
        matches = re.findall(pattern, product_idea)
        dev_preferences["implementation_details"].extend(matches)
    
    # Extract performance requirements
    perf_patterns = [
        r"(?i)(?:performance|speed|efficiency)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in perf_patterns:
        matches = re.findall(pattern, product_idea)
        dev_preferences["performance_requirements"].extend(matches)
    
    # Extract accessibility requirements
    access_patterns = [
        r"(?i)(?:accessibility|a11y)[:\s]+(.*?)(?:\n\n|\n\d|\Z)",
    ]
    
    for pattern in access_patterns:
        matches = re.findall(pattern, product_idea)
        dev_preferences["accessibility_requirements"].extend(matches)
    
    return dev_preferences

def extract_all_preferences(product_idea: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract all types of preferences from a product idea.
    
    Args:
        product_idea: The product idea text
        
    Returns:
        Dictionary with all preference categories
    """
    return {
        "business": extract_business_requirements(product_idea),
        "technical": extract_technical_preferences(product_idea),
        "project_management": extract_project_management_preferences(product_idea),
        "scrum": extract_scrum_preferences(product_idea),
        "development": extract_development_preferences(product_idea)
    }

def format_preferences_for_agent(preferences: Dict[str, Any], agent_type: str) -> str:
    """
    Format preferences in a way suitable for inclusion in task descriptions.
    
    Args:
        preferences: Dictionary of preferences
        agent_type: Type of agent (business_analyst, architect, etc.)
        
    Returns:
        Formatted string of preferences
    """
    formatted_text = ""
    
    if agent_type == "business_analyst":
        relevant_prefs = preferences.get("business", {})
        formatted_text += "Extracted Business Requirements:\n\n"
        
        for category, items in relevant_prefs.items():
            if items:
                formatted_text += f"- {category.replace('_', ' ').title()}:\n"
                for item in items:
                    formatted_text += f"  - {item.strip()}\n"
                formatted_text += "\n"
    
    elif agent_type == "architect":
        relevant_prefs = preferences.get("technical", {})
        formatted_text += "Technical Preferences:\n\n"
        
        for category, items in relevant_prefs.items():
            if items:
                formatted_text += f"- {category.replace('_', ' ').title()}:\n"
                for item in items:
                    formatted_text += f"  - {item.strip()}\n"
                formatted_text += "\n"
    
    elif agent_type == "project_manager":
        relevant_prefs = preferences.get("project_management", {})
        formatted_text += "Project Management Considerations:\n\n"
        
        for category, items in relevant_prefs.items():
            if items:
                formatted_text += f"- {category.replace('_', ' ').title()}:\n"
                for item in items:
                    formatted_text += f"  - {item.strip()}\n"
                formatted_text += "\n"
    
    elif agent_type == "scrum_master":
        relevant_prefs = preferences.get("scrum", {})
        formatted_text += "Scrum and User Story Preferences:\n\n"
        
        for category, items in relevant_prefs.items():
            if items:
                formatted_text += f"- {category.replace('_', ' ').title()}:\n"
                for item in items:
                    formatted_text += f"  - {item.strip()}\n"
                formatted_text += "\n"
    
    elif agent_type == "developer":
        relevant_prefs = preferences.get("development", {})
        formatted_text += "Development Preferences:\n\n"
        
        for category, items in relevant_prefs.items():
            if items:
                formatted_text += f"- {category.replace('_', ' ').title()}:\n"
                for item in items:
                    formatted_text += f"  - {item.strip()}\n"
                formatted_text += "\n"
    
    return formatted_text if formatted_text else "No specific preferences found."
