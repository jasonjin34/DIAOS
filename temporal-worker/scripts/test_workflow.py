#!/usr/bin/env python3
"""
Test script to trigger a research workflow locally.
"""

import asyncio
from temporalio.client import Client
from src.workflows.research_workflow import ResearchWorkflow

async def main():
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Start workflow
    print("Starting research workflow...")
    handle = await client.start_workflow(
        ResearchWorkflow.run,
        args=["vision transformer", "test-user"],  # research_query, user_id
        id="test-research-workflow",
        task_queue="research-agent-queue"
    )
    
    print(f"Workflow started with ID: {handle.id}")
    
    # Wait for result
    print("Waiting for workflow to complete...")
    result = await handle.result()
    
    print(f"Workflow completed!")
    print(f"Success: {result.get('success', False)}")
    print(f"Papers discovered: {result.get('papers_discovered', 0)}")
    
    if result.get('success'):
        print("✅ Workflow completed successfully!")
    else:
        print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())