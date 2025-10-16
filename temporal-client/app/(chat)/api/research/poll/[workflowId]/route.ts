import { Client } from '@temporalio/client';
import { NextRequest } from 'next/server';
import { getDocumentById, saveDocument } from '@/lib/db/queries';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;
    const { documentId } = await request.json();

    if (!workflowId || !documentId) {
      return Response.json({ error: 'Workflow ID and Document ID are required' }, { status: 400 });
    }

    // Connect to Temporal server
    const { Connection, Client } = await import('@temporalio/client');
    const connection = await Connection.connect({
      address: process.env.TEMPORAL_SERVER_ADDRESS || 'localhost:7233',
    });
    const temporalClient = new Client({ connection });

    // Get workflow handle
    const workflowHandle = temporalClient.workflow.getHandle(workflowId);
    
    // Get workflow info
    const workflowInfo = await workflowHandle.describe();
    
    const response: any = {
      workflowId,
      status: workflowInfo.status.name.toLowerCase(),
      documentId,
    };

    // Check if workflow is completed
    if (workflowInfo.status.name === 'COMPLETED') {
      try {
        // Get the workflow result
        const result = await workflowHandle.result();
        
        console.log('=== TEMPORAL WORKFLOW RESULT ===');
        console.log('Full Result:', JSON.stringify(result, null, 2));
        console.log('Success:', result?.success);
        console.log('Papers Discovered:', result?.papers_discovered);
        console.log('Final Summary:', result?.final_summary);
        console.log('Research Context:', result?.research_context);
        console.log('================================');
        
        if (result && result.success) {
          // Get the current document to preserve topic
          const currentDoc = await getDocumentById({ id: documentId });
          const researchTopic = currentDoc?.title?.replace('Deep Research: ', '') || 'Research Topic';
          
          // Format the complete research document
          const completedDocumentContent = `# Deep Research: ${researchTopic}

**Status:** ✅ Completed  
**Workflow ID:** ${workflowId}  
**Completed:** ${new Date().toLocaleString()}

## Research Summary

${result.final_summary?.summary || 'Research analysis completed successfully.'}

## Research Statistics
- **Papers Discovered:** ${result.papers_discovered || 0}
- **Analysis Iterations:** ${result.research_context?.iteration || 0}  
- **Tools Used:** ${result.research_context?.tool_results?.length || 0}
- **Processing Time:** ${Math.round((Date.now() - new Date(workflowInfo.startTime).getTime()) / 1000)} seconds

## Key Papers Found
${result.research_context?.discovered_papers?.slice(0, 5).map((paper: any, index: number) => 
  `${index + 1}. **${paper.title || 'Untitled'}**${paper.authors ? ` - ${paper.authors}` : ''}${paper.published ? ` (${paper.published})` : ''}`
).join('\n') || 'No papers found in results.'}

## Research Methodology
${result.research_context?.plan?.methodology || 'Comprehensive academic literature analysis using multiple research tools and citation network analysis.'}

## Detailed Findings
${result.research_context?.tool_results?.map((tool: any, index: number) => 
  `### ${index + 1}. ${tool.tool} Analysis\n${tool.result?.summary || 'Analysis completed'}`
).join('\n\n') || 'Detailed analysis completed with comprehensive insights.'}

## Citations and References
${result.research_context?.citations?.slice(0, 10).map((citation: any, index: number) => 
  `${index + 1}. ${citation.title || citation.text || 'Reference'}`
).join('\n') || 'Citation analysis completed.'}

---
*Research completed using Temporal workflows with comprehensive academic analysis and citation network mapping.*`;

          // Update the document with completed research
          await saveDocument({
            id: documentId,
            title: `Deep Research: ${researchTopic}`,
            content: completedDocumentContent,
            kind: "text",
            userId: "system", // Since this is from the workflow
          });

          response.completed = true;
          response.documentUpdated = true;
          response.statistics = {
            papers: result.papers_discovered || 0,
            iterations: result.research_context?.iteration || 0,
            tools: result.research_context?.tool_results?.length || 0,
          };
        } else {
          // Update document with error status
          const errorDocumentContent = `# Deep Research: Research Topic

**Status:** ⚠️ Completed with Issues  
**Workflow ID:** ${workflowId}  
**Completed:** ${new Date().toLocaleString()}

## Error Information
Research workflow completed but encountered issues during processing.

Please check the detailed results for more information:
🔗 **Detailed Results:** /api/research/status/${workflowId}

---
*Research powered by Temporal workflows*`;

          await saveDocument({
            id: documentId,
            title: "Deep Research: Error",
            content: errorDocumentContent,
            kind: "text",
            userId: "system",
          });

          response.completed = true;
          response.error = true;
          response.documentUpdated = true;
        }
      } catch (error) {
        console.error('Error getting workflow result:', error);
        
        // Update document with retrieval error
        const errorDocumentContent = `# Deep Research: Research Topic

**Status:** ❌ Error Retrieving Results  
**Workflow ID:** ${workflowId}  
**Error Time:** ${new Date().toLocaleString()}

## Error Information
Error retrieving research results. Please try checking the status manually.

🔗 **Status Check:** /api/research/status/${workflowId}

---
*Research powered by Temporal workflows*`;

        await saveDocument({
          id: documentId,
          title: "Deep Research: Retrieval Error",
          content: errorDocumentContent,
          kind: "text",
          userId: "system",
        });

        response.completed = true;
        response.error = 'Failed to retrieve workflow result';
        response.documentUpdated = true;
      }
    } else if (workflowInfo.status.name === 'FAILED') {
      // Update document with failure status
      const failedDocumentContent = `# Deep Research: Research Topic

**Status:** ❌ Failed  
**Workflow ID:** ${workflowId}  
**Failed Time:** ${new Date().toLocaleString()}

## Error Information
Research workflow failed during execution. Please try starting a new research request.

🔗 **Details:** /api/research/status/${workflowId}

---
*Research powered by Temporal workflows*`;

      await saveDocument({
        id: documentId,
        title: "Deep Research: Failed",
        content: failedDocumentContent,
        kind: "text",
        userId: "system",
      });

      response.completed = true;
      response.error = 'Workflow execution failed';
      response.documentUpdated = true;
    } else if (workflowInfo.status.name === 'RUNNING') {
      // Still running - query workflow for detailed status
      try {
        const workflowStatus = await workflowHandle.query('get_current_status');
        
        console.log('=== WORKFLOW STATUS QUERY ===');
        console.log('Status:', workflowStatus);
        console.log('============================');
        
        // Format activity-based progress message
        const statusData = workflowStatus as any;
        const statusText = statusData.status || 'running';
        const iteration = statusData.iteration || 0;
        const papersFound = statusData.papers_discovered || 0;
        const analyses = statusData.analysis_count || 0;
        
        let activityMessage = '';
        switch (statusText) {
          case 'initializing':
            activityMessage = 'initializing research framework...';
            break;
          case 'planning_complete':
            activityMessage = 'research plan ready, starting execution...';
            break;
          case `iteration_${iteration}`:
            activityMessage = `iteration ${iteration + 1}: analyzing data and selecting tools...`;
            break;
          case 'summarizing':
            activityMessage = 'generating final research summary...';
            break;
          default:
            activityMessage = 'processing research activities...';
        }
        
        response.running = true;
        response.progress = {
          status: statusText,
          iteration: iteration,
          papers_discovered: papersFound,
          analysis_count: analyses,
          activity: activityMessage,
          detailed_status: workflowStatus
        };
      } catch (queryError) {
        console.log('Could not query workflow status:', queryError);
        // Fallback to basic progress
        response.running = true;
        response.progress = {
          status: 'running',
          activity: 'research workflow executing...'
        };
      }
    }

    return Response.json(response);

  } catch (error) {
    console.error('Error polling workflow:', error);
    
    return Response.json({ 
      error: 'Failed to poll workflow status',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}