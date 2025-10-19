"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "./ui/button";

interface ActivityMonitorProps {
  workflowId: string;
  isVisible: boolean;
  onClose: () => void;
}

interface ActivityStatus {
  status: string;
  iteration: number;
  papers_discovered: number;
  analysis_count: number;
  activity?: string;
  detailed_status?: any;
}

interface ActivityLogEntry {
  timestamp: string;
  type: "status" | "tool" | "discovery" | "analysis";
  message: string;
  details?: any;
}

// Static ID for the monitor document (not saved to database)
const MONITOR_DOCUMENT_ID = "monitor-document-id";

export function ResearchActivityMonitor({
  workflowId,
  isVisible,
  onClose,
}: ActivityMonitorProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [activityStatus, setActivityStatus] = useState<ActivityStatus | null>(
    null
  );
  const [isCompleted, setIsCompleted] = useState(false);
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!workflowId || !isVisible || isCompleted) return;

    const pollActivity = async () => {
      try {
        const response = await fetch(`/api/research/poll/${workflowId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ documentId: MONITOR_DOCUMENT_ID }),
        });

        if (!response.ok) {
          if (response.status === 404) {
            // Workflow not found - stop polling gracefully
            console.log("Workflow not found, stopping monitor");
            setIsCompleted(true);
            return;
          }
          if (response.status >= 500) {
            // Server error - continue polling but log warning
            console.log(
              "Server error during polling, will retry:",
              response.status
            );
            return;
          }
          // Other errors - try to get response data
          try {
            const data = await response.json();
            if (data.completed || data.error) {
              setIsCompleted(true);
              return;
            }
          } catch {
            // Cannot parse response, continue polling
            console.log("Could not parse polling response, continuing...");
            return;
          }
        }

        // Process successful response
        const data = await response.json();

        if (data.completed || data.error) {
          setIsCompleted(true);
          setActivityStatus((prev) =>
            prev ? { ...prev, status: "completed" } : null
          );
          return;
        }

        if (data.running && data.progress) {
          const newStatus = {
            status: data.progress.status || "running",
            iteration: data.progress.iteration || 0,
            papers_discovered: data.progress.papers_discovered || 0,
            analysis_count: data.progress.analysis_count || 0,
            activity: data.progress.activity || "processing...",
            detailed_status: data.progress.detailed_status,
          };

          setActivityStatus(newStatus);

          // Only log key summary updates, not every activity
          const activityMessage = data.progress.activity || "processing...";

          // Only show essential milestones - filter out verbose activities
          const isSummaryActivity =
            activityMessage.includes("Final summary") ||
            activityMessage.includes("Research complete") ||
            activityMessage.includes("Starting research") ||
            activityMessage.includes("New iteration") ||
            (newStatus.iteration !== activityStatus?.iteration &&
              newStatus.iteration % 2 === 0); // Only log every 2nd iteration

          if (isSummaryActivity) {
            const timestamp = new Date().toLocaleTimeString();

            setActivityLog((prev) => {
              // Don't duplicate the same message
              if (
                prev.length > 0 &&
                prev[prev.length - 1].message === activityMessage
              ) {
                return prev;
              }

              const newEntry: ActivityLogEntry = {
                timestamp,
                type: "status",
                message: activityMessage,
                details: {
                  iteration: newStatus.iteration,
                  papers: newStatus.papers_discovered,
                  analyses: newStatus.analysis_count,
                },
              };

              return [...prev, newEntry];
            });
          }
        }
      } catch (error) {
        console.log("Activity monitor polling error:", error);
      }
    };

    // Poll every 3 seconds
    const interval = setInterval(pollActivity, 3000);
    pollActivity(); // Initial poll

    return () => clearInterval(interval);
  }, [workflowId, isVisible, isCompleted]);

  if (!isVisible) return null;

  return (
    <div className="w-full max-w-4xl">
      {isMinimized ? (
        // Minimized state - small banner
        <div className="mb-2 flex items-center justify-between rounded-lg border border-gray-700 bg-gray-900 px-3 py-2">
          <div className="flex items-center gap-2 text-blue-400 text-sm">
            <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
            <span>Research Monitor ({activityLog.length} activities)</span>
          </div>
          <Button
            className="h-6 text-blue-400 hover:bg-gray-800"
            onClick={() => setIsMinimized(false)}
            size="sm"
            variant="ghost"
          >
            Expand
          </Button>
        </div>
      ) : (
        // Expanded state - full monitor with activity log
        <div className="mb-2 max-w-4xl rounded-lg border border-gray-700 bg-gray-900 shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between rounded-t-lg border-gray-700 border-b bg-gray-800 px-4 py-2">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
              <span className="font-medium text-gray-100 text-sm">
                Research Monitor
              </span>
            </div>
            <div className="flex gap-1">
              <Button
                className="h-6 px-2 text-gray-300 text-xs hover:bg-gray-700"
                onClick={() => setIsMinimized(true)}
                size="sm"
                variant="ghost"
              >
                Minimize
              </Button>
              <Button
                className="h-6 px-2 text-gray-300 text-xs hover:bg-gray-700"
                onClick={onClose}
                size="sm"
                variant="ghost"
              >
                Close
              </Button>
            </div>
          </div>

          {/* Content */}
          <div className="flex h-64 flex-col">
            {/* Status Header */}
            <div className="border-gray-700 border-b bg-gray-800 px-4 py-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">
                  Workflow: {workflowId.slice(-8)}...
                </span>
                {activityStatus && (
                  <div className="flex gap-4 text-gray-300 text-xs">
                    <span>Iter: {activityStatus.iteration + 1}</span>
                    <span>Papers: {activityStatus.papers_discovered}</span>
                    <span>Analysis: {activityStatus.analysis_count}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Scrollable Activity Log */}
            <div
              className="max-h-48 flex-1 space-y-2 overflow-y-auto bg-gray-900 p-3"
              ref={scrollRef}
              style={{
                scrollbarWidth: "thin",
                scrollbarColor: "#4B5563 #1F2937",
              }}
            >
              {activityLog.length > 0 ? (
                activityLog.map((entry, index) => (
                  <div className="flex gap-2 text-xs" key={index}>
                    <span className="w-16 shrink-0 font-mono text-gray-500">
                      {entry.timestamp}
                    </span>
                    <div className="flex-1">
                      <div className="text-gray-200 leading-relaxed">
                        {entry.message}
                      </div>
                      {entry.details && (
                        <div className="mt-1 text-gray-400 text-xs">
                          Iteration {entry.details.iteration + 1} •{" "}
                          {entry.details.papers} papers •{" "}
                          {entry.details.analyses} analyses
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex h-full items-center justify-center text-gray-400 text-sm">
                  {activityStatus ? (
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 animate-spin rounded-full border-2 border-blue-600 border-t-blue-400" />
                      <span>Monitoring workflow activities...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 animate-spin rounded-full border-2 border-gray-600 border-t-gray-400" />
                      <span>Connecting to workflow...</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-gray-700 border-t bg-gray-800 px-3 py-2 text-gray-400 text-xs">
              <span>{activityLog.length} activities logged</span>
              {!isCompleted && (
                <div className="flex items-center gap-1">
                  <div className="h-1 w-1 animate-pulse rounded-full bg-green-400" />
                  <span>Live updates</span>
                </div>
              )}
              {isCompleted && (
                <span className="font-medium text-green-400">✓ Completed</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
