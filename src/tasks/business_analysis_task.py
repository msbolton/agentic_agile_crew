"""
Business Analysis Task for the Agentic Agile Crew
"""

from crewai import Task

def create_business_analysis_task(agent, product_idea):
    """
    Creates a task for the Business Analyst to refine a product idea
    into comprehensive business requirements.
    
    Args:
        agent (Agent): The Business Analyst agent.
        product_idea (str): The initial product idea text.
        
    Returns:
        Task: A CrewAI Task for business analysis.
    """
    return Task(
        description=f"""
        Analyze the following product idea and create comprehensive business requirements:
        
        {product_idea}
        
        Your task is to refine this product idea into detailed business requirements. 
        Please include the following:
        
        1. Target Audience Analysis:
           - Identify primary and secondary user personas
           - Describe their needs, pain points, and goals
           - Explain how the product addresses these needs
        
        2. Market Analysis:
           - Identify market opportunities
           - Analyze competitors and differentiators
           - Assess potential challenges and risks
        
        3. Core Features:
           - List and describe all essential features
           - Prioritize features based on business value
           - Explain the rationale behind each feature
        
        4. Success Metrics:
           - Define key business success metrics
           - Outline how to measure user satisfaction
           - Suggest specific KPIs to track
        
        5. Constraints and Assumptions:
           - Document any business constraints
           - List key assumptions made during the analysis
           - Identify dependencies that could impact the project
        
        Present your analysis in a well-structured document that clearly communicates the 
        business requirements for this product.
        """,
        expected_output="A comprehensive business requirements document including target audience, market analysis, core features, success metrics, and constraints.",
        agent=agent
    )
