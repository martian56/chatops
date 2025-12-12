// React application root component
// CI/CD: Changes here trigger frontend build and deployment workflow
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { useAuthStore } from './store/auth';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LoginPage } from './pages/login/LoginPage';
import { RegisterPage } from './pages/register/RegisterPage';
import { ServersPage } from './pages/servers/ServersPage';
import { ServerDetailPage } from './pages/server-detail/ServerDetailPage';
import { ContainerDetailPage } from './pages/container-detail/ContainerDetailPage';
import { AlertsPage } from './pages/alerts/AlertsPage';
import { SettingsPage } from './pages/settings/SettingsPage';
import { useEffect } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

function App() {
  const { initialize } = useAuthStore();

  useEffect(() => {
    // Initialize auth on app start
    initialize();
    // Initialize theme from localStorage or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/servers"
            element={
              <ProtectedRoute>
                <ServersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/servers/:id"
            element={
              <ProtectedRoute>
                <ServerDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/servers/:serverId/containers/:containerId"
            element={
              <ProtectedRoute>
                <ContainerDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/alerts"
            element={
              <ProtectedRoute>
                <AlertsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/servers" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
