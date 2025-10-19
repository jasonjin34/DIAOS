import { geolocation } from "@vercel/functions";
import {
  convertToModelMessages,
  createUIMessageStream,
  JsonToSseTransformStream,
  smoothStream,
  stepCountIs,
  streamText,
} from "ai";

// Smart detection for research requests
function isDeepResearchRequest(message: string): boolean {
  const researchKeywords = [
    "comprehensive research",
    "deep research",
    "do research",
    "analyze papers",
    "academic research",
    "literature review",
    "research papers",
    "arxiv search",
    "citation analysis",
    "research on",
    "study on",
    "investigate",
    "comprehensive analysis",
    "survey papers",
    "systematic review",
  ];

  const lowerMessage = message.toLowerCase();
  return researchKeywords.some((keyword) => lowerMessage.includes(keyword));
}

import { unstable_cache as cache } from "next/cache";
import { after } from "next/server";
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from "resumable-stream";
import type { ModelCatalog } from "tokenlens/core";
import { fetchModels } from "tokenlens/fetch";
import { getUsage } from "tokenlens/helpers";
import { auth, type UserType } from "@/app/(auth)/auth";
import type { VisibilityType } from "@/components/visibility-selector";
import { entitlementsByUserType } from "@/lib/ai/entitlements";
import type { ChatModel } from "@/lib/ai/models";
import { type RequestHints, systemPrompt } from "@/lib/ai/prompts";
import { myProvider } from "@/lib/ai/providers";
import { createDocument } from "@/lib/ai/tools/create-document";
import { isProductionEnvironment } from "@/lib/constants";
import {
  createStreamId,
  deleteChatById,
  getChatById,
  getMessageCountByUserId,
  getMessagesByChatId,
  saveChat,
  saveMessages,
  updateChatLastContextById,
} from "@/lib/db/queries";
import { ChatSDKError } from "@/lib/errors";
import type { ChatMessage } from "@/lib/types";
import type { AppUsage } from "@/lib/usage";
import { convertToUIMessages, generateUUID } from "@/lib/utils";
import { generateTitleFromUserMessage } from "../../actions";
import { type PostRequestBody, postRequestBodySchema } from "./schema";

export const maxDuration = 600; // 10 minutes for research workflows

let globalStreamContext: ResumableStreamContext | null = null;

const getTokenlensCatalog = cache(
  async (): Promise<ModelCatalog | undefined> => {
    try {
      return await fetchModels();
    } catch (err) {
      console.warn(
        "TokenLens: catalog fetch failed, using default catalog",
        err
      );
      return; // tokenlens helpers will fall back to defaultCatalog
    }
  },
  ["tokenlens-catalog"],
  { revalidate: 24 * 60 * 60 } // 24 hours
);

export function getStreamContext() {
  if (!globalStreamContext) {
    try {
      globalStreamContext = createResumableStreamContext({
        waitUntil: after,
      });
    } catch (error: any) {
      if (error.message.includes("REDIS_URL")) {
        console.log(
          " > Resumable streams are disabled due to missing REDIS_URL"
        );
      } else {
        console.error(error);
      }
    }
  }

  return globalStreamContext;
}

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    requestBody = postRequestBodySchema.parse(json);
  } catch (_) {
    return new ChatSDKError("bad_request:api").toResponse();
  }

  try {
    const {
      id,
      message,
      selectedChatModel,
      selectedVisibilityType,
    }: {
      id: string;
      message: ChatMessage;
      selectedChatModel: ChatModel["id"];
      selectedVisibilityType: VisibilityType;
    } = requestBody;

    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError("unauthorized:chat").toResponse();
    }

    const userType: UserType = session.user.type;

    const messageCount = await getMessageCountByUserId({
      id: session.user.id,
      differenceInHours: 24,
    });

    if (messageCount > entitlementsByUserType[userType].maxMessagesPerDay) {
      return new ChatSDKError("rate_limit:chat").toResponse();
    }

    const chat = await getChatById({ id });

    if (chat) {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError("forbidden:chat").toResponse();
      }
    } else {
      const title = await generateTitleFromUserMessage({
        message,
      });

      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
      });
    }

    const messagesFromDb = await getMessagesByChatId({ id });
    const uiMessages = [...convertToUIMessages(messagesFromDb), message];

    const { longitude, latitude, city, country } = geolocation(request);

    const requestHints: RequestHints = {
      longitude,
      latitude,
      city,
      country,
    };

    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: "user",
          parts: message.parts,
          attachments: [],
          createdAt: new Date(),
        },
      ],
    });

    // Check if this is a research request and start Temporal workflow
    const firstPart = message.parts?.[0];
    const userText = firstPart && "text" in firstPart ? firstPart.text : "";
    const needsResearchWorkflow = isDeepResearchRequest(userText);

    console.log("=== CHAT API REQUEST ANALYSIS ===");
    console.log("User Text:", userText);
    console.log("Needs Research Workflow:", needsResearchWorkflow);
    console.log("Message Parts:", message.parts);
    console.log("================================");

    let workflowInfo = "";
    let researchTopic = "";
    let documentId = "";
    let workflowId = "";

    if (needsResearchWorkflow) {
      console.log("🔬 STARTING RESEARCH WORKFLOW PROCESS...");
      try {
        console.log("📡 Creating Temporal client connection...");
        // Create Temporal client with connection
        const { Connection, Client } = await import("@temporalio/client");
        const connection = await Connection.connect({
          address: process.env.TEMPORAL_SERVER_ADDRESS || "localhost:7233",
        });
        console.log("✅ Temporal connection established");

        const temporalClient = new Client({ connection });

        workflowId = `research-${Date.now()}`;
        console.log("🆔 Generated Workflow ID:", workflowId);

        // Generate document ID and research topic
        documentId = generateUUID();
        researchTopic = userText
          .replace(
            /^(deep research on|do research on|comprehensive research on)\s*/i,
            ""
          )
          .trim();

        // Just start the workflow, completion will happen in streaming
        console.log("🚀 Starting Temporal workflow...");
        console.log("Workflow Args:", [
          userText,
          session.user.id || "anonymous",
          documentId,
        ]);

        console.log("📊 Research workflow info prepared:");
        console.log("- Workflow ID:", workflowId);
        console.log("- Document ID:", documentId);
        console.log("- Research Topic:", researchTopic);
      } catch (temporalError) {
        console.error("Failed to start Temporal workflow:", temporalError);
        workflowInfo =
          "\n\n⚠️ Could not start research workflow. Temporal server may not be running.";
      }
    }

    // For research requests, return streaming response with workflow info only (no GPT generation)
    if (needsResearchWorkflow && workflowId) {
      console.log(
        "🚀 RESEARCH REQUEST - Creating streaming response with workflow info only"
      );
      console.log("- Workflow ID:", workflowId);
      console.log("- Document ID:", documentId);
      console.log("- Skipping GPT streamText() call entirely");

      const streamId = generateUUID();
      await createStreamId({ streamId, chatId: id });

      // Create a streaming response that shows loading then final results
      const stream = createUIMessageStream({
        execute: async ({ writer: dataStream }) => {
          console.log(
            "📝 SENDING RESEARCH RESPONSE - Showing loading then results"
          );

          const messageId = generateUUID();

          // First show loading state
          dataStream.write({
            type: "text-start",
            id: messageId,
          });

          const loadingMessage = `**Starting Deep Research on ${researchTopic}**

I'm conducting comprehensive academic research using Temporal workflows. This may take 2-5 minutes.

**Workflow ID:** ${workflowId}

**Current Status:** Initializing research plan...
- Searching academic databases
- Analyzing papers and citations  
- Generating insights and recommendations

Please wait while I complete the analysis...`;

          dataStream.write({
            type: "text-delta",
            id: messageId,
            delta: loadingMessage,
          });

          // NOW start and wait for the workflow (blocking inside stream)
          try {
            // Create Temporal client inside stream
            const { Connection, Client } = await import("@temporalio/client");
            const connection = await Connection.connect({
              address: process.env.TEMPORAL_SERVER_ADDRESS || "localhost:7233",
            });
            const temporalClient = new Client({ connection });

            const workflowHandle = await temporalClient.workflow.start(
              "ResearchWorkflow",
              {
                args: [userText, session.user.id || "anonymous", documentId],
                taskQueue: "research-agent-queue",
                workflowId,
              }
            );

            console.log("✅ Temporal workflow started successfully!");
            console.log(
              "⏳ Waiting for workflow to complete (this may take 2-5 minutes)..."
            );

            // WAIT for the workflow to complete (blocking)
            const workflowResult = await workflowHandle.result();

            console.log("🎉 Workflow completed! Result:", workflowResult);

            // Format the research results for display
            let finalResults;
            if (workflowResult.success && workflowResult.final_summary) {
              const stats = workflowResult.final_summary.research_stats || {};

              finalResults = `

# Deep Research: ${researchTopic}

**Status:** Completed  
**Workflow ID:** ${workflowId}  
**Completed:** ${new Date().toLocaleString()}

## Research Summary

${workflowResult.final_summary.summary || "Research analysis completed successfully."}

## Research Statistics
- **Papers Discovered:** ${workflowResult.papers_discovered || 0}
- **Analysis Iterations:** ${stats.iterations_completed || 0}  
- **Tools Used:** ${stats.tools_used || 0}
- **Papers Analyzed:** ${stats.papers_analyzed || 0}

---
*Research completed using Temporal workflows with comprehensive academic analysis.*`;
            } else {
              finalResults = `

# Deep Research: ${researchTopic}

**Status:** Completed with Issues  
**Workflow ID:** ${workflowId}  
**Completed:** ${new Date().toLocaleString()}

## Error Information
Research workflow completed but encountered issues during processing.

---
*Research powered by Temporal workflows*`;
            }

            // Replace loading message with final results
            dataStream.write({
              type: "text-delta",
              id: messageId,
              delta: finalResults,
            });
          } catch (error) {
            console.error("❌ Workflow execution failed:", error);
            const errorMessage =
              error instanceof Error ? error.message : "Unknown error";
            dataStream.write({
              type: "text-delta",
              id: messageId,
              delta: `\n\n❌ **Research Failed**\n\nError: ${errorMessage}\n\nPlease try again.`,
            });
          }

          dataStream.write({
            type: "text-end",
            id: messageId,
          });
        },
        generateId: generateUUID,
        onFinish: async ({ messages }) => {
          console.log("💾 SAVING WORKFLOW MESSAGE - Saving to database");
          await saveMessages({
            messages: messages.map((currentMessage) => ({
              id: currentMessage.id,
              role: currentMessage.role,
              parts: currentMessage.parts,
              createdAt: new Date(),
              attachments: [],
              chatId: id,
            })),
          });
        },
        onError: () => {
          return "Oops, an error occurred while starting research!";
        },
      });

      return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
    }

    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    let finalMergedUsage: AppUsage | undefined;

    console.log("🎯 PREPARING GPT RESPONSE...");
    console.log("Will use GPT for research workflow:", needsResearchWorkflow);

    if (needsResearchWorkflow) {
      console.log(
        "⚠️ WARNING: GPT will generate content while Temporal is processing!"
      );
      console.log("System prompt will include:", {
        researchTopic,
        workflowId,
        documentId,
        workflowInfo: workflowInfo.substring(0, 100) + "...",
      });
    }

    const stream = createUIMessageStream({
      execute: ({ writer: dataStream }) => {
        console.log("🚀 Starting GPT text generation...");

        const result = streamText({
          model: myProvider.languageModel(selectedChatModel),
          system: `${systemPrompt({ selectedChatModel, requestHints })}
          
          ${
            needsResearchWorkflow
              ? `The user has requested comprehensive research. You must create a document titled "Deep Research: ${researchTopic}" with initial research content showing workflow status. A Temporal workflow has been started to conduct deep academic research.${workflowInfo}`
              : 'For comprehensive research requests, suggest the user ask for "deep research" or "comprehensive research" to trigger our academic workflow.'
          }`,
          messages: convertToModelMessages(uiMessages),
          stopWhen: stepCountIs(5),
          experimental_transform: smoothStream({ chunking: "word" }),
          tools: needsResearchWorkflow
            ? {
                createDocument: createDocument({ session, dataStream }),
              }
            : {},
          experimental_telemetry: {
            isEnabled: isProductionEnvironment,
            functionId: "stream-text",
          },
          onFinish: async ({ usage }) => {
            try {
              const providers = await getTokenlensCatalog();
              const modelId =
                myProvider.languageModel(selectedChatModel).modelId;
              if (!modelId) {
                finalMergedUsage = usage;
                dataStream.write({
                  type: "data-usage",
                  data: finalMergedUsage,
                });
                return;
              }

              if (!providers) {
                finalMergedUsage = usage;
                dataStream.write({
                  type: "data-usage",
                  data: finalMergedUsage,
                });
                return;
              }

              const summary = getUsage({ modelId, usage, providers });
              finalMergedUsage = { ...usage, ...summary, modelId } as AppUsage;
              dataStream.write({ type: "data-usage", data: finalMergedUsage });
            } catch (err) {
              console.warn("TokenLens enrichment failed", err);
              finalMergedUsage = usage;
              dataStream.write({ type: "data-usage", data: finalMergedUsage });
            }
          },
        });

        result.consumeStream();

        dataStream.merge(
          result.toUIMessageStream({
            sendReasoning: true,
          })
        );
      },
      generateId: generateUUID,
      onFinish: async ({ messages }) => {
        await saveMessages({
          messages: messages.map((currentMessage) => ({
            id: currentMessage.id,
            role: currentMessage.role,
            parts: currentMessage.parts,
            createdAt: new Date(),
            attachments: [],
            chatId: id,
          })),
        });

        if (finalMergedUsage) {
          try {
            await updateChatLastContextById({
              chatId: id,
              context: finalMergedUsage,
            });
          } catch (err) {
            console.warn("Unable to persist last usage for chat", id, err);
          }
        }
      },
      onError: () => {
        return "Oops, an error occurred!";
      },
    });

    // const streamContext = getStreamContext();

    // if (streamContext) {
    //   return new Response(
    //     await streamContext.resumableStream(streamId, () =>
    //       stream.pipeThrough(new JsonToSseTransformStream())
    //     )
    //   );
    // }

    return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
  } catch (error) {
    const vercelId = request.headers.get("x-vercel-id");

    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }

    // Check for Vercel AI Gateway credit card error
    if (
      error instanceof Error &&
      error.message?.includes(
        "AI Gateway requires a valid credit card on file to service requests"
      )
    ) {
      return new ChatSDKError("bad_request:activate_gateway").toResponse();
    }

    console.error("Unhandled error in chat API:", error, { vercelId });
    return new ChatSDKError("offline:chat").toResponse();
  }
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  if (!id) {
    return new ChatSDKError("bad_request:api").toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError("unauthorized:chat").toResponse();
  }

  const chat = await getChatById({ id });

  if (chat?.userId !== session.user.id) {
    return new ChatSDKError("forbidden:chat").toResponse();
  }

  const deletedChat = await deleteChatById({ id });

  return Response.json(deletedChat, { status: 200 });
}
