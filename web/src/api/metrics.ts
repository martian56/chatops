import apiClient from '../utils/fetcher';
import type { ServerMetrics } from '../utils/types';

export const metricsApi = {
  getLatest: async (serverId: string): Promise<ServerMetrics> => {
    const response = await apiClient.get<ServerMetrics>(`/api/v1/metrics/${serverId}/latest`);
    return response.data;
  },

  getHistory: async (
    serverId: string,
    startTime?: string,
    endTime?: string,
    limit?: number
  ): Promise<ServerMetrics[]> => {
    const params = new URLSearchParams();
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    if (limit) params.append('limit', limit.toString());

    const response = await apiClient.get<ServerMetrics[]>(
      `/api/v1/metrics/${serverId}/history?${params.toString()}`
    );
    return response.data;
  },
};

