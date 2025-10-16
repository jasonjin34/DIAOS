"""
Tests for tool registry functionality.
Tests tool registration, validation, and discovery mechanisms.
"""

import pytest
from src.tools.registry import (
    get_available_tools,
    get_tool_descriptions,
    validate_tool_usage,
    get_tool_handler,
    register_tool,
    unregister_tool,
    TOOL_REGISTRY,
    TOOL_DESCRIPTIONS
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_available_tools():
    """Test getting list of available tools."""
    tools = await get_available_tools()
    
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # Should include all main research tools
    expected_tools = [
        # Enhanced arXiv tools
        "arxiv_search_papers",
        "arxiv_download_paper",
        "arxiv_list_papers", 
        "arxiv_read_paper",
        "arxiv_get_metadata",
        # Other research tools
        "extract_citations",
        "analyze_citation_network",
        "process_pdf",
        "extract_sections",
        "find_similar_papers",
        "calculate_similarity"
    ]
    
    for tool in expected_tools:
        assert tool in tools


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_tool_descriptions():
    """Test getting tool descriptions."""
    descriptions = await get_tool_descriptions()
    
    assert isinstance(descriptions, dict)
    assert len(descriptions) > 0
    
    # Check structure of tool descriptions
    for tool_name, description in descriptions.items():
        assert "description" in description
        assert "args" in description
        assert "returns" in description
        
        # Check that description has meaningful content
        assert isinstance(description["description"], str)
        assert len(description["description"]) > 10
        
        # Check args structure
        assert isinstance(description["args"], dict)
        
        # Check returns description
        assert isinstance(description["returns"], str)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_usage_valid_arxiv_search():
    """Test validation of valid arXiv search tool usage."""
    args = {
        "query": "machine learning",
        "max_results": 10,
        "category": "cs.AI"
    }
    
    result = await validate_tool_usage("arxiv_search_papers", args)
    
    assert result["valid"] is True
    assert result["tool_name"] == "arxiv_search_papers"
    assert result["validated_args"] == args


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_usage_valid_paper_details():
    """Test validation of valid paper details tool usage."""
    args = {
        "paper_id": "1706.03762"
    }
    
    result = await validate_tool_usage("arxiv_get_metadata", args)
    
    assert result["valid"] is True
    assert result["tool_name"] == "arxiv_get_metadata"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_usage_missing_required_args():
    """Test validation with missing required arguments."""
    # arxiv_get_metadata requires paper_id
    args = {}  # Missing paper_id
    
    result = await validate_tool_usage("arxiv_get_metadata", args)
    
    assert result["valid"] is False
    assert "requires 'paper_id' parameter" in result["reason"]
    assert "required_args" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_usage_unknown_tool():
    """Test validation with unknown tool name."""
    result = await validate_tool_usage("unknown_tool", {"arg": "value"})
    
    assert result["valid"] is False
    assert "Tool 'unknown_tool' not found in registry" in result["reason"]
    assert "available_tools" in result
    assert isinstance(result["available_tools"], list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_usage_extract_citations_special_case():
    """Test validation for extract_citations which has special requirements."""
    # Should require either paper_text or paper_url
    args_with_text = {"paper_text": "Some paper content"}
    result_text = await validate_tool_usage("extract_citations", args_with_text)
    assert result_text["valid"] is True
    
    args_with_url = {"paper_url": "https://example.com/paper.pdf"}
    result_url = await validate_tool_usage("extract_citations", args_with_url)
    assert result_url["valid"] is True
    
    # Should fail if neither is provided
    args_empty = {}
    result_empty = await validate_tool_usage("extract_citations", args_empty)
    assert result_empty["valid"] is False
    assert "requires either 'paper_text' or 'paper_url'" in result_empty["reason"]


@pytest.mark.unit
def test_get_tool_handler_existing_tool():
    """Test getting handler for existing tool."""
    handler = get_tool_handler("arxiv_search_papers")
    
    assert handler is not None
    assert callable(handler)


@pytest.mark.unit
def test_get_tool_handler_nonexistent_tool():
    """Test getting handler for non-existent tool."""
    handler = get_tool_handler("nonexistent_tool")
    
    assert handler is None


@pytest.mark.unit
def test_register_new_tool():
    """Test registering a new tool."""
    def dummy_tool(args):
        return {"result": "dummy"}
    
    tool_description = {
        "description": "A dummy tool for testing",
        "args": {"test_arg": "Test argument"},
        "returns": "Dummy result"
    }
    
    # Register tool
    register_tool("dummy_tool", dummy_tool, tool_description)
    
    # Verify it was registered
    assert "dummy_tool" in TOOL_REGISTRY
    assert "dummy_tool" in TOOL_DESCRIPTIONS
    assert TOOL_REGISTRY["dummy_tool"] == dummy_tool
    assert TOOL_DESCRIPTIONS["dummy_tool"] == tool_description
    
    # Clean up
    unregister_tool("dummy_tool")


@pytest.mark.unit
def test_unregister_existing_tool():
    """Test unregistering an existing tool."""
    # First register a tool
    def temp_tool(args):
        return {}
    
    register_tool("temp_tool", temp_tool, {"description": "temp", "args": {}, "returns": "temp"})
    assert "temp_tool" in TOOL_REGISTRY
    
    # Now unregister it
    result = unregister_tool("temp_tool")
    
    assert result is True
    assert "temp_tool" not in TOOL_REGISTRY
    assert "temp_tool" not in TOOL_DESCRIPTIONS


@pytest.mark.unit
def test_unregister_nonexistent_tool():
    """Test unregistering a non-existent tool."""
    result = unregister_tool("nonexistent_tool")
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tool_descriptions_completeness():
    """Test that all registered tools have complete descriptions."""
    tools = await get_available_tools()
    descriptions = await get_tool_descriptions()
    
    # Every tool should have a description
    for tool in tools:
        assert tool in descriptions
        
        desc = descriptions[tool]
        # Check required fields
        assert "description" in desc
        assert "args" in desc
        assert "returns" in desc
        
        # Description should be meaningful
        assert len(desc["description"]) > 20
        assert "returns" in desc and len(desc["returns"]) > 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_usage_optional_args():
    """Test validation with optional arguments."""
    # arxiv_search_papers has optional arguments
    args_minimal = {"query": "test"}  # Only required arg
    result_minimal = await validate_tool_usage("arxiv_search_papers", args_minimal)
    assert result_minimal["valid"] is True
    
    args_with_optional = {
        "query": "test",
        "max_results": 5,
        "category": "cs.AI"
    }
    result_optional = await validate_tool_usage("arxiv_search_papers", args_with_optional)
    assert result_optional["valid"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_multiple_tools():
    """Test validation for multiple different tools."""
    test_cases = [
        # Enhanced arXiv tools
        ("arxiv_search_papers", {"query": "test"}, True),
        ("arxiv_download_paper", {"paper_id": "1234.5678"}, True),
        ("arxiv_list_papers", {}, True),  # No required args
        ("arxiv_read_paper", {"paper_id": "1234.5678"}, True),
        ("arxiv_get_metadata", {"paper_id": "1234.5678"}, True),
        # Other tools
        ("extract_citations", {"paper_text": "sample text"}, True),
        ("process_pdf", {"pdf_url": "https://example.com/paper.pdf"}, True),
        ("find_similar_papers", {"reference_paper": "sample text"}, True),
        ("calculate_similarity", {"paper1_text": "text1", "paper2_text": "text2"}, True),
        ("analyze_citation_network", {"paper_ids": ["paper1", "paper2"]}, True),
        ("extract_sections", {"paper_text": "text", "sections": ["abstract"]}, True)
    ]
    
    for tool_name, args, expected_valid in test_cases:
        result = await validate_tool_usage(tool_name, args)
        assert result["valid"] == expected_valid, f"Tool {tool_name} validation failed"


@pytest.mark.unit
def test_tool_registry_consistency():
    """Test that tool registry and descriptions are consistent."""
    # Every tool in registry should have a description
    for tool_name in TOOL_REGISTRY:
        assert tool_name in TOOL_DESCRIPTIONS, f"Tool {tool_name} missing description"
    
    # Every description should have a corresponding tool
    for tool_name in TOOL_DESCRIPTIONS:
        assert tool_name in TOOL_REGISTRY, f"Description for {tool_name} without tool"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_tool_with_complex_args():
    """Test validation with complex argument structures."""
    # Test analyze_citation_network which expects a list
    args = {
        "paper_ids": ["paper1", "paper2", "paper3"],
        "depth": 2,
        "include_co_citations": True
    }
    
    result = await validate_tool_usage("analyze_citation_network", args)
    assert result["valid"] is True
    
    # Test extract_sections which expects a list of sections
    args_sections = {
        "paper_text": "sample text",
        "sections": ["abstract", "introduction", "conclusion"]
    }
    
    result_sections = await validate_tool_usage("extract_sections", args_sections)
    assert result_sections["valid"] is True


@pytest.mark.unit
def test_registry_immutability_during_validation():
    """Test that validation doesn't modify the registry."""
    original_registry = dict(TOOL_REGISTRY)
    original_descriptions = dict(TOOL_DESCRIPTIONS)
    
    # Perform various validations
    import asyncio
    
    async def run_validations():
        await validate_tool_usage("arxiv_search", {"query": "test"})
        await validate_tool_usage("unknown_tool", {})
        await validate_tool_usage("extract_citations", {})
    
    asyncio.run(run_validations())
    
    # Registry should remain unchanged
    assert TOOL_REGISTRY == original_registry
    assert TOOL_DESCRIPTIONS == original_descriptions


@pytest.mark.unit
@pytest.mark.asyncio
async def test_edge_case_validations():
    """Test edge cases in tool validation."""
    # Empty string arguments
    result_empty_query = await validate_tool_usage("arxiv_search_papers", {"query": ""})
    # Should be invalid since empty string doesn't pass our validation
    assert result_empty_query["valid"] is False
    
    # None values
    result_none = await validate_tool_usage("arxiv_search_papers", {"query": None})
    # Should be invalid since None doesn't pass our validation
    assert result_none["valid"] is False
    
    # Extra arguments (should be allowed)
    result_extra = await validate_tool_usage("arxiv_search_papers", {
        "query": "test",
        "extra_arg": "should_be_ignored"
    })
    assert result_extra["valid"] is True


@pytest.mark.unit
def test_tool_handler_retrieval_consistency():
    """Test that tool handlers can be consistently retrieved."""
    tools = list(TOOL_REGISTRY.keys())
    
    for tool_name in tools:
        handler = get_tool_handler(tool_name)
        assert handler is not None
        assert callable(handler)
        assert handler == TOOL_REGISTRY[tool_name]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_description_format_consistency():
    """Test that all tool descriptions follow consistent format."""
    descriptions = await get_tool_descriptions()
    
    for tool_name, desc in descriptions.items():
        # All should have the same top-level keys
        assert set(desc.keys()) == {"description", "args", "returns"}
        
        # Description should be a meaningful string
        assert isinstance(desc["description"], str)
        assert len(desc["description"]) > 10
        
        # Args should be a dictionary with string keys
        assert isinstance(desc["args"], dict)
        for arg_name, arg_desc in desc["args"].items():
            assert isinstance(arg_name, str)
            assert isinstance(arg_desc, str)
        
        # Returns should be a descriptive string
        assert isinstance(desc["returns"], str)
        assert len(desc["returns"]) > 5