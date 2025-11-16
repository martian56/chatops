import { create } from 'zustand';
import type { User } from '../utils/types';
import { setAuthToken, getAuthToken } from '../utils/fetcher';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isInitializing: true,
  
  setAuth: (user: User, accessToken: string, refreshToken: string) => {
    setAuthToken(accessToken, refreshToken);
    set({ user, token: accessToken, isAuthenticated: true, isInitializing: false });
  },
  
  clearAuth: () => {
    setAuthToken(null, null);
    set({ user: null, token: null, isAuthenticated: false, isInitializing: false });
  },
  
  initialize: async () => {
    set({ isInitializing: true });
    const token = getAuthToken();
    if (token) {
      // Try to fetch user info to verify token is still valid
      try {
        const { authApi } = await import('../api/auth');
        const user = await authApi.getCurrentUser();
        set({ user, token, isAuthenticated: true, isInitializing: false });
      } catch (error) {
        // Token is invalid, clear it
        setAuthToken(null, null);
        set({ user: null, token: null, isAuthenticated: false, isInitializing: false });
      }
    } else {
      set({ isInitializing: false });
    }
  },
}));

