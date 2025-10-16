"""
Clean tool registry activities for Temporal workflows.
These activities don't import external tool libraries to avoid sandbox restrictions.
"""

from typing import Any, Dict, List
from temporalio import activity


# Tool descriptions for LLM understanding (no imports needed)
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
            "paper_text": "Optional: Full text of the paper (provide either this or paper_url)",
            "paper_url": "Optional: URL to paper PDF (provide either this or paper_text)",
            "format": "Optional: Citation format to expect (default: mixed)"
        },
        "returns": "List of extracted citations with parsed metadata"
    },
    "analyze_citation_network": {
        "description": "Analyze citation relationships between papers",
        "args": {
            "paper_ids": "List of paper IDs to analyze (required)",
            "depth": "Optional: Citation depth to explore (default: 2)"
        },
        "returns": "Citation network graph with relationships and metrics"
    },
    "process_pdf": {
        "description": "Extract and process text content from PDF",
        "args": {
            "pdf_url": "URL to PDF file (required)",
            "sections": "Optional: List of sections to extract. If not provided, extracts all content"
        },
        "returns": "Processed text content with section breakdown"
    },
    "extract_sections": {
        "description": "Extract specific sections from academic paper",
        "args": {
            "paper_text": "Full paper text (required)",
            "sections": "Optional: List of section names (e.g., ['abstract', 'introduction', 'conclusion']). If not provided, extracts all major sections"
        },
        "returns": "Dictionary mapping section names to content"
    },
    "find_similar_papers": {
        "description": "Find papers similar to given paper using semantic search",
        "args": {
            "reference_paper": "Paper text or abstract for similarity comparison (required)",
            "search_corpus": "Optional: Specific corpus to search in. If not provided, uses default academic corpus"
        },
        "returns": "List of similar papers with similarity scores"
    },
    "calculate_similarity": {
        "description": "Calculate semantic similarity between two papers",
        "args": {
            "paper1_text": "Text content of first paper (required)",
            "paper2_text": "Text content of second paper (required)"
        },
        "returns": "Similarity score and detailed comparison metrics"
    }
}


@activity.defn
async def get_available_tools() -> List[str]:
    """Get list of available research tools."""
    return list(TOOL_DESCRIPTIONS.keys())


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
    
    if tool_name not in TOOL_DESCRIPTIONS:
        return {
            "valid": False,
            "reason": f"Tool '{tool_name}' not found in registry",
            "available_tools": list(TOOL_DESCRIPTIONS.keys())
        }
    
    # Basic argument validation
    tool_desc = TOOL_DESCRIPTIONS[tool_name]
    required_args = tool_desc.get("args", {})
    
    missing_args = []
    for arg_name, arg_desc in required_args.items():
        # Check if argument is truly required (not marked as optional)
        is_optional = (
            "Optional:" in arg_desc or 
            "optional" in arg_desc.lower() or
            arg_desc.startswith("Optional")
        )
        if not is_optional and arg_name not in tool_args:
            missing_args.append(arg_name)
    
    # Special validation cases
    if tool_name == "extract_citations":
        # Requires at least one of paper_text or paper_url
        if not tool_args.get("paper_text") and not tool_args.get("paper_url"):
            return {
                "valid": False,
                "reason": "extract_citations requires either 'paper_text' or 'paper_url'",
                "required_args": required_args
            }
    elif tool_name == "arxiv_search_papers":
        # Query is required for search functions
        if not tool_args.get("query"):
            return {
                "valid": False,
                "reason": f"{tool_name} requires 'query' parameter",
                "required_args": required_args
            }
    elif tool_name in ["arxiv_download_paper", "arxiv_read_paper", "arxiv_get_metadata", "arxiv_deep_analysis"]:
        # Paper ID is required for these functions
        if not tool_args.get("paper_id"):
            return {
                "valid": False,
                "reason": f"{tool_name} requires 'paper_id' parameter",
                "required_args": required_args
            }
    elif missing_args:
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