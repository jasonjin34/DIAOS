#!/usr/bin/env python3
"""
Verification script to ensure the temporal-worker setup is correct.
Run with: uv run verify_setup.py
"""

import asyncio
import sys
from pathlib import Path

async def main():
    print("🚀 Verifying temporal-worker setup...")
    print("=" * 50)
    
    # Test 1: Basic imports
    try:
        from src.tools.arxiv_client_mcp import (
            ArxivMCPServerClient, 
            ensure_mcp_server_available,
            arxiv_search_papers,
            arxiv_download_paper,
            arxiv_deep_analysis
        )
        print("✅ All MCP client imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Tool registry
    try:
        from src.tools.registry import get_available_tools, TOOL_REGISTRY
        tools = await get_available_tools()
        expected_tools = [
            "arxiv_search_papers", "arxiv_download_paper", 
            "arxiv_list_papers", "arxiv_read_paper", 
            "arxiv_get_metadata", "arxiv_deep_analysis"
        ]
        
        for tool in expected_tools:
            if tool not in tools:
                print(f"❌ Missing tool: {tool}")
                return False
        
        print(f"✅ Tool registry working ({len(tools)} tools available)")
        print(f"   Including: {', '.join(expected_tools)}")
    except Exception as e:
        print(f"❌ Tool registry failed: {e}")
        return False
    
    # Test 3: MCP server availability
    try:
        result = await ensure_mcp_server_available()
        print("✅ arxiv-mcp-server is available")
    except Exception as e:
        print(f"❌ MCP server check failed: {e}")
        print("   Make sure you ran: uv tool install arxiv-mcp-server")
        return False
    
    # Test 4: Activity imports
    try:
        from src.activities.dynamic_tool_activity import dynamic_tool_activity
        from src.activities.tool_registry_activities import get_tool_descriptions
        print("✅ Activity imports successful")
    except Exception as e:
        print(f"❌ Activity import failed: {e}")
        return False
    
    # Test 5: Configuration
    try:
        from src.config.arxiv_config import ArxivConfig
        print("✅ Configuration imports successful")
    except Exception as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    
    print("\n🎉 All verification checks passed!")
    print("\n📋 Setup Summary:")
    print("   • Python version: 3.11+")
    print("   • Dependencies: Installed via uv")
    print("   • arxiv-mcp-server: Available as tool")
    print("   • MCP client: Consolidated and working")
    print("   • Tool registry: All arXiv tools available")
    print("   • Deep analysis: Available via MCP server")
    
    print("\n🚦 Ready to run:")
    print("   • uv run pytest  # Run tests")
    print("   • uv run python src/worker.py  # Start worker")
    print("   • uv tool run arxiv-mcp-server  # Test MCP server directly")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)