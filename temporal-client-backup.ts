// TEMPORAL CLIENT BACKUP - Chat API Route with Research Workflow Integration
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { Client } from '@temporalio/client';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  throw new Error('OPENAI_API_KEY environment variable is required');
}

// Smart detection for research requests
function isDeepResearchRequest(message: string): boolean {
  const researchKeywords = [
    'comprehensive research',
    'deep research', 
    'do research',
    'analyze papers',
    'academic research',
    'literature review',
    'research papers',
    'arxiv search',
    'citation analysis',
    'research on',
    'study on',
    'investigate',
    'comprehensive analysis',
    'survey papers',
    'systematic review'
  ];
  
  const lowerMessage = message.toLowerCase();
  return researchKeywords.some(keyword => lowerMessage.includes(keyword));
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    
    // Get the latest user message
    const userMessage = messages[messages.length - 1];
    if (!userMessage || userMessage.role !== 'user') {
      return new Response('Invalid message format', { status: 400 });
    }

    const userText = userMessage.content;
    const needsResearchWorkflow = isDeepResearchRequest(userText);
    
    let workflowInfo = '';
    
    // Try to start Temporal workflow for comprehensive research
    if (needsResearchWorkflow) {
      try {
        const client = new Client();
        const workflowId = `research-${Date.now()}`;
        
        await client.workflow.start('ResearchWorkflow', {
          args: [userText, 'chat-user'],
          taskQueue: 'research-agent-queue',
          workflowId,
        });
        
        workflowInfo = `\n\n🔬 **Research Workflow Started**\nWorkflow ID: ${workflowId}\n\nI've initiated a comprehensive research workflow that will:\n1. Search academic papers on arXiv\n2. Download and analyze relevant papers\n3. Extract citations and build citation networks\n4. Provide detailed insights and summaries\n\nYou can check the workflow status in your Temporal UI.`;
        
        console.log(`Started research workflow: ${workflowId}`);
      } catch (temporalError) {
        console.error('Failed to start Temporal workflow:', temporalError);
        workflowInfo = '\n\n⚠️ Could not start research workflow. Temporal server may not be running.';
      }
    }

    const result = streamText({
      model: openai('gpt-4'),
      system: `You are an AI research assistant. Answer questions clearly and concisely.
      
      ${needsResearchWorkflow ? 
        `The user has requested comprehensive research. A Temporal workflow has been started to conduct deep academic research.${workflowInfo}` :
        'For comprehensive research requests, suggest the user ask for "deep research" or "comprehensive research" to trigger our academic workflow.'
      }
      
      Be helpful, professional, and informative.`,
      messages,
    });

    return result.toTextStreamResponse();
    
  } catch (error) {
    console.error('Chat API error:', error);
    return new Response('Internal server error', { status: 500 });
  }
}