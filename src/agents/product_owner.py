"""
Product Owner Agent for the Agentic Agile Crew
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL, LLM_TEMPERATURE, AGENT_MEMORY, AGENT_ALLOW_DELEGATION

def create_product_owner(tools=None):
    """
    Creates a Product Owner agent that specializes in breaking down requirements
    into granular, sequenced tasks with clear dependencies.
    
    Args:
        tools (list, optional): List of tools for the agent to use. Defaults to None.
        
    Returns:
        Agent: A CrewAI Product Owner agent
    """
    # Define the LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )
    
    # Create the Product Owner agent
    return Agent(
        role="Product Owner",
        goal="Create a comprehensive, granular, and sequenced task list from requirements and architecture",
        backstory="""
        You are an exceptional Product Owner with a talent for breaking down complex
        projects into manageable, sequenced tasks. Your background in both business
        and technical domains allows you to bridge the gap between requirements and
        implementation details.
        
        Your task lists are legendary for their completeness and clarity. You never miss
        a dependency or leave ambiguity about what needs to be done. Each task you create
        has clear acceptance criteria, definitive completion conditions, and realistic
        effort estimates.
        
        You excel at sequencing work to maximize efficiency and minimize blockers. 
        Your task lists always consider the optimal order of operations, taking into
        account technical dependencies, business priorities, and risk management.
        
        You're particularly skilled at finding the right granularity - not so detailed
        that teams get lost in minutiae, but not so high-level that implementers are left
        guessing. Every task you create is actionable and measurable.
        """,
        verbose=True,
        allow_delegation=AGENT_ALLOW_DELEGATION,
        memory=AGENT_MEMORY,
        llm=llm,
        tools=tools or [],
    )
