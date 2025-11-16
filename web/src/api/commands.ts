import apiClient from '../utils/fetcher';
import type { CommandResponse } from '../utils/types';

export const commandsApi = {
  execute: async (serverId: string, command: string): Promise<CommandResponse> => {
    const response = await apiClient.post<CommandResponse>(`/api/v1/commands/${serverId}`, {
      command,
    });
    return response.data;
  },
};

