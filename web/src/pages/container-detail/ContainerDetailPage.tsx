import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import { dockerApi, serversApi } from '../../api';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { format } from 'date-fns';
import { ContainerDetailPageSkeleton } from '../../components/skeletons/ContainerDetailPageSkeleton';

export const ContainerDetailPage = () => {
  const { serverId, containerId } = useParams<{ serverId: string; containerId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);
  
  // Get tab from URL or default to 'overview'
  const activeTab = searchParams.get('tab') || 'overview';
  
  // Valid tab values
  const validTabs = ['overview', 'logs'];
  const currentTab = validTabs.includes(activeTab) ? activeTab : 'overview';
  
  const handleTabChange = (value: string) => {
    setSearchParams({ tab: value });
  };

  const { isLoading: serverLoading } = useQuery({
    queryKey: ['server', serverId],
    queryFn: () => serversApi.getById(serverId!),
    enabled: !!serverId,
  });

  const { data: containers = [] } = useQuery({
    queryKey: ['containers', serverId],
    queryFn: () => dockerApi.getContainers(serverId!),
    enabled: !!serverId,
    refetchInterval: 5000,
  });

  const container = containers.find((c) => c.id === containerId || c.id.startsWith(containerId || ''));

  const loadLogs = async () => {
    if (!serverId || !containerId) return;
    setIsLoadingLogs(true);
    try {
      const containerLogs = await dockerApi.getContainerLogs(serverId, containerId, 500);
      setLogs(containerLogs);
    } catch (error) {
      console.error('Failed to load logs:', error);
    } finally {
      setIsLoadingLogs(false);
    }
  };

  // Load logs on mount and when container changes
  useEffect(() => {
    if (container?.state === 'running') {
      loadLogs();
    }
  }, [container?.id, container?.state]);

  if (serverLoading) {
    return <ContainerDetailPageSkeleton />;
  }

  if (!container) {
    return (
      <div>
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/servers/${serverId}`)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Container Not Found</h1>
          </div>
        </div>
      </div>
    );
  }

  const getStateColor = (state: string) => {
    switch (state) {
      case 'running':
        return 'text-green-500';
      case 'stopped':
        return 'text-red-500';
      case 'paused':
        return 'text-yellow-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" onClick={() => navigate(`/servers/${serverId}`)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{container.name}</h1>
          <p className="text-muted-foreground">{container.image}</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className={`text-sm font-medium ${getStateColor(container.state)}`}>
            {container.state}
          </span>
        </div>
      </div>

      <Tabs value={currentTab} onValueChange={handleTabChange} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Container Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Container ID:</span>
                  <span className="font-mono text-sm">{container.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Image:</span>
                  <span>{container.image}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className={getStateColor(container.state)}>{container.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">State:</span>
                  <span className={getStateColor(container.state)}>{container.state}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created:</span>
                  <span>{format(new Date(container.created), 'PPP p')}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Ports</CardTitle>
              </CardHeader>
              <CardContent>
                {container.ports.length > 0 ? (
                  <div className="space-y-2">
                    {container.ports.map((port, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-muted-foreground">
                          {port.public_port ? `${port.public_port}:` : ''}
                          {port.private_port}/{port.type}
                        </span>
                        {port.public_port && (
                          <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                            {port.public_port}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No ports exposed</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Container Logs</CardTitle>
                <CardDescription>Real-time logs from the container</CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={loadLogs}
                disabled={isLoadingLogs || container.state !== 'running'}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingLogs ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </CardHeader>
            <CardContent>
              {container.state !== 'running' ? (
                <div className="text-center text-muted-foreground py-12">
                  Container is not running. Logs are only available for running containers.
                </div>
              ) : logs.length === 0 ? (
                <div className="text-center text-muted-foreground py-12">
                  {isLoadingLogs ? 'Loading logs...' : 'No logs available. Click Refresh to load logs.'}
                </div>
              ) : (
                <div className="bg-black rounded-lg p-4 font-mono text-sm max-h-[600px] overflow-y-auto custom-scrollbar">
                  {logs.map((log, idx) => (
                    <div key={idx} className="text-green-400 mb-1">
                      {log}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

