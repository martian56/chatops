import apiClient from '../utils/fetcher';
import type { Alert, AlertThreshold } from '../utils/types';

export interface CreateAlertThresholdDto {
  server_id: string;
  metric_type: 'cpu' | 'memory' | 'disk' | 'network';
  threshold_value: number;
  comparison: 'gt' | 'lt';
  enabled: boolean;
}

export const alertsApi = {
  getAll: async (resolved?: boolean): Promise<Alert[]> => {
    const params = new URLSearchParams();
    if (resolved !== undefined) params.append('resolved', resolved.toString());

    const response = await apiClient.get<Alert[]>(`/api/v1/alerts?${params.toString()}`);
    return response.data;
  },

  getById: async (id: string): Promise<Alert> => {
    const response = await apiClient.get<Alert>(`/api/v1/alerts/${id}`);
    return response.data;
  },

  resolve: async (id: string): Promise<Alert> => {
    const response = await apiClient.post<Alert>(`/api/v1/alerts/${id}/resolve`);
    return response.data;
  },

  getThresholds: async (serverId?: string): Promise<AlertThreshold[]> => {
    let url = '/api/v1/alerts/thresholds';
    if (serverId) {
      url += `?server_id=${serverId}`;
    }

    const response = await apiClient.get<AlertThreshold[]>(url);
    return response.data;
  },

  createThreshold: async (data: CreateAlertThresholdDto): Promise<AlertThreshold> => {
    const response = await apiClient.post<AlertThreshold>('/api/v1/alerts/thresholds', data);
    return response.data;
  },

  updateThreshold: async (id: string, data: Partial<CreateAlertThresholdDto>): Promise<AlertThreshold> => {
    const response = await apiClient.put<AlertThreshold>(`/api/v1/alerts/thresholds/${id}`, data);
    return response.data;
  },

  deleteThreshold: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/alerts/thresholds/${id}`);
  },
};

