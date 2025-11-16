import { useNavigate } from 'react-router-dom';
import { Play, Square, RotateCw, ExternalLink, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import type { DockerContainer } from '../../utils/types';

interface DockerContainersListProps {
  containers: DockerContainer[];
  serverId: string;
  onAction: (action: 'start' | 'stop' | 'restart', containerId: string) => void;
  loadingState?: { containerId: string; action: 'start' | 'stop' | 'restart' } | null;
}

export const DockerContainersList = ({ containers, serverId, onAction, loadingState }: DockerContainersListProps) => {
  const navigate = useNavigate();
  
  const isActionLoading = (containerId: string, action: 'start' | 'stop' | 'restart') => {
    return loadingState?.containerId === containerId && loadingState?.action === action;
  };

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

  const handleContainerClick = (containerId: string) => {
    navigate(`/servers/${serverId}/containers/${containerId}`);
  };

  if (containers.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          No containers found
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {containers.map((container) => (
        <Card 
          key={container.id}
          className="cursor-pointer hover:bg-accent/50 transition-colors"
          onClick={() => handleContainerClick(container.id)}
        >
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {container.name}
                    <ExternalLink className="h-4 w-4 text-muted-foreground" />
                  </CardTitle>
                  <CardDescription>{container.image}</CardDescription>
                </div>
              </div>
              <span className={`font-medium ${getStateColor(container.state)}`}>
                {container.state}
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>ID: {container.id.substring(0, 12)}</span>
                <span>•</span>
                <span>Created: {new Date(container.created).toLocaleString()}</span>
              </div>
              {container.ports.length > 0 && (
                <div className="text-sm">
                  <span className="font-medium">Ports: </span>
                  {container.ports.map((port, idx) => (
                    <span key={idx}>
                      {port.public_port ? `${port.public_port}:` : ''}
                      {port.private_port}/{port.type}
                      {idx < container.ports.length - 1 && ', '}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex gap-2">
                {container.state !== 'running' && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAction('start', container.id);
                    }}
                    disabled={isActionLoading(container.id, 'start')}
                  >
                    {isActionLoading(container.id, 'start') ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4 mr-2" />
                    )}
                    Start
                  </Button>
                )}
                {container.state === 'running' && (
                  <>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAction('stop', container.id);
                      }}
                      disabled={isActionLoading(container.id, 'stop')}
                    >
                      {isActionLoading(container.id, 'stop') ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Square className="h-4 w-4 mr-2" />
                      )}
                      Stop
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAction('restart', container.id);
                      }}
                      disabled={isActionLoading(container.id, 'restart')}
                    >
                      {isActionLoading(container.id, 'restart') ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <RotateCw className="h-4 w-4 mr-2" />
                      )}
                      Restart
                    </Button>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

