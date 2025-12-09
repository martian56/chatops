import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/auth';
import { getAuthErrorMessage, getRegisterErrorMessage } from '../utils/errorMessages';

export const useAuth = () => {
  const { user, isAuthenticated, setAuth, clearAuth } = useAuthStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      navigate('/servers');
    },
  });

  const registerMutation = useMutation({
    mutationFn: ({
      email,
      password,
      passwordConfirm,
      username,
      fullName,
    }: {
      email: string;
      password: string;
      passwordConfirm: string;
      username: string;
      fullName?: string;
    }) => authApi.register(email, password, passwordConfirm, username, fullName),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      navigate('/servers');
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      clearAuth();
      queryClient.clear();
      navigate('/login');
    },
  });

  const { data: currentUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
  });

  // Get user-friendly error messages
  const loginError = loginMutation.error ? getAuthErrorMessage(loginMutation.error) : null;
  const registerError = registerMutation.error ? getRegisterErrorMessage(registerMutation.error) : null;

  return {
    user: user || currentUser,
    isAuthenticated,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: () => logoutMutation.mutate(),
    isLoading: loginMutation.isPending || registerMutation.isPending,
    error: loginError || registerError,
    rawError: loginMutation.error || registerMutation.error,
  };
};

