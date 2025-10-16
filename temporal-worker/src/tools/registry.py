"""
Tool registry for dynamic research tool management.
Provides discovery, validation, and execution of research tools.

Enhanced with MCP-based arXiv tools for improved performance and local storage.
"""

from typing import Any, Callable, Dict, List, Optional

from temporalio import activity

# Enhanced arXiv tools with MCP server
from .arxiv_client_mcp import (
    arxiv_search_papers, arxiv_download_paper, arxiv_list_papers, 
    arxiv_read_paper, arxiv_get_paper_metadata, arxiv_deep_analysis
)

# Other research tools
from .citation_analyzer import extract_citations, analyze_citation_network
from .pdf_processor import process_pdf_content, extract_paper_sections
from .semantic_search import find_similar_papers, calculate_paper_similarity


# Tool registry mapping
TOOL_REGISTRY: Dict[str, Callable] = {
    # Enhanced arXiv tools with MCP server
    "arxiv_search_papers": arxiv_search_papers,
    "arxiv_download_paper": arxiv_download_paper,
    "arxiv_list_papers": arxiv_list_papers,
    "arxiv_read_paper": arxiv_read_paper,
    "arxiv_get_metadata": arxiv_get_paper_metadata,
    "arxiv_deep_analysis": arxiv_deep_analysis,
    
    # Other research tools
    "extract_citations": extract_citations,
    "analyze_citation_network": analyze_citation_network,
    "process_pdf": process_pdf_content,
    "extract_sections": extract_paper_sections,
    "find_similar_papers": find_similar_papers,
    "calculate_similarity": calculate_paper_similarity,
}

# Tool descriptions for LLM understanding
TOOL_DESCRIPTIONS = {
    # Enhanced arXiv tools with MCP server
    "arxiv_search_papers": {
        "description": "Enhanced arXiv paper search with local caching and advanced filtering",
        "args": {
            "query": "Search query string",
            "max_results": "Optional: Maximum papers to return (default: 10)",
            "category": "Optional: arXiv category filter (e.g., 'cs.AI', 'cs.LG')",
            "date_from": "Optional: Start date filter (YYYY-MM-DD)",
            "date_to": "Optional: End date filter (YYYY-MM-DD)",
            "sort_by": "Optional: Sort criteria ('relevance', 'submitted', 'updated')"
        },
        "returns": "List of papers with metadata and local storage status"
    },
    "arxiv_download_paper": {
        "description": "Download and locally store an arXiv paper with metadata",
        "args": {
            "paper_id": "arXiv paper ID (e.g., '1706.03762')",
            "force_download": "Optional: Force re-download if already exists (default: false)"
        },
        "returns": "Download status and local file information"
    },
    "arxiv_list_papers": {
        "description": "List all locally downloaded papers with filtering options",
        "args": {
            "category_filter": "Optional: Category to filter by",
            "date_from": "Optional: Start date filter for download date",
            "limit": "Optional: Maximum papers to return (default: 100)"
        },
        "returns": "List of downloaded papers with metadata and local paths"
    },
    "arxiv_read_paper": {
        "description": "Read content of a locally downloaded paper",
        "args": {
            "paper_id": "arXiv paper ID",
            "include_metadata": "Optional: Include full metadata (default: true)",
            "extract_sections": "Optional: Extract paper sections (default: false)"
        },
        "returns": "Paper content, metadata, and extracted sections if requested"
    },
    "arxiv_get_metadata": {
        "description": "Get enhanced metadata for a paper (local or remote)",
        "args": {
            "paper_id": "arXiv paper ID",
            "include_citations": "Optional: Include citation analysis (default: false)",
            "force_refresh": "Optional: Force refresh from arXiv API (default: false)"
        },
        "returns": "Enhanced paper metadata with local storage information"
    },
    "arxiv_deep_analysis": {
        "description": "Get comprehensive deep analysis of a paper using MCP server",
        "args": {
            "paper_id": "arXiv paper ID"
        },
        "returns": "Comprehensive analysis including executive summary, methodology, results, and implications"
    },
    "extract_citations": {
        "description": "Extract citations from paper text or PDF",
        "args": {
            "paper_text": "Full text of the paper",
            "paper_url": "Alternative: URL to paper PDF"
        },
        "returns": "List of extracted citations with parsed metadata"
    },
    "analyze_citation_network": {
        "description": "Analyze citation relationships between papers",
        "args": {
            "paper_ids": "List of paper IDs to analyze",
            "depth": "Citation depth to explore (default: 2)"
        },
        "returns": "Citation network graph with relationships and metrics"
    },
    "process_pdf": {
        "description": "Extract and process text content from PDF",
        "args": {
            "pdf_url": "URL to PDF file",
            "sections": "Optional list of sections to extract"
        },
        "returns": "Processed text content with section breakdown"
    },
    "extract_sections": {
        "description": "Extract specific sections from academic paper",
        "args": {
            "paper_text": "Full paper text",
            "sections": "List of section names (e.g., ['abstract', 'introduction', 'conclusion'])"
        },
        "returns": "Dictionary mapping section names to content"
    },
    "find_similar_papers": {
        "description": "Find papers similar to given paper using semantic search",
        "args": {
            "reference_paper": "Paper text or abstract for similarity comparison",
            "search_corpus": "Optional: specific corpus to search in"
        },
        "returns": "List of similar papers with similarity scores"
    },
    "calculate_similarity": {
        "description": "Calculate semantic similarity between two papers",
        "args": {
            "paper1_text": "Text content of first paper",
            "paper2_text": "Text content of second paper"
        },
        "returns": "Similarity score and detailed comparison metrics"
    }
}


@activity.defn
async def get_available_tools() -> List[str]:
    """Get list of available research tools."""
    return list(TOOL_REGISTRY.keys())


@activity.defn
async def get_tool_descriptions() -> Dict[str, Any]:
    """Get detailed descriptions of all available tools."""
    return TOOL_DESCRIPTIONS


@activity.defn
async def validate_tool_usage(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate tool usage before execution.
    
    Args:
        tool_name: Name of tool to validate
        tool_args: Arguments to validate
        
    Returns:
        Validation result with success status and any issues
    """
    
    if tool_name not in TOOL_REGISTRY:
        return {
            "valid": False,
            "reason": f"Tool '{tool_name}' not found in registry",
            "available_tools": list(TOOL_REGISTRY.keys())
        }
    
    if tool_name not in TOOL_DESCRIPTIONS:
        return {
            "valid": False,
            "reason": f"Tool '{tool_name}' missing description metadata"
        }
    
    # Basic argument validation
    tool_desc = TOOL_DESCRIPTIONS[tool_name]
    required_args = tool_desc.get("args", {})
    
    missing_args = []
    for arg_name, arg_desc in required_args.items():
        if "Optional:" not in arg_desc and arg_name not in tool_args:
            missing_args.append(arg_name)
    
    if missing_args:
        return {
            "valid": False,
            "reason": f"Missing required arguments: {missing_args}",
            "required_args": required_args
        }
    
    return {
        "valid": True,
        "tool_name": tool_name,
        "validated_args": tool_args
    }


def get_tool_handler(tool_name: str) -> Optional[Callable]:
    """
    Get tool handler function by name.
    
    Args:
        tool_name: Name of tool to retrieve
        
    Returns:
        Tool handler function or None if not found
    """
    
    return TOOL_REGISTRY.get(tool_name)


def register_tool(name: str, handler: Callable, description: Dict[str, Any]) -> None:
    """
    Register a new research tool.
    
    Args:
        name: Tool name identifier
        handler: Function to handle tool execution
        description: Tool description metadata
    """
    
    TOOL_REGISTRY[name] = handler
    TOOL_DESCRIPTIONS[name] = description


def unregister_tool(name: str) -> bool:
    """
    Unregister a research tool.
    
    Args:
        name: Tool name to remove
        
    Returns:
        True if tool was removed, False if not found
    """
    
    if name in TOOL_REGISTRY:
        del TOOL_REGISTRY[name]
        if name in TOOL_DESCRIPTIONS:
            del TOOL_DESCRIPTIONS[name]
        return True
    
    return False