"""
Dynamic tool activity for executing research tools at runtime.
Follows the Temporal tutorial pattern for flexible tool execution.
Uses lazy imports to avoid Temporal sandbox restrictions.
"""

import asyncio
import inspect
from typing import Any, Dict, Callable, Optional

from temporalio import activity


async def _get_tool_handler(tool_name: str) -> Optional[Callable]:
    """
    Lazy import tool handlers to avoid sandbox restrictions.
    Only imports when actually needed during activity execution.
    """
    
    # Enhanced arXiv tools with MCP server
    if tool_name == "arxiv_search_papers":
        from src.tools.arxiv_client_mcp import arxiv_search_papers
        return arxiv_search_papers
    
    elif tool_name == "arxiv_download_paper":
        from src.tools.arxiv_client_mcp import arxiv_download_paper
        return arxiv_download_paper
    
    elif tool_name == "arxiv_list_papers":
        from src.tools.arxiv_client_mcp import arxiv_list_papers
        return arxiv_list_papers
    
    elif tool_name == "arxiv_read_paper":
        from src.tools.arxiv_client_mcp import arxiv_read_paper
        return arxiv_read_paper
    
    elif tool_name == "arxiv_get_metadata":
        from src.tools.arxiv_client_mcp import arxiv_get_paper_metadata
        return arxiv_get_paper_metadata
    
    elif tool_name == "arxiv_deep_analysis":
        from src.tools.arxiv_client_mcp import arxiv_deep_analysis
        return arxiv_deep_analysis
    
    elif tool_name == "extract_citations":
        from src.tools.citation_analyzer import extract_citations
        return extract_citations
    
    elif tool_name == "analyze_citation_network":
        from src.tools.citation_analyzer import analyze_citation_network
        return analyze_citation_network
    
    elif tool_name == "process_pdf":
        from src.tools.pdf_processor import process_pdf_content
        return process_pdf_content
    
    elif tool_name == "extract_sections":
        from src.tools.pdf_processor import extract_paper_sections
        return extract_paper_sections
    
    elif tool_name == "find_similar_papers":
        from src.tools.semantic_search import find_similar_papers
        return find_similar_papers
    
    elif tool_name == "calculate_similarity":
        from src.tools.semantic_search import calculate_paper_similarity
        return calculate_paper_similarity
    
    else:
        return None


@activity.defn
async def dynamic_tool_activity(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a research tool dynamically based on runtime decisions.
    Uses lazy imports to avoid Temporal workflow sandbox restrictions.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments to pass to the tool
        
    Returns:
        Tool execution results
    """
    
    activity.logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
    
    try:
        # Get tool handler using lazy import
        handler = await _get_tool_handler(tool_name)
        
        if handler is None:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        
        # Execute tool based on whether it's async or sync
        if inspect.iscoroutinefunction(handler):
            result = await handler(tool_args)
        else:
            # Run sync function in executor to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None, handler, tool_args
            )
        
        activity.logger.info(f"Tool {tool_name} completed successfully")
        
        return {
            "success": True,
            "tool_name": tool_name,
            "result": result,
            "metadata": {
                "execution_time": activity.info().current_attempt_scheduled_time,
                "attempt": activity.info().attempt
            }
        }
        
    except Exception as e:
        activity.logger.error(f"Tool {tool_name} failed: {str(e)}")
        
        # Don't raise exception, return error result for workflow to handle
        return {
            "success": False,
            "tool_name": tool_name,
            "error": str(e),
            "error_type": type(e).__name__,
            "metadata": {
                "execution_time": activity.info().current_attempt_scheduled_time,
                "attempt": activity.info().attempt
            }
        }