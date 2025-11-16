import apiClient from '../utils/fetcher';
import type { DockerContainer } from '../utils/types';

export const dockerApi = {
  getContainers: async (serverId: string): Promise<DockerContainer[]> => {
    const response = await apiClient.get<DockerContainer[]>(`/api/v1/docker/${serverId}/containers`);
    return response.data;
  },

  startContainer: async (serverId: string, containerId: string): Promise<void> => {
    await apiClient.post(`/api/v1/docker/${serverId}/containers/${containerId}/start`);
  },

  stopContainer: async (serverId: string, containerId: string): Promise<void> => {
    await apiClient.post(`/api/v1/docker/${serverId}/containers/${containerId}/stop`);
  },

  restartContainer: async (serverId: string, containerId: string): Promise<void> => {
    await apiClient.post(`/api/v1/docker/${serverId}/containers/${containerId}/restart`);
  },

  getContainerLogs: async (
    serverId: string,
    containerId: string,
    tail?: number
  ): Promise<string[]> => {
    const params = new URLSearchParams();
    if (tail) params.append('tail', tail.toString());

    const response = await apiClient.get<string[]>(
      `/api/v1/docker/${serverId}/containers/${containerId}/logs?${params.toString()}`
    );
    return response.data;
  },
};

