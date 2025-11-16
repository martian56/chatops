import apiClient from '../utils/fetcher';
import type { Server } from '../utils/types';

export interface CreateServerDto {
  name: string;
  host?: string;
  port?: number;
  metadata?: Record<string, unknown>;
}

export interface UpdateServerDto {
  name?: string;
  host?: string;
  port?: number;
  metadata?: Record<string, unknown>;
}

export const serversApi = {
  getAll: async (): Promise<Server[]> => {
    const response = await apiClient.get<Server[]>('/api/v1/servers');
    return response.data;
  },

  getById: async (id: string): Promise<Server> => {
    const response = await apiClient.get<Server>(`/api/v1/servers/${id}`);
    return response.data;
  },

  create: async (data: CreateServerDto): Promise<Server> => {
    const response = await apiClient.post<Server>('/api/v1/servers', data);
    return response.data;
  },

  update: async (id: string, data: UpdateServerDto): Promise<Server> => {
    const response = await apiClient.put<Server>(`/api/v1/servers/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/servers/${id}`);
  },

  checkHealth: async (id: string): Promise<{ status: string }> => {
    const response = await apiClient.post<{ status: string }>(`/api/v1/servers/${id}/health`);
    return response.data;
  },
};

