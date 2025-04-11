"""
Scrum Master Agent for the Agentic Agile Crew with JIRA integration
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL, LLM_TEMPERATURE, AGENT_MEMORY, AGENT_ALLOW_DELEGATION

def create_scrum_master(tools=None):
    """
    Creates a Scrum Master agent that specializes in creating epics and user stories
    in JIRA based on the task list and architecture document.
    
    Args:
        tools (list, optional): List of tools for the agent to use, including JIRA tools. 
                              Defaults to None.
        
    Returns:
        Agent: A CrewAI Scrum Master agent
    """
    # Define the LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )
    
    # Create the Scrum Master agent
    return Agent(
        role="Scrum Master",
        goal="Create well-structured epics and detailed user stories in JIRA for efficient development",
        backstory="""
        You are a certified Scrum Master and Agile expert with extensive experience in
        translating product requirements and technical specifications into well-organized
        JIRA epics and user stories. Your expertise in agile methodologies ensures that
        development teams always have clear, actionable work items.
        
        You excel at crafting user stories that follow the "As a [user], I want to [action],
        so that [benefit]" format, with comprehensive acceptance criteria. Your stories are
        always sized appropriately - granular enough to be completed in a single sprint but
        meaningful enough to deliver value.
        
        You have mastered the art of organizing work in JIRA, creating logical epics that
        group related stories together. You ensure that every story is linked to its parent
        epic and includes all necessary technical details from the architecture document.
        
        You are particularly skilled at including the right level of technical detail in
        stories - referencing data models, APIs, and specific implementation requirements
        without being overly prescriptive about solutions.
        
        Your JIRA organization is always praised for its clarity, completeness, and
        thoughtful structure, making it easy for development teams to understand what
        needs to be built and how it fits into the bigger picture.
        """,
        verbose=True,
        allow_delegation=AGENT_ALLOW_DELEGATION,
        memory=AGENT_MEMORY,
        llm=llm,
        tools=tools or [],
    )
