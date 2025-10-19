import { useEffect, useRef } from "react";

interface ResearchPollingOptions {
  workflowId: string;
  documentId: string;
  onUpdate?: () => void;
  enabled?: boolean;
}

export function useResearchPolling({
  workflowId,
  documentId,
  onUpdate,
  enabled = true,
}: ResearchPollingOptions) {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const completedRef = useRef(false);

  useEffect(() => {
    console.log("🔄 RESEARCH POLLING HOOK - Setup");
    console.log("- Enabled:", enabled);
    console.log("- Workflow ID:", workflowId);
    console.log("- Document ID:", documentId);
    console.log("- Already Completed:", completedRef.current);

    if (!enabled || !workflowId || !documentId || completedRef.current) {
      console.log(
        "❌ POLLING HOOK - Not starting polling due to missing requirements"
      );
      return;
    }

    console.log("✅ POLLING HOOK - Starting workflow polling...");

    const pollWorkflow = async () => {
      try {
        console.log("🌐 POLLING REQUEST - Sending poll request");
        console.log("- Target URL:", `/api/research/poll/${workflowId}`);
        console.log("- Request Body:", { documentId });

        const response = await fetch(`/api/research/poll/${workflowId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ documentId }),
        });

        console.log("📥 POLLING RESPONSE - Received response");
        console.log("- Response OK:", response.ok);
        console.log("- Response Status:", response.status);

        if (response.ok) {
          const data = await response.json();

          console.log("📊 POLLING DATA - Response data received:");
          console.log("- Data:", JSON.stringify(data, null, 2));
          console.log("- Completed:", data.completed);
          console.log("- Error:", data.error);
          console.log("- Running:", data.running);
          console.log("- Document Updated:", data.documentUpdated);

          if (data.completed || data.error) {
            // Workflow completed or failed - stop polling
            console.log("🏁 POLLING COMPLETE - Stopping polling");
            console.log(
              "- Reason:",
              data.completed ? "Workflow completed" : "Workflow error"
            );
            console.log(
              "- Final Statistics:",
              data.statistics || "No statistics"
            );

            completedRef.current = true;
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }

            // Trigger document refresh to show updated content
            console.log("🔄 TRIGGERING UPDATE - Calling onUpdate callback");
            if (onUpdate) {
              onUpdate();
            }

            console.log(
              "Research completed:",
              data.statistics || "No statistics available"
            );
          } else if (data.running && data.progress) {
            // Workflow still running - could show progress if needed
            console.log("⏳ POLLING PROGRESS - Workflow still running");
            console.log("- Progress Data:", data.progress);
            console.log("Research progress:", data.progress);
          } else {
            console.log("⚠️ POLLING UNKNOWN - Unexpected response format");
          }
        } else {
          console.error(
            "❌ POLLING ERROR - Response not OK:",
            response.status,
            response.statusText
          );
        }
      } catch (error) {
        console.error("💥 POLLING EXCEPTION - Error during polling:", error);
      }
    };

    // Start polling every 10 seconds
    console.log("⏰ SETTING UP POLLING INTERVAL - Every 10 seconds");
    intervalRef.current = setInterval(pollWorkflow, 10_000);

    // Initial poll
    console.log("🚀 INITIAL POLL - Running first poll immediately");
    pollWorkflow();

    // Cleanup on unmount
    return () => {
      console.log(
        "🧹 POLLING CLEANUP - Component unmounting, clearing interval"
      );
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [workflowId, documentId, onUpdate, enabled]);

  // Cleanup function to stop polling manually
  const stopPolling = () => {
    console.log("🛑 MANUAL STOP POLLING - Stopping polling manually");
    completedRef.current = true;
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  return { stopPolling };
}
