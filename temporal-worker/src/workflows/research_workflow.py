"""
Research workflow for durable AI agent following Temporal patterns.
Orchestrates paper discovery, citation analysis, and idea validation.
"""

import asyncio
from datetime import timedelta
from typing import Any, Dict, List 

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import only activity functions, no tool modules
from src.activities.dynamic_tool_activity import dynamic_tool_activity
from src.activities.llm_activities import llm_analyze, llm_plan_research
from src.activities.tool_registry_activities import get_available_tools, validate_tool_usage


@workflow.defn
class ResearchWorkflow:
    """Main workflow for conducting durable research sessions."""

    def __init__(self) -> None:
        self.research_context: Dict[str, Any] = {}
        self.discovered_papers: List[Dict[str, Any]] = []
        self.analysis_results: List[Dict[str, Any]] = []
        self.max_iterations = 10

    @workflow.run
    async def run(self, research_query: str, user_id: str, document_id: str = None) -> Dict[str, Any]:
        """Execute a complete research workflow."""
        
        workflow.logger.info(f"Starting research for query: {research_query}")
        
        # Initialize research context
        self.research_context = {
            "query": research_query,
            "user_id": user_id,
            "document_id": document_id,
            "iteration": 0,
            "status": "initializing"
        }
        
        try:
            # Step 1: Plan research strategy using LLM
            research_plan = await workflow.execute_activity(
                llm_plan_research,
                args=[research_query],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            self.research_context["plan"] = research_plan
            self.research_context["status"] = "planning_complete"
            
            # Step 2: Execute research plan iteratively
            for iteration in range(self.max_iterations):
                self.research_context["iteration"] = iteration
                self.research_context["status"] = f"iteration_{iteration}"
                
                # Get available tools
                available_tools = await workflow.execute_activity(
                    get_available_tools,
                    start_to_close_timeout=timedelta(seconds=30)
                )
                
                # Analyze current state and decide next action
                next_action = await workflow.execute_activity(
                    llm_analyze,
                    args=[self.research_context, available_tools],
                    start_to_close_timeout=timedelta(minutes=3),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )
                
                if next_action.get("action") == "complete":
                    workflow.logger.info("Research completed by agent decision")
                    break
                
                # Validate and execute tool
                if "tool_name" in next_action and "tool_args" in next_action:
                    tool_validation = await workflow.execute_activity(
                        validate_tool_usage,
                        args=[next_action["tool_name"], next_action["tool_args"]],
                        start_to_close_timeout=timedelta(seconds=30)
                    )
                    
                    if tool_validation["valid"]:
                        # Execute dynamic tool activity
                        tool_result = await workflow.execute_activity(
                            dynamic_tool_activity,
                            args=[next_action["tool_name"], next_action["tool_args"]],
                            start_to_close_timeout=timedelta(minutes=10),
                            retry_policy=RetryPolicy(maximum_attempts=2)
                        )
                        
                        # Update research context with results
                        self._update_context_with_results(tool_result, next_action["tool_name"])
                    else:
                        workflow.logger.warning(f"Tool validation failed: {tool_validation['reason']}")
                
                # Brief pause between iterations
                await asyncio.sleep(1)
            
            # Step 3: Generate final research summary
            self.research_context["status"] = "summarizing"
            final_summary = await workflow.execute_activity(
                llm_analyze,
                args=[self.research_context, [], "summarize"],
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            self.research_context["status"] = "completed"
            self.research_context["summary"] = final_summary
            
            return {
                "success": True,
                "research_context": self.research_context,
                "papers_discovered": len(self.discovered_papers),
                "analysis_count": len(self.analysis_results),
                "final_summary": final_summary
            }
            
        except Exception as e:
            workflow.logger.error(f"Research workflow failed: {str(e)}")
            self.research_context["status"] = "failed"
            self.research_context["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "research_context": self.research_context
            }

    def _update_context_with_results(self, tool_result: Dict[str, Any], tool_name: str) -> None:
        """Update research context with tool execution results."""
        
        # Handle enhanced arXiv search results
        if tool_name in ["arxiv_search_papers", "arxiv_search"] and "papers" in tool_result:
            self.discovered_papers.extend(tool_result["papers"])
            self.research_context["papers_count"] = len(self.discovered_papers)
            
            # Track local storage status for enhanced tools
            if tool_name == "arxiv_search_papers":
                downloaded_count = sum(1 for paper in tool_result["papers"] if paper.get("is_downloaded", False))
                self.research_context["papers_downloaded"] = downloaded_count
        
        # Handle paper download results
        elif tool_name == "arxiv_download_paper" and tool_result.get("success"):
            if "downloaded_papers" not in self.research_context:
                self.research_context["downloaded_papers"] = []
            if "paper_id" in tool_result:
                self.research_context["downloaded_papers"].append(tool_result["paper_id"])
        
        # Handle paper reading results
        elif tool_name == "arxiv_read_paper" and tool_result.get("success"):
            if "read_papers" not in self.research_context:
                self.research_context["read_papers"] = []
            if "paper_id" in tool_result:
                self.research_context["read_papers"].append(tool_result["paper_id"])
            
            # Track extracted content if available
            if "content" in tool_result and "paper_id" in tool_result:
                if "extracted_content" not in self.research_context:
                    self.research_context["extracted_content"] = []
                self.research_context["extracted_content"].append({
                    "paper_id": tool_result["paper_id"],
                    "sections_found": len(tool_result["content"].get("sections", {}))
                })
        
        # Handle citation analysis
        elif tool_name in ["extract_citations", "analyze_citation_network"]:
            if "citations" in tool_result:
                if "citations" not in self.research_context:
                    self.research_context["citations"] = []
                self.research_context["citations"].extend(tool_result["citations"])
            
            if "network" in tool_result:
                self.research_context["citation_network"] = tool_result["network"]
        
        # Handle PDF analysis
        elif tool_name in ["process_pdf", "extract_sections"] and "content" in tool_result:
            self.analysis_results.append(tool_result["content"])
            self.research_context["analysis_count"] = len(self.analysis_results)
        
        # Handle similarity analysis
        elif tool_name in ["find_similar_papers", "calculate_similarity"]:
            if "similar_papers" in tool_result:
                if "similar_papers" not in self.research_context:
                    self.research_context["similar_papers"] = []
                self.research_context["similar_papers"].extend(tool_result["similar_papers"])
            
            if "similarity" in tool_result:
                if "similarity_scores" not in self.research_context:
                    self.research_context["similarity_scores"] = []
                self.research_context["similarity_scores"].append(tool_result["similarity"])
        
        # Store latest tool result
        if "tool_results" not in self.research_context:
            self.research_context["tool_results"] = []
        
        self.research_context["tool_results"].append({
            "tool": tool_name,
            "result": tool_result,
            "timestamp": workflow.now()
        })

    @workflow.query
    def get_current_status(self) -> Dict[str, Any]:
        """Query current research status."""
        return {
            "status": self.research_context.get("status", "unknown"),
            "iteration": self.research_context.get("iteration", 0),
            "papers_discovered": len(self.discovered_papers),
            "analysis_count": len(self.analysis_results)
        }

    @workflow.signal
    def update_research_focus(self, new_focus: str) -> None:
        """Signal to update research focus during execution."""
        self.research_context["updated_focus"] = new_focus
        workflow.logger.info(f"Research focus updated: {new_focus}")