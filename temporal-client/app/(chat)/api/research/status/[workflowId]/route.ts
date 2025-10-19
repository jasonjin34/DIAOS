import { Client } from "@temporalio/client";
import type { NextRequest } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  const { workflowId } = await params;

  if (!workflowId) {
    return Response.json({ error: "Workflow ID is required" }, { status: 400 });
  }

  try {
    // Connect to Temporal server
    const { Connection, Client } = await import("@temporalio/client");
    const connection = await Connection.connect({
      address: process.env.TEMPORAL_SERVER_ADDRESS || "localhost:7233",
    });
    const temporalClient = new Client({ connection });

    // Get workflow handle
    const workflowHandle = temporalClient.workflow.getHandle(workflowId);

    // Get workflow info
    const workflowInfo = await workflowHandle.describe();

    const response: any = {
      workflowId,
      status: workflowInfo.status.name.toLowerCase(),
    };

    // Check if workflow is completed
    if (workflowInfo.status.name === "COMPLETED") {
      try {
        // Get the workflow result
        const result = await workflowHandle.result();
        response.result = result;
        response.completedAt = workflowInfo.closeTime;
      } catch (error) {
        console.error("Error getting workflow result:", error);
        response.error = "Failed to retrieve workflow result";
      }
    } else if (workflowInfo.status.name === "FAILED") {
      response.error = "Workflow execution failed";
    } else if (workflowInfo.status.name === "RUNNING") {
      response.startedAt = workflowInfo.startTime;
      response.message = "Research workflow is currently running...";
    }

    return Response.json(response);
  } catch (error) {
    console.error("Error checking workflow status:", error);

    // Check if it's a "workflow not found" error
    if (error instanceof Error && error.message.includes("not found")) {
      return Response.json(
        {
          error: "Workflow not found",
          workflowId,
        },
        { status: 404 }
      );
    }

    return Response.json(
      {
        error: "Failed to check workflow status",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
