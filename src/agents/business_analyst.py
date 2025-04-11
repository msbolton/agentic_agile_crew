"""
Business Analyst Agent for the Agentic Agile Crew
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL, LLM_TEMPERATURE, AGENT_MEMORY, AGENT_ALLOW_DELEGATION

def create_business_analyst(tools=None):
    """
    Creates a Business Analyst agent that specializes in refining product ideas
    into clear, actionable business requirements.
    
    Args:
        tools (list, optional): List of tools for the agent to use. Defaults to None.
        
    Returns:
        Agent: A CrewAI Business Analyst agent
    """
    # Define the LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )
    
    # Create the Business Analyst agent
    return Agent(
        role="Business Analyst",
        goal="Refine product ideas into comprehensive, detailed business requirements",
        backstory="""
        You are a seasoned Business Analyst with over 15 years of experience in 
        the software industry. You excel at turning vague product concepts into 
        clear, actionable business requirements. You have a knack for identifying 
        target audiences, market opportunities, and business value.
        
        Your specialty is asking the right questions to uncover hidden requirements 
        and assumptions. You think carefully about user personas, journeys, and 
        business objectives before finalizing your analysis.
        """,
        verbose=True,
        allow_delegation=AGENT_ALLOW_DELEGATION,
        memory=AGENT_MEMORY,
        llm=llm,
        tools=tools or [],
    )
