import apiClient from '../utils/fetcher';

export interface APIKey {
  id: string;
  server_id: string;
  name?: string;
  is_active: boolean;
  last_used?: string;
  created_at: string;
  expires_at?: string;
}

export interface APIKeyResponse {
  id: string;
  server_id: string;
  key: string; // Only shown on creation
  name?: string;
  is_active: boolean;
  last_used?: string;
  created_at: string;
  expires_at?: string;
}

export interface CreateAPIKeyDto {
  server_id: string;
  name?: string;
  expires_at?: string;
}

export const apiKeysApi = {
  create: async (data: CreateAPIKeyDto): Promise<APIKeyResponse> => {
    const response = await apiClient.post<APIKeyResponse>('/api/v1/api-keys', data);
    return response.data;
  },

  getByServer: async (serverId: string): Promise<APIKey[]> => {
    const response = await apiClient.get<APIKey[]>(`/api/v1/api-keys/server/${serverId}`);
    return response.data;
  },

  deactivate: async (keyId: string): Promise<APIKey> => {
    const response = await apiClient.post<APIKey>(`/api/v1/api-keys/${keyId}/deactivate`);
    return response.data;
  },

  delete: async (keyId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/api-keys/${keyId}`);
  },
};

