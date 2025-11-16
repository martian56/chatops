import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../store/auth';
import { WS_BASE_URL } from '../utils/constants';
import type { ServerMetrics, LogEntry } from '../utils/types';

interface UseMetricsWSOptions {
  serverId: string;
  enabled?: boolean;
}

export const useMetricsWS = ({ serverId, enabled = true }: UseMetricsWSOptions) => {
  const [metrics, setMetrics] = useState<ServerMetrics | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<ServerMetrics[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    if (!enabled || !serverId || !token) return;

    // Convert http/https to ws/wss
    let wsUrl = WS_BASE_URL;
    if (wsUrl.startsWith('http://')) {
      wsUrl = wsUrl.replace('http://', 'ws://');
    } else if (wsUrl.startsWith('https://')) {
      wsUrl = wsUrl.replace('https://', 'wss://');
    } else if (!wsUrl.startsWith('ws://') && !wsUrl.startsWith('wss://')) {
      wsUrl = `ws://${wsUrl}`;
    }
    wsUrl = `${wsUrl}/api/v1/ws/metrics/${serverId}`;
    console.log('Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send authentication message as first message
      ws.send(JSON.stringify({ type: 'auth', token }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle auth success
        if (message.type === 'auth_success') {
          setIsConnected(true);
          return;
        }
        
        // Handle metrics
        if (message.type === 'metrics' && message.data) {
          console.log('Setting metrics:', message.data);
          const newMetrics = message.data;
          setMetrics(newMetrics);
          
          // Add to history (keep last 100 points for chart)
          setMetricsHistory((prev) => {
            const updated = [...prev, newMetrics];
            return updated.slice(-100); // Keep last 100 data points
          });
        } else if (message.type === 'pong') {
          // Heartbeat response
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    // Send periodic ping to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Every 30 seconds

    return () => {
      clearInterval(pingInterval);
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
      wsRef.current = null;
    };
  }, [serverId, enabled, token]);

  return { metrics, metricsHistory, isConnected };
};

interface UseLogsWSOptions {
  serverId: string;
  enabled?: boolean;
  maxLines?: number;
}

export const useLogsWS = ({ serverId, enabled = true, maxLines = 1000 }: UseLogsWSOptions) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const { token } = useAuthStore();

  const addLog = useCallback((log: LogEntry) => {
    setLogs((prev) => {
      const newLogs = [log, ...prev];
      return newLogs.slice(0, maxLines);
    });
  }, [maxLines]);

  useEffect(() => {
    if (!enabled || !serverId || !token) return;

    // Convert http/https to ws/wss
    let wsUrl = WS_BASE_URL;
    if (wsUrl.startsWith('http://')) {
      wsUrl = wsUrl.replace('http://', 'ws://');
    } else if (wsUrl.startsWith('https://')) {
      wsUrl = wsUrl.replace('https://', 'wss://');
    } else if (!wsUrl.startsWith('ws://') && !wsUrl.startsWith('wss://')) {
      wsUrl = `ws://${wsUrl}`;
    }
    wsUrl = `${wsUrl}/api/v1/ws/logs/${serverId}`;
    console.log('Connecting to WebSocket (logs):', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send authentication message as first message
      ws.send(JSON.stringify({ type: 'auth', token }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle auth success
        if (message.type === 'auth_success') {
          console.log('Logs WebSocket connected');
          setIsConnected(true);
          return;
        }
        
        // Handle logs
        if (message.type === 'log' && message.data) {
          addLog(message.data);
        } else if (message.type === 'pong') {
          // Heartbeat response
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    // Send periodic ping to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Every 30 seconds

    return () => {
      clearInterval(pingInterval);
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
      wsRef.current = null;
    };
  }, [serverId, enabled, token, addLog]);

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  return { logs, isConnected, clearLogs };
};
