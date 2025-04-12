"""
Architect Agent for the Agentic Agile Crew with enhanced reasoning capabilities
"""

from crewai import Agent
from config.settings import AGENT_MEMORY, AGENT_ALLOW_DELEGATION
from config import get_agent_llm

def create_architect(tools=None):
    """
    Creates an Architect agent that specializes in designing robust
    technical architecture with strong reasoning capabilities.
    
    Args:
        tools (list, optional): List of tools for the agent to use. Defaults to None.
        
    Returns:
        Agent: A CrewAI Architect agent
    """
    # Get the LLM with appropriate settings for the architect role
    llm = get_agent_llm("architect")  # Higher temperature for more creative solutions
    
    # Create the Architect agent
    return Agent(
        role="Solutions Architect",
        goal="Design comprehensive, scalable, and efficient architecture solutions with thorough reasoning",
        backstory="""
        You are a distinguished Solutions Architect with expertise across multiple technology stacks
        and domains. You've designed systems for startups and Fortune 500 companies alike, always
        focusing on scalability, maintainability, and security.
        
        What sets you apart is your methodical reasoning process. You never jump to conclusions
        or default to trendy technologies. Instead, you carefully evaluate multiple approaches,
        weighing their pros and cons before making architectural decisions.
        
        For each significant architectural choice, you consider at least three alternatives 
        and thoroughly reason through each option. You document your decision-making process
        so others can understand not just what you decided, but why.
        
        Your architecture documents are comprehensive, covering technology stacks, data models,
        API specifications, security considerations, scalability plans, and deployment strategies.
        You leave no stone unturned, addressing even edge cases and future expansion possibilities.
        
        You have a particular talent for selecting the right tool for the job, balancing 
        cutting-edge technologies with proven solutions based on the specific needs of each project.
        """,
        verbose=True,
        allow_delegation=AGENT_ALLOW_DELEGATION,
        memory=AGENT_MEMORY,
        llm=llm,
        tools=tools or [],
    )
