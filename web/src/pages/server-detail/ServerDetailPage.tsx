import { useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { ArrowLeft } from 'lucide-react';
import { serversApi, dockerApi } from '../../api';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { useMetricsWS, useLogsWS } from '../../hooks/useWS';
import { MetricsChart } from '../../components/charts/MetricsChart';
import { DockerContainersList } from '../../components/charts/DockerContainersList';
import { ProcessesList } from '../../components/charts/ProcessesList';
import { LogsViewer } from '../../components/charts/LogsViewer';
import { APIKeyManager } from '../../components/forms/APIKeyManager';
import { Terminal } from '../../components/terminal/Terminal';
import { ServerDetailPageSkeleton } from '../../components/skeletons/ServerDetailPageSkeleton';
import { MetricsChartSkeleton } from '../../components/skeletons/MetricsChartSkeleton';
import { DockerContainersListSkeleton } from '../../components/skeletons/DockerContainersListSkeleton';
import { ProcessesListSkeleton } from '../../components/skeletons/ProcessesListSkeleton';
import { alertsApi } from '../../api/alerts';
import { logsApi } from '../../api/logs';

export const ServerDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Get tab from URL or default to 'metrics'
  const activeTab = searchParams.get('tab') || 'metrics';
  
  // Valid tab values
  const validTabs = ['metrics', 'containers', 'processes', 'logs', 'terminal', 'api-keys'];
  const currentTab = validTabs.includes(activeTab) ? activeTab : 'metrics';
  
  const handleTabChange = (value: string) => {
    setSearchParams({ tab: value });
  };

  const { data: server, isLoading } = useQuery({
    queryKey: ['server', id],
    queryFn: () => serversApi.getById(id!),
    enabled: !!id,
  });

  const { metrics, metricsHistory, isConnected: metricsConnected } = useMetricsWS({
    serverId: id!,
    enabled: !!id,
  });

  // Use containers from metrics if available, otherwise fallback to API
  const containersFromMetrics = metrics?.containers || [];
  const { data: containersFromApi = [], isLoading: isLoadingContainers } = useQuery({
    queryKey: ['containers', id],
    queryFn: () => dockerApi.getContainers(id!),
    enabled: !!id && containersFromMetrics.length === 0,
    refetchInterval: 5000,
  });
  const containers = containersFromMetrics.length > 0 ? containersFromMetrics : containersFromApi;
  const isLoadingContainersData = isLoadingContainers && containersFromMetrics.length === 0;

  const { logs, clearLogs, isConnected: logsConnected } = useLogsWS({
    serverId: id!,
    enabled: !!id,
  });

  // Get recent alerts for this server
  const { data: recentAlerts = [] } = useQuery({
    queryKey: ['server-alerts', id],
    queryFn: () => alertsApi.getAll(false),
    enabled: !!id,
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // Filter alerts for this server
  const serverAlerts = recentAlerts.filter((alert) => alert.server_id === id).slice(0, 20);

  // Fetch historical logs from database
  const { data: historicalLogs = [] } = useQuery({
    queryKey: ['logs', 'server', id],
    queryFn: () => logsApi.getServerLogs(id!, { limit: 100 }),
    enabled: !!id,
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  const [loadingState, setLoadingState] = useState<{ containerId: string; action: 'start' | 'stop' | 'restart' } | null>(null);

  const containerActionMutation = useMutation({
    mutationFn: ({ action, containerId }: { action: 'start' | 'stop' | 'restart'; containerId: string }) => {
      setLoadingState({ containerId, action });
      switch (action) {
        case 'start':
          return dockerApi.startContainer(id!, containerId);
        case 'stop':
          return dockerApi.stopContainer(id!, containerId);
        case 'restart':
          return dockerApi.restartContainer(id!, containerId);
      }
    },
    onSettled: () => {
      setLoadingState(null);
    },
  });

  if (isLoading) {
    return <ServerDetailPageSkeleton />;
  }

  if (!server) {
    return <div>Server not found</div>;
  }

  return (
    <div>
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={() => navigate('/servers')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{server.name}</h1>
            {server.host && server.port && (
              <p className="text-muted-foreground">
                {server.host}:{server.port}
              </p>
            )}
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className={`text-sm ${metricsConnected ? 'text-green-500' : 'text-red-500'}`}>
              {metricsConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        <Tabs value={currentTab} onValueChange={handleTabChange} className="space-y-4">
          <TabsList>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="containers">Docker ({containers.length})</TabsTrigger>
            <TabsTrigger value="processes">Processes {metrics?.processes ? `(${metrics.processes.length})` : ''}</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="terminal">Terminal</TabsTrigger>
            <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          </TabsList>

          <TabsContent value="metrics" className="space-y-4">
            {metrics ? (
              <MetricsChart metrics={metrics} metricsHistory={metricsHistory} />
            ) : (
              <MetricsChartSkeleton />
            )}
          </TabsContent>

          <TabsContent value="containers" className="space-y-4">
            {isLoadingContainersData ? (
              <DockerContainersListSkeleton />
            ) : (
              <DockerContainersList
                containers={containers}
                serverId={id!}
                onAction={(action, containerId) =>
                  containerActionMutation.mutate({ action, containerId })
                }
                loadingState={loadingState}
              />
            )}
          </TabsContent>

          <TabsContent value="processes" className="space-y-4">
            {metrics?.processes ? (
              <ProcessesList processes={metrics.processes} />
            ) : (
              <ProcessesListSkeleton />
            )}
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <LogsViewer 
              logs={logs}
              historicalLogs={historicalLogs}
              onClear={clearLogs}
              serverAlerts={serverAlerts}
              isConnected={logsConnected}
              metricsConnected={metricsConnected}
            />
          </TabsContent>

          <TabsContent value="terminal" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Command Terminal</CardTitle>
                <CardDescription>Execute commands on the server</CardDescription>
              </CardHeader>
              <CardContent>
                <Terminal serverId={id!} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api-keys" className="space-y-4">
            <APIKeyManager serverId={id!} />
          </TabsContent>
        </Tabs>
    </div>
  );
};

