import { useEffect, useRef, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Trash2, AlertCircle, Activity } from 'lucide-react';
import type { LogEntry, Alert } from '../../utils/types';

interface LogsViewerProps {
  logs: LogEntry[];
  historicalLogs?: LogEntry[];
  onClear: () => void;
  serverAlerts?: Alert[];
  isConnected?: boolean;
  metricsConnected?: boolean;
}

export const LogsViewer = ({ logs, historicalLogs = [], onClear, serverAlerts = [], isConnected = false, metricsConnected = false }: LogsViewerProps) => {
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Convert alerts to log entries for display
  const alertLogs = useMemo(() => {
    return serverAlerts.map((alert): LogEntry => ({
      timestamp: alert.created_at,
      level: alert.severity === 'critical' ? 'error' : alert.severity === 'warning' ? 'warning' : 'info',
      message: alert.message,
      source: 'alert',
    }));
  }, [serverAlerts]);

  // System status logs - only show connection issues, not connected state
  // Connected state is misleading because it's the frontend WS connection, not agent connection
  const systemLogs = useMemo((): LogEntry[] => {
    const systemEntries: LogEntry[] = [];
    
    const now = new Date().toISOString();
    
    // Only show warnings when disconnected, not info when connected
    // This prevents showing fake "connected" messages when no agent is running
    if (!metricsConnected && logs.length === 0 && alertLogs.length === 0) {
      systemEntries.push({
        timestamp: now,
        level: 'warning',
        message: 'No agent connected - waiting for agent to start...',
        source: 'system',
      });
    }

    return systemEntries;
  }, [metricsConnected, logs.length, alertLogs.length]);

  // Combine all logs: real-time logs, historical logs, alerts, then system status
  const allLogs = useMemo(() => {
    return [...logs, ...historicalLogs, ...alertLogs, ...systemLogs].sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [logs, historicalLogs, alertLogs, systemLogs]);

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-500';
      case 'warning':
        return 'text-yellow-500';
      case 'info':
        return 'text-blue-500';
      case 'debug':
        return 'text-gray-500';
      default:
        return 'text-foreground';
    }
  };

  const getSourceIcon = (source?: string) => {
    switch (source) {
      case 'alert':
        return <AlertCircle className="h-3 w-3 inline mr-1" />;
      case 'system':
        return <Activity className="h-3 w-3 inline mr-1" />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Logs & Activity</CardTitle>
            <CardDescription>
              Real-time logs, alerts, and system activity ({allLogs.length} entries)
              {logs.length === 0 && !isConnected && ' - Waiting for agent logs...'}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={onClear} disabled={logs.length === 0}>
            <Trash2 className="h-4 w-4 mr-2" />
            Clear
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-black rounded p-4 font-mono text-sm h-96 overflow-y-auto custom-scrollbar">
          {allLogs.length === 0 ? (
            <div className="text-muted-foreground text-center py-8">
              <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No logs available yet.</p>
              <p className="text-xs mt-2">Logs will appear here when the agent starts sending them.</p>
            </div>
          ) : (
            allLogs.map((log, idx) => (
              <div key={idx} className="mb-1 hover:bg-gray-900/50 px-2 py-1 rounded">
                <span className="text-muted-foreground">
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </span>
                <span className={`ml-2 ${getLogLevelColor(log.level)}`}>
                  [{log.level.toUpperCase()}]
                </span>
                {log.source && (
                  <span className="ml-2 text-muted-foreground inline-flex items-center">
                    {getSourceIcon(log.source)}
                    [{log.source}]
                  </span>
                )}
                <span className="ml-2">{log.message}</span>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </CardContent>
    </Card>
  );
};

