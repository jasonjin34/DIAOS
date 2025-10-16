"use client";

import { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';

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
  type: 'status' | 'tool' | 'discovery' | 'analysis';
  message: string;
  details?: any;
}

export function ResearchActivityMonitor({ workflowId, isVisible, onClose }: ActivityMonitorProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [activityStatus, setActivityStatus] = useState<ActivityStatus | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!workflowId || !isVisible || isCompleted) return;

    const pollActivity = async () => {
      try {
        const response = await fetch(`/api/research/poll/${workflowId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ documentId: 'monitor' }),
        });

        if (response.ok) {
          const data = await response.json();
          
          if (data.completed || data.error) {
            setIsCompleted(true);
            setActivityStatus(prev => prev ? { ...prev, status: 'completed' } : null);
            return;
          }

          if (data.running && data.progress) {
            const newStatus = {
              status: data.progress.status || 'running',
              iteration: data.progress.iteration || 0,
              papers_discovered: data.progress.papers_discovered || 0,
              analysis_count: data.progress.analysis_count || 0,
              activity: data.progress.activity || 'processing...',
              detailed_status: data.progress.detailed_status
            };
            
            setActivityStatus(newStatus);
            
            // Only log key summary updates, not every activity
            const activityMessage = data.progress.activity || 'processing...';
            
            // Only show essential milestones - filter out verbose activities
            const isSummaryActivity = activityMessage.includes('Final summary') || 
                                    activityMessage.includes('Research complete') ||
                                    activityMessage.includes('Starting research') ||
                                    activityMessage.includes('New iteration') ||
                                    (newStatus.iteration !== activityStatus?.iteration && newStatus.iteration % 2 === 0); // Only log every 2nd iteration
            
            if (isSummaryActivity) {
              const timestamp = new Date().toLocaleTimeString();
              
              setActivityLog(prev => {
                // Don't duplicate the same message
                if (prev.length > 0 && prev[prev.length - 1].message === activityMessage) {
                  return prev;
                }
                
                const newEntry: ActivityLogEntry = {
                  timestamp,
                  type: 'status',
                  message: activityMessage,
                  details: {
                    iteration: newStatus.iteration,
                    papers: newStatus.papers_discovered,
                    analyses: newStatus.analysis_count
                  }
                };
                
                return [...prev, newEntry];
              });
            }
          }
        }
      } catch (error) {
        console.log('Activity monitor polling error:', error);
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
        <div className="flex items-center justify-between bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 mb-2">
          <div className="flex items-center gap-2 text-sm text-blue-400">
            <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></div>
            <span>Research Monitor ({activityLog.length} activities)</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMinimized(false)}
            className="h-6 text-blue-400 hover:bg-gray-800"
          >
            Expand
          </Button>
        </div>
      ) : (
        // Expanded state - full monitor with activity log
        <div className="bg-gray-900 border border-gray-700 rounded-lg mb-2 shadow-xl max-w-4xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-700 bg-gray-800 px-4 py-2 rounded-t-lg">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-sm font-medium text-gray-100">Research Monitor</span>
            </div>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(true)}
                className="h-6 px-2 hover:bg-gray-700 text-xs text-gray-300"
              >
                Minimize
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-6 px-2 hover:bg-gray-700 text-xs text-gray-300"
              >
                Close
              </Button>
            </div>
          </div>

          {/* Content */}
          <div className="flex flex-col h-64">
            {/* Status Header */}
            <div className="px-4 py-2 border-b border-gray-700 bg-gray-800">
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Workflow: {workflowId.slice(-8)}...</span>
                {activityStatus && (
                  <div className="flex gap-4 text-xs text-gray-300">
                    <span>Iter: {activityStatus.iteration + 1}</span>
                    <span>Papers: {activityStatus.papers_discovered}</span>
                    <span>Analysis: {activityStatus.analysis_count}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Scrollable Activity Log */}
            <div 
              ref={scrollRef}
              className="flex-1 overflow-y-auto p-3 space-y-2 max-h-48 bg-gray-900"
              style={{
                scrollbarWidth: 'thin',
                scrollbarColor: '#4B5563 #1F2937'
              }}
            >
              {activityLog.length > 0 ? (
                activityLog.map((entry, index) => (
                  <div key={index} className="flex gap-2 text-xs">
                    <span className="text-gray-500 font-mono shrink-0 w-16">
                      {entry.timestamp}
                    </span>
                    <div className="flex-1">
                      <div className="text-gray-200 leading-relaxed">
                        {entry.message}
                      </div>
                      {entry.details && (
                        <div className="text-gray-400 text-xs mt-1">
                          Iteration {entry.details.iteration + 1} • {entry.details.papers} papers • {entry.details.analyses} analyses
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                  {activityStatus ? (
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 border-2 border-blue-600 border-t-blue-400 rounded-full animate-spin"></div>
                      <span>Monitoring workflow activities...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 border-2 border-gray-600 border-t-gray-400 rounded-full animate-spin"></div>
                      <span>Connecting to workflow...</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-3 py-2 border-t border-gray-700 bg-gray-800 flex justify-between items-center text-xs text-gray-400">
              <span>{activityLog.length} activities logged</span>
              {!isCompleted && (
                <div className="flex items-center gap-1">
                  <div className="h-1 w-1 rounded-full bg-green-400 animate-pulse"></div>
                  <span>Live updates</span>
                </div>
              )}
              {isCompleted && (
                <span className="text-green-400 font-medium">✓ Completed</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}