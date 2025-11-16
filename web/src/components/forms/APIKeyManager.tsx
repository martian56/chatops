import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Copy, Check, Trash2, Key } from 'lucide-react';
import { apiKeysApi } from '../../api/apiKeys';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardTitle } from '../ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

interface APIKeyManagerProps {
  serverId: string;
}

export const APIKeyManager = ({ serverId }: APIKeyManagerProps) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const queryClient = useQueryClient();

  const { data: keys = [] } = useQuery({
    queryKey: ['apiKeys', serverId],
    queryFn: () => apiKeysApi.getByServer(serverId),
  });

  const createMutation = useMutation({
    mutationFn: () => {
      const payload: { server_id: string; name?: string } = { server_id: serverId };
      if (newKeyName.trim()) {
        payload.name = newKeyName.trim();
      }
      return apiKeysApi.create(payload);
    },
    onSuccess: (data) => {
      setCreatedKey(data.key);
      setNewKeyName('');
      queryClient.invalidateQueries({ queryKey: ['apiKeys', serverId] });
    },
    onError: (error: any) => {
      console.error('Failed to create API key:', error);
      alert(`Failed to create API key: ${error?.response?.data?.detail || error.message || 'Unknown error'}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: apiKeysApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', serverId] });
    },
  });

  const handleCopy = () => {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setCreatedKey(null);
    setNewKeyName('');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">API Keys</h3>
          <p className="text-sm text-muted-foreground">
            Create API keys to authenticate agents on this server
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={(open) => {
          setIsDialogOpen(open);
          if (!open) {
            // Reset state when dialog closes
            setCreatedKey(null);
            setNewKeyName('');
          }
        }}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create API Key
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            {createdKey ? (
              <>
                <DialogHeader>
                  <DialogTitle>API Key Created</DialogTitle>
                  <DialogDescription>
                    Copy this key now - it won't be shown again!
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>API Key</Label>
                    <div className="flex gap-2">
                      <Input
                        value={createdKey}
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button variant="outline" size="icon" onClick={handleCopy}>
                        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Use this key with: <code className="bg-muted px-1 rounded">./chatops-agent -api-key YOUR_KEY</code>
                    </p>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={handleCloseDialog}>Done</Button>
                </DialogFooter>
              </>
            ) : (
              <>
                <DialogHeader>
                  <DialogTitle>Create API Key</DialogTitle>
                  <DialogDescription>
                    Create a new API key for this server. The key will be shown only once.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (!createMutation.isPending && serverId) {
                      console.log('Creating API key for server:', serverId);
                      createMutation.mutate();
                    }
                  }}
                >
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="keyName">Name (Optional)</Label>
                      <Input
                        id="keyName"
                        value={newKeyName}
                        onChange={(e) => setNewKeyName(e.target.value)}
                        placeholder="Production Agent"
                        disabled={createMutation.isPending}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleCloseDialog}
                      disabled={createMutation.isPending}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={createMutation.isPending || !serverId}
                    >
                      {createMutation.isPending ? 'Creating...' : 'Create Key'}
                    </Button>
                  </DialogFooter>
                </form>
              </>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {keys.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Key className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <CardTitle>No API Keys</CardTitle>
            <CardDescription>Create an API key to connect an agent to this server</CardDescription>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {keys.map((key) => (
            <Card key={key.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <div className="font-medium">{key.name || 'Unnamed Key'}</div>
                  <div className="text-sm text-muted-foreground">
                    Created: {new Date(key.created_at).toLocaleString()}
                    {key.last_used && (
                      <> • Last used: {new Date(key.last_used).toLocaleString()}</>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Status: {key.is_active ? (
                      <span className="text-green-500">Active</span>
                    ) : (
                      <span className="text-gray-500">Inactive</span>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => deleteMutation.mutate(key.id)}
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

