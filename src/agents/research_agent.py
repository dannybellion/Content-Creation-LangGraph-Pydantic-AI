from src.agents.base import BaseAgent
from src.models import ConsolidatedResearch, ContentPlan
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="researcher",
    output_type=ConsolidatedResearch,
    system_prompt=PromptManager.get_prompt("researcher"),
    model_name="gpt-4o",
    temperature=0.2,
    tools=[_search_web, _search_youtube, _analyze_authority],
)

async def conduct_research(content_plan: ContentPlan) -> ConsolidatedResearch:
    """Conduct comprehensive research using both web and YouTube sources."""
    research_prompt = f"""
    Conduct comprehensive research for this content plan using all available tools:

    CONTENT PLAN:
    Topic: {content_plan.title}
    Research Angles: {content_plan.research_angles}
    Target Keywords: {content_plan.target_keywords}
    Unique Value Proposition: {content_plan.unique_value_proposition}
    Key Messages: {content_plan.key_messages}

    RESEARCH INSTRUCTIONS:
    1. Use the web search tool to find authoritative articles, reports, and industry insights
    2. Use the YouTube search tool to find expert interviews, tutorials, and presentations
    3. Use the authority analysis tool to assess source credibility
    4. Synthesize findings from both sources into consolidated insights
    5. Identify unique angles and content gaps
    6. Extract quotable expert opinions and relevant statistics

    Focus on finding:
    - Latest trends and developments
    - Expert opinions and industry commentary
    - Statistical data and case studies
    - Practical implementation insights
    - Emerging challenges and solutions
    - Unique perspectives not widely covered

    Provide comprehensive research that combines the best of both web and video sources.
    """
    
    return await agent.run(research_prompt)