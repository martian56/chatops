import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertCircle, CheckCircle, XCircle, Plus, Edit, Trash2, Settings } from 'lucide-react';
import { alertsApi, type CreateAlertThresholdDto } from '../../api/alerts';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { serversApi } from '../../api/servers';
import { AlertsPageSkeleton } from '../../components/skeletons/AlertsPageSkeleton';
import { toast } from 'sonner';
import type { AlertThreshold } from '../../utils/types';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../../components/ui/alert-dialog';

export const AlertsPage = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingThreshold, setEditingThreshold] = useState<AlertThreshold | null>(null);
  const [deletingThresholdId, setDeletingThresholdId] = useState<string | null>(null);
  const [showResolved, setShowResolved] = useState(false);
  const [newThreshold, setNewThreshold] = useState<CreateAlertThresholdDto>({
    server_id: '',
    metric_type: 'cpu',
    threshold_value: 80,
    comparison: 'gt',
    enabled: true,
  });
  const [editThreshold, setEditThreshold] = useState<Partial<CreateAlertThresholdDto>>({
    metric_type: 'cpu',
    threshold_value: 80,
    comparison: 'gt',
    enabled: true,
  });
  const queryClient = useQueryClient();

  const { data: alerts = [], isLoading: isLoadingAlerts } = useQuery({
    queryKey: ['alerts', showResolved],
    queryFn: () => alertsApi.getAll(showResolved ? undefined : false),
    refetchInterval: 5000, // Refetch every 5 seconds to get new alerts
  });

  const { data: thresholds = [], isLoading: isLoadingThresholds } = useQuery({
    queryKey: ['alertThresholds'],
    queryFn: () => alertsApi.getThresholds(),
  });

  const { data: servers = [] } = useQuery({
    queryKey: ['servers'],
    queryFn: serversApi.getAll,
  });

  const isLoading = isLoadingAlerts || isLoadingThresholds;

  const resolveMutation = useMutation({
    mutationFn: alertsApi.resolve,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert resolved');
    },
    onError: (error: any) => {
      toast.error(`Failed to resolve alert: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const createThresholdMutation = useMutation({
    mutationFn: alertsApi.createThreshold,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertThresholds'] });
      setIsDialogOpen(false);
      setNewThreshold({
        server_id: '',
        metric_type: 'cpu',
        threshold_value: 80,
        comparison: 'gt',
        enabled: true,
      });
      toast.success('Alert threshold created');
    },
    onError: (error: any) => {
      toast.error(`Failed to create threshold: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const updateThresholdMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateAlertThresholdDto> }) =>
      alertsApi.updateThreshold(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertThresholds'] });
      setIsEditDialogOpen(false);
      setEditingThreshold(null);
      toast.success('Alert threshold updated');
    },
    onError: (error: any) => {
      toast.error(`Failed to update threshold: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const deleteThresholdMutation = useMutation({
    mutationFn: alertsApi.deleteThreshold,
    onSuccess: (_, thresholdId) => {
      queryClient.setQueryData<AlertThreshold[]>(['alertThresholds'], (old) => {
        return old?.filter((t) => t.id !== thresholdId) || [];
      });
      queryClient.invalidateQueries({ queryKey: ['alertThresholds'] });
      setIsDeleteDialogOpen(false);
      setDeletingThresholdId(null);
      toast.success('Alert threshold deleted');
    },
    onError: (error: any) => {
      queryClient.invalidateQueries({ queryKey: ['alertThresholds'] });
      toast.error(`Failed to delete threshold: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const toggleThresholdMutation = useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      alertsApi.updateThreshold(id, { enabled }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertThresholds'] });
      toast.success('Threshold updated');
    },
    onError: (error: any) => {
      toast.error(`Failed to update threshold: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-blue-500" />;
    }
  };

  const handleCreateThreshold = (e: React.FormEvent) => {
    e.preventDefault();
    createThresholdMutation.mutate(newThreshold);
  };

  const handleEditThreshold = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingThreshold) {
      updateThresholdMutation.mutate({ id: editingThreshold.id, data: editThreshold });
    }
  };

  const handleDeleteThreshold = () => {
    if (deletingThresholdId) {
      deleteThresholdMutation.mutate(deletingThresholdId);
    }
  };

  const handleEditClick = (threshold: AlertThreshold) => {
    setEditingThreshold(threshold);
    setEditThreshold({
      metric_type: threshold.metric_type,
      threshold_value: threshold.threshold_value,
      comparison: threshold.comparison,
      enabled: threshold.enabled,
    });
    setIsEditDialogOpen(true);
  };

  const handleDeleteClick = (thresholdId: string) => {
    setDeletingThresholdId(thresholdId);
    setIsDeleteDialogOpen(true);
  };

  const handleToggleThreshold = (threshold: AlertThreshold) => {
    toggleThresholdMutation.mutate({ id: threshold.id, enabled: !threshold.enabled });
  };

  if (isLoading) {
    return <AlertsPageSkeleton />;
  }

  return (
    <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Alerts</h1>
            <p className="text-muted-foreground">Monitor and manage system alerts</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={showResolved ? 'default' : 'outline'}
              onClick={() => setShowResolved(!showResolved)}
            >
              {showResolved ? 'Hide Resolved' : 'Show Resolved'}
            </Button>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Active Alerts</h2>
            {alerts.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  No alerts found
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {alerts.map((alert) => (
                  <Card key={alert.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getSeverityIcon(alert.severity)}
                          <CardTitle className="text-lg">{alert.type}</CardTitle>
                        </div>
                        {!alert.resolved && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => resolveMutation.mutate(alert.id)}
                            disabled={resolveMutation.isPending}
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Resolve
                          </Button>
                        )}
                      </div>
                      <CardDescription>{alert.server_name || alert.server_id}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="mb-2">{alert.message}</p>
                      {alert.threshold && alert.current_value !== undefined && (
                        <p className="text-sm text-muted-foreground">
                          Threshold: {alert.threshold} | Current: {alert.current_value}
                        </p>
                      )}
                      <p className="text-xs text-muted-foreground mt-2">
                        {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Alert Thresholds</h2>
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Threshold
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <form onSubmit={handleCreateThreshold}>
                    <DialogHeader>
                      <DialogTitle>Create Alert Threshold</DialogTitle>
                      <DialogDescription>Set up a new alert threshold for monitoring</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="server">Server</Label>
                        <Select
                          value={newThreshold.server_id}
                          onValueChange={(value) => setNewThreshold({ ...newThreshold, server_id: value })}
                        >
                          <SelectTrigger id="server">
                            <SelectValue placeholder="Select a server" />
                          </SelectTrigger>
                          <SelectContent>
                            {servers.map((server) => (
                              <SelectItem key={server.id} value={server.id}>
                                {server.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="metric_type">Metric Type</Label>
                        <Select
                          value={newThreshold.metric_type}
                          onValueChange={(value: 'cpu' | 'memory' | 'disk' | 'network') =>
                            setNewThreshold({ ...newThreshold, metric_type: value })
                          }
                        >
                          <SelectTrigger id="metric_type">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="cpu">CPU Usage</SelectItem>
                            <SelectItem value="memory">Memory Usage</SelectItem>
                            <SelectItem value="disk">Disk Usage</SelectItem>
                            <SelectItem value="network">Network</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="comparison">Comparison</Label>
                        <Select
                          value={newThreshold.comparison}
                          onValueChange={(value: 'gt' | 'lt') =>
                            setNewThreshold({ ...newThreshold, comparison: value })
                          }
                        >
                          <SelectTrigger id="comparison">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="gt">Greater Than (&gt;)</SelectItem>
                            <SelectItem value="lt">Less Than (&lt;)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="threshold_value">Threshold Value (%)</Label>
                        <Input
                          id="threshold_value"
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          value={newThreshold.threshold_value}
                          onChange={(e) =>
                            setNewThreshold({ ...newThreshold, threshold_value: parseFloat(e.target.value) })
                          }
                          required
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" disabled={createThresholdMutation.isPending}>
                        {createThresholdMutation.isPending ? 'Creating...' : 'Create Threshold'}
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
            {thresholds.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  No thresholds configured. Create one to start monitoring.
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {thresholds.map((threshold) => (
                  <Card key={threshold.id} className="group">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">
                            {threshold.metric_type.toUpperCase()} - {threshold.comparison === 'gt' ? '>' : '<'}{' '}
                            {threshold.threshold_value}%
                          </CardTitle>
                          <CardDescription>
                            Server: {servers.find((s) => s.id === threshold.server_id)?.name || threshold.server_id}
                          </CardDescription>
                        </div>
                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => handleEditClick(threshold)}
                            title="Edit threshold"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                            onClick={() => handleDeleteClick(threshold.id)}
                            title="Delete threshold"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={threshold.enabled ? 'text-green-500' : 'text-gray-500'}>
                            {threshold.enabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleThreshold(threshold)}
                          disabled={toggleThresholdMutation.isPending}
                        >
                          <Settings className="h-4 w-4 mr-2" />
                          {threshold.enabled ? 'Disable' : 'Enable'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Edit Threshold Dialog */}
          <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
            <DialogContent>
              <form onSubmit={handleEditThreshold}>
                <DialogHeader>
                  <DialogTitle>Edit Alert Threshold</DialogTitle>
                  <DialogDescription>Update alert threshold settings</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="edit-metric_type">Metric Type</Label>
                    <Select
                      value={editThreshold.metric_type}
                      onValueChange={(value: 'cpu' | 'memory' | 'disk' | 'network') =>
                        setEditThreshold({ ...editThreshold, metric_type: value })
                      }
                    >
                      <SelectTrigger id="edit-metric_type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cpu">CPU Usage</SelectItem>
                        <SelectItem value="memory">Memory Usage</SelectItem>
                        <SelectItem value="disk">Disk Usage</SelectItem>
                        <SelectItem value="network">Network</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-comparison">Comparison</Label>
                    <Select
                      value={editThreshold.comparison}
                      onValueChange={(value: 'gt' | 'lt') =>
                        setEditThreshold({ ...editThreshold, comparison: value })
                      }
                    >
                      <SelectTrigger id="edit-comparison">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gt">Greater Than (&gt;)</SelectItem>
                        <SelectItem value="lt">Less Than (&lt;)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-threshold_value">Threshold Value (%)</Label>
                    <Input
                      id="edit-threshold_value"
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={editThreshold.threshold_value}
                      onChange={(e) =>
                        setEditThreshold({ ...editThreshold, threshold_value: parseFloat(e.target.value) })
                      }
                      required
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsEditDialogOpen(false);
                      setEditingThreshold(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updateThresholdMutation.isPending}>
                    {updateThresholdMutation.isPending ? 'Updating...' : 'Update Threshold'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Delete Confirmation Dialog */}
          <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete the alert threshold
                  {deletingThresholdId &&
                    thresholds.find((t) => t.id === deletingThresholdId) && (
                      <>
                        {' '}
                        for {thresholds.find((t) => t.id === deletingThresholdId)?.metric_type.toUpperCase()}
                      </>
                    )}
                  .
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteThreshold}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  disabled={deleteThresholdMutation.isPending}
                >
                  {deleteThresholdMutation.isPending ? 'Deleting...' : 'Delete'}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
    </div>
  );
};

