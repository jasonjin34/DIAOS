"""
Temporal worker for the research agent.
Starts worker to execute workflows and activities.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import workflows
from src.workflows.research_workflow import ResearchWorkflow

# Import activities
from src.activities.dynamic_tool_activity import dynamic_tool_activity
from src.activities.llm_activities import llm_analyze, llm_plan_research
from src.activities.tool_registry_activities import get_available_tools, get_tool_descriptions, validate_tool_usage


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the Temporal worker."""
    
    # Get configuration from environment
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "research-agent-queue")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    logger.info(f"Starting worker for task queue: {task_queue}")
    logger.info(f"Connecting to Temporal at: {temporal_host}")
    
    try:
        # Create Temporal client
        client = await Client.connect(
            target_host=temporal_host,
            namespace=namespace
        )
        
        # Create worker
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[ResearchWorkflow],
            activities=[
                dynamic_tool_activity,
                llm_analyze,
                llm_plan_research,
                get_available_tools,
                get_tool_descriptions,
                validate_tool_usage,
            ],
        )
        
        logger.info("Worker started successfully")
        logger.info("Available workflows: ResearchWorkflow")
        logger.info("Available activities: dynamic_tool_activity, llm_analyze, llm_plan_research, registry activities")
        
        # Run worker
        await worker.run()
        
    except Exception as e:
        logger.error(f"Worker failed to start: {str(e)}")
        raise


def cli_main():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()