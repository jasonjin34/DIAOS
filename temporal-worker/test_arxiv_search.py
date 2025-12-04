#!/usr/bin/env python3
"""
Test script for arxiv MCP paper search functionality.
Run with: uv run python test_arxiv_search.py
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.arxiv_client_mcp import (
    arxiv_search_papers,
    ensure_mcp_server_available,
    get_mcp_client,
    cleanup_mcp_client
)


async def test_mcp_server_availability():
    """Test if MCP server can be started."""
    print("\n" + "="*60)
    print("TEST 1: MCP Server Availability")
    print("="*60)

    try:
        available = await ensure_mcp_server_available()
        print(f"MCP Server Available: {available}")

        if available:
            client = await get_mcp_client()
            tools = await client.list_tools()
            print(f"Available tools: {tools}")
        return available
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_basic_search():
    """Test basic paper search."""
    print("\n" + "="*60)
    print("TEST 2: Basic Paper Search")
    print("="*60)

    result = await arxiv_search_papers({
        "query": "transformer attention mechanism",
        "max_results": 5
    })

    print(f"Success: {result.get('success')}")
    print(f"Source: {result.get('search_metadata', {}).get('source', 'unknown')}")
    print(f"Papers found: {result.get('count', 0)}")

    if result.get('papers'):
        print("\nPapers:")
        for i, paper in enumerate(result['papers'][:3], 1):
            print(f"  {i}. {paper.get('title', 'No title')[:60]}...")
            print(f"     ID: {paper.get('id')}")
            print(f"     Authors: {', '.join(paper.get('authors', [])[:2])}...")

    return result.get('success', False)


async def test_category_filter():
    """Test search with category filter."""
    print("\n" + "="*60)
    print("TEST 3: Category Filtered Search (cs.AI)")
    print("="*60)

    result = await arxiv_search_papers({
        "query": "large language models",
        "max_results": 3,
        "categories": ["cs.AI"]
    })

    print(f"Success: {result.get('success')}")
    print(f"Source: {result.get('search_metadata', {}).get('source', 'unknown')}")
    print(f"Papers found: {result.get('count', 0)}")

    if result.get('papers'):
        for paper in result['papers']:
            print(f"  - {paper.get('title', '')[:50]}...")
            print(f"    Categories: {paper.get('categories', [])}")

    return result.get('success', False)


async def test_date_range():
    """Test search with date range."""
    print("\n" + "="*60)
    print("TEST 4: Date Range Search (2024)")
    print("="*60)

    result = await arxiv_search_papers({
        "query": "neural network",
        "max_results": 3,
        "date_from": "2024-01-01",
        "date_to": "2024-12-31"
    })

    print(f"Success: {result.get('success')}")
    print(f"Source: {result.get('search_metadata', {}).get('source', 'unknown')}")
    print(f"Papers found: {result.get('count', 0)}")

    if result.get('papers'):
        for paper in result['papers']:
            print(f"  - {paper.get('title', '')[:50]}...")
            print(f"    Published: {paper.get('published')}")

    return result.get('success', False)


async def test_empty_query():
    """Test handling of empty query."""
    print("\n" + "="*60)
    print("TEST 5: Empty Query Handling")
    print("="*60)

    result = await arxiv_search_papers({
        "query": "",
        "max_results": 5
    })

    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error', 'None')}")

    # Should fail gracefully
    return result.get('success') == False


async def main():
    """Run all tests."""
    print("="*60)
    print("ArXiv MCP Search Test Suite")
    print("="*60)

    results = {}

    try:
        # Test 1: MCP availability
        results['mcp_available'] = await test_mcp_server_availability()

        # Test 2: Basic search
        results['basic_search'] = await test_basic_search()

        # Test 3: Category filter
        results['category_filter'] = await test_category_filter()

        # Test 4: Date range
        results['date_range'] = await test_date_range()

        # Test 5: Empty query
        results['empty_query'] = await test_empty_query()

    finally:
        # Cleanup
        print("\n" + "="*60)
        print("Cleaning up MCP client...")
        await cleanup_mcp_client()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("="*60))
    print(f"Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
