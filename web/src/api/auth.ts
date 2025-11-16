import apiClient from '../utils/fetcher';
import type { AuthResponse, User } from '../utils/types';

export const authApi = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (email: string, password: string, passwordConfirm: string, username: string, fullName?: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/register', {
      email,
      password,
      password_confirm: passwordConfirm,
      username,
      full_name: fullName,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/v1/auth/logout');
  },

  updateProfile: async (data: { full_name?: string }): Promise<User> => {
    const response = await apiClient.put<User>('/api/v1/auth/me', data);
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string, newPasswordConfirm: string): Promise<void> => {
    await apiClient.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    });
  },
};

