"""
LLM activities for research planning, analysis, and decision-making.
Uses OpenAI for intelligent research orchestration.
"""

import json
import os
from typing import Any, Dict, List

from temporalio import activity


def _get_openai_client():
    """Lazy initialization of OpenAI client to avoid sandbox restrictions."""
    import openai
    return openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@activity.defn
async def llm_plan_research(research_query: str) -> Dict[str, Any]:
    """
    Plan research strategy using LLM based on user query.
    
    Args:
        research_query: User's research question or topic
        
    Returns:
        Research plan with strategy and initial steps
    """
    
    activity.logger.info(f"Planning research for: {research_query}")
    
    system_prompt = """You are a research planning assistant. Given a research query, create a comprehensive research plan.

Your plan should include:
1. Key concepts to explore
2. Potential search terms for academic papers
3. Expected types of papers to find (theoretical, empirical, review, etc.)
4. Citation analysis strategy
5. Validation approach for ideas

Respond with a JSON object containing the research plan."""

    user_prompt = f"""Research Query: {research_query}

Create a detailed research plan for this query. Focus on academic paper discovery and analysis."""

    try:
        openai_client = _get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        plan = json.loads(response.choices[0].message.content)
        
        activity.logger.info("Research plan generated successfully")
        return {
            "success": True,
            "plan": plan,
            "query": research_query
        }
        
    except Exception as e:
        activity.logger.error(f"Failed to generate research plan: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "fallback_plan": {
                "key_concepts": [research_query],
                "search_terms": [research_query],
                "strategy": "basic_search"
            }
        }


@activity.defn
async def llm_analyze(
    research_context: Dict[str, Any], 
    available_tools: List[str], 
    analysis_type: str = "next_action"
) -> Dict[str, Any]:
    """
    Analyze research context and decide next action or generate summary.
    
    Args:
        research_context: Current research state and findings
        available_tools: List of available research tools
        analysis_type: Type of analysis ("next_action" or "summarize")
        
    Returns:
        Analysis results with recommended actions or summary
    """
    
    activity.logger.info(f"Performing {analysis_type} analysis")
    
    if analysis_type == "summarize":
        return await _generate_research_summary(research_context)
    
    system_prompt = f"""You are a research agent analyzer. Based on the current research context and available tools, decide the next best action.

Available tools: {', '.join(available_tools)}

Your response must be a JSON object with either:
1. {{"action": "complete", "reason": "why research is complete"}}
2. {{"action": "use_tool", "tool_name": "tool_name", "tool_args": {{"arg": "value"}}, "reason": "why this tool"}}

IMPORTANT - Tool Usage Guidelines:
- For arxiv_search_papers: Always provide "query" parameter
- For extract_sections: Always provide "paper_text" parameter. "sections" is optional
- For extract_citations: Provide either "paper_text" OR "paper_url"
- For process_pdf: Always provide "pdf_url" parameter. "sections" is optional
- For citation analysis: Always provide "paper_ids" parameter
- For similarity tools: Always provide required text parameters

Consider:
- What information is missing
- Which tools would provide the most value
- Whether enough research has been conducted
- Quality and relevance of current findings
- Ensure you provide all required arguments for chosen tools"""

    user_prompt = f"""Current Research Context:
{json.dumps(research_context, indent=2, default=str)}

Based on this context, what should be the next action? 

If recommending a tool, provide specific tool arguments. Use the ACTUAL research query from the context above in your search terms.

For the current research query "{research_context.get('query', '')}", appropriate tool examples would be:
- arxiv_search_papers: {{"query": "{research_context.get('query', '')}", "max_results": 10}}
- extract_sections: {{"paper_text": "full paper content here"}}
- extract_citations: {{"paper_text": "paper content with citations"}}
- process_pdf: {{"pdf_url": "https://arxiv.org/pdf/1234.5678.pdf"}}

IMPORTANT: Always use the actual research query terms, not generic examples. Ensure all required arguments are provided for your chosen tool."""

    try:
        openai_client = _get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        activity.logger.info(f"Analysis completed: {analysis.get('action', 'unknown')}")
        return analysis
        
    except Exception as e:
        activity.logger.error(f"Analysis failed: {str(e)}")
        return {
            "action": "complete",
            "reason": f"Analysis failed: {str(e)}",
            "error": True
        }


async def _generate_research_summary(research_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive research summary."""
    
    system_prompt = """You are a research summarizer. Create a comprehensive summary of the research conducted.

Your summary should include:
1. Research question and approach
2. Key papers discovered and their relevance
3. Important findings and insights
4. Citation networks and relationships
5. Gaps or limitations in current research
6. Recommendations for further investigation

Provide a well-structured, academic-style summary."""

    user_prompt = f"""Research Context:
{json.dumps(research_context, indent=2, default=str)}

Generate a comprehensive research summary based on all the work conducted."""

    try:
        openai_client = _get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        summary = response.choices[0].message.content
        
        return {
            "success": True,
            "summary": summary,
            "research_stats": {
                "papers_analyzed": len(research_context.get("tool_results", [])),
                "iterations_completed": research_context.get("iteration", 0),
                "tools_used": len(set(
                    result.get("tool", "") 
                    for result in research_context.get("tool_results", [])
                ))
            }
        }
        
    except Exception as e:
        activity.logger.error(f"Summary generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "fallback_summary": "Research summary could not be generated due to technical issues."
        }