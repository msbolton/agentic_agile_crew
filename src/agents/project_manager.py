"""
Project Manager Agent for the Agentic Agile Crew
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL, LLM_TEMPERATURE, AGENT_MEMORY, AGENT_ALLOW_DELEGATION

def create_project_manager(tools=None):
    """
    Creates a Project Manager agent that specializes in creating
    detailed Product Requirement Documents (PRDs) and asking clarifying questions.
    
    Args:
        tools (list, optional): List of tools for the agent to use. Defaults to None.
        
    Returns:
        Agent: A CrewAI Project Manager agent
    """
    # Define the LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )
    
    # Create the Project Manager agent
    return Agent(
        role="Project Manager",
        goal="Create comprehensive PRDs based on business requirements and ask clarifying questions",
        backstory="""
        You are an experienced Project Manager with a proven track record of delivering 
        complex software projects on time and within budget. You excel at creating 
        detailed Product Requirement Documents (PRDs) that serve as the foundation for 
        successful product development.
        
        You are known for your ability to identify gaps in requirements and ask incisive
        clarifying questions. You never assume and always seek to understand the complete 
        picture before finalizing a PRD. Your documents are comprehensive, clear, and leave 
        no room for ambiguity.
        
        You have a deep understanding of software development processes and can anticipate 
        challenges before they arise. Your PRDs always include detailed user flows, edge cases, 
        and non-functional requirements that others might miss.
        """,
        verbose=True,
        allow_delegation=AGENT_ALLOW_DELEGATION,
        memory=AGENT_MEMORY,
        llm=llm,
        tools=tools or [],
    )
