import apiClient from '../utils/fetcher';

export interface LogEntry {
  id: string;
  server_id: string;
  timestamp: string;
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  source: 'system' | 'agent' | 'application' | 'alert';
  message: string;
  component?: string;
  extra_data?: string;
}

export const logsApi = {
  getServerLogs: async (
    serverId: string,
    params?: {
      limit?: number;
      level?: string;
      source?: string;
      component?: string;
    }
  ): Promise<LogEntry[]> => {
    const response = await apiClient.get<LogEntry[]>(
      `/api/v1/logs/${serverId}`,
      { params }
    );
    return response.data;
  },
};
