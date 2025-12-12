import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Server as ServerIcon, Activity, AlertCircle, Edit, Trash2 } from 'lucide-react';
import { serversApi } from '../../api/servers';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { useServersStore } from '../../store/servers';
import { HEALTH_STATUS_COLORS, SERVER_STATUS_COLORS } from '../../utils/constants';
import type { CreateServerDto, UpdateServerDto } from '../../api/servers';
import type { Server } from '../../utils/types';
import { ServersPageSkeleton } from '../../components/skeletons/ServersPageSkeleton';
import { toast } from 'sonner';
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

export const ServersPage = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingServer, setEditingServer] = useState<Server | null>(null);
  const [deletingServerId, setDeletingServerId] = useState<string | null>(null);
  const [newServer, setNewServer] = useState<CreateServerDto>({
    name: '',
  });
  const [editServer, setEditServer] = useState<UpdateServerDto>({
    name: '',
  });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setSelectedServer } = useServersStore();

  const { data: servers = [], isLoading } = useQuery({
    queryKey: ['servers'],
    queryFn: serversApi.getAll,
  });

  const createMutation = useMutation({
    mutationFn: serversApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      setIsDialogOpen(false);
      setNewServer({ name: '' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateServerDto }) => serversApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      setIsEditDialogOpen(false);
      setEditingServer(null);
      setEditServer({ name: '' });
      toast.success('Server updated successfully');
    },
    onError: (error: any) => {
      toast.error(`Failed to update server: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: serversApi.delete,
    onSuccess: (_, serverId) => {
      // Optimistically remove the server from cache immediately
      queryClient.setQueryData<Server[]>(['servers'], (old) => {
        return old?.filter((server) => server.id !== serverId) || [];
      });
      // Also invalidate to refetch in background for consistency
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      setIsDeleteDialogOpen(false);
      setDeletingServerId(null);
      toast.success('Server deleted successfully');
    },
    onError: (error: any) => {
      // Refetch on error to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      toast.error(`Failed to delete server: ${error?.response?.data?.detail || error.message}`);
    },
  });

  const handleCreateServer = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(newServer);
  };

  const handleEditServer = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingServer) {
      updateMutation.mutate({ id: editingServer.id, data: editServer });
    }
  };

  const handleDeleteServer = () => {
    if (deletingServerId) {
      deleteMutation.mutate(deletingServerId);
    }
  };

  const handleServerClick = (server: typeof servers[0]) => {
    setSelectedServer(server);
    navigate(`/servers/${server.id}`);
  };

  const handleEditClick = (e: React.MouseEvent, server: Server) => {
    e.stopPropagation();
    setEditingServer(server);
    setEditServer({
      name: server.name,
      host: server.host,
      port: server.port,
    });
    setIsEditDialogOpen(true);
  };

  const handleDeleteClick = (e: React.MouseEvent, serverId: string) => {
    e.stopPropagation();
    setDeletingServerId(serverId);
    setIsDeleteDialogOpen(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <Activity className="h-4 w-4 text-green-500" />;
      case 'offline':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <ServerIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Servers</h1>
            <p className="text-muted-foreground">Manage and monitor your servers and Life</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Server
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateServer}>
                <DialogHeader>
                  <DialogTitle>Add New Server</DialogTitle>
                  <DialogDescription>
                    Create a new server entry. After creation, generate an API key for the agent to connect.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Server Name</Label>
                    <Input
                      id="name"
                      value={newServer.name}
                      onChange={(e) => setNewServer({ ...newServer, name: e.target.value })}
                      placeholder="Production Server"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="host">Host (Optional)</Label>
                    <Input
                      id="host"
                      value={newServer.host || ''}
                      onChange={(e) => setNewServer({ ...newServer, host: e.target.value || undefined })}
                      placeholder="192.168.1.100"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="port">Port (Optional)</Label>
                    <Input
                      id="port"
                      type="number"
                      value={newServer.port || ''}
                      onChange={(e) => setNewServer({ ...newServer, port: e.target.value ? parseInt(e.target.value) : undefined })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={createMutation.isPending}>
                    {createMutation.isPending ? 'Adding...' : 'Add Server'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Edit Server Dialog */}
          <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
            <DialogContent>
              <form onSubmit={handleEditServer}>
                <DialogHeader>
                  <DialogTitle>Edit Server</DialogTitle>
                  <DialogDescription>Update server information</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="edit-name">Server Name</Label>
                    <Input
                      id="edit-name"
                      value={editServer.name}
                      onChange={(e) => setEditServer({ ...editServer, name: e.target.value })}
                      placeholder="Production Server"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-host">Host (Optional)</Label>
                    <Input
                      id="edit-host"
                      value={editServer.host || ''}
                      onChange={(e) => setEditServer({ ...editServer, host: e.target.value || undefined })}
                      placeholder="192.168.1.100"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-port">Port (Optional)</Label>
                    <Input
                      id="edit-port"
                      type="number"
                      value={editServer.port || ''}
                      onChange={(e) => setEditServer({ ...editServer, port: e.target.value ? parseInt(e.target.value) : undefined })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsEditDialogOpen(false);
                      setEditingServer(null);
                      setEditServer({ name: '' });
                    }}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updateMutation.isPending}>
                    {updateMutation.isPending ? 'Updating...' : 'Update Server'}
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
                  This action cannot be undone. This will permanently delete the server
                  {deletingServerId && servers.find((s) => s.id === deletingServerId) && (
                    <> "{servers.find((s) => s.id === deletingServerId)?.name}"</>
                  )}
                  {' '}and all associated data.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteServer}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>

        {isLoading ? (
          <ServersPageSkeleton />
        ) : servers.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <ServerIcon className="h-12 w-12 text-muted-foreground mb-4" />
              <CardTitle>No servers found</CardTitle>
              <CardDescription>Add your first server to get started</CardDescription>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {servers.map((server) => (
              <Card
                key={server.id}
                className="cursor-pointer hover:shadow-lg transition-shadow group"
                onClick={() => handleServerClick(server)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{server.name}</CardTitle>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(server.status)}
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={(e) => handleEditClick(e, server)}
                          title="Edit server"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          onClick={(e) => handleDeleteClick(e, server.id)}
                          title="Delete server"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  <CardDescription>
                    {server.host && server.port ? `${server.host}:${server.port}` : 'No address specified'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Status:</span>
                      <span className={SERVER_STATUS_COLORS[server.status]}>
                        {server.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Health:</span>
                      <span className={HEALTH_STATUS_COLORS[server.health_status]}>
                        {server.health_status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Last Seen:</span>
                      <span>{new Date(server.last_seen).toLocaleString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
    </div>
  );
};

