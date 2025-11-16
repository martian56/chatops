import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Search } from 'lucide-react';
import type { Process } from '../../utils/types';

interface ProcessesListProps {
  processes: Process[];
}

export const ProcessesList = ({ processes }: ProcessesListProps) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter processes based on search query
  const filteredProcesses = useMemo(() => {
    if (!searchQuery.trim()) {
      return processes;
    }

    const query = searchQuery.toLowerCase().trim();
    return processes.filter((process) => {
      return (
        process.name.toLowerCase().includes(query) ||
        process.pid.toString().includes(query) ||
        process.user.toLowerCase().includes(query) ||
        process.status.toLowerCase().includes(query) ||
        process.cpu.toFixed(2).includes(query) ||
        process.memory.toFixed(1).includes(query)
      );
    });
  }, [processes, searchQuery]);

  if (processes.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          No processes found
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Running Processes</CardTitle>
          <CardDescription>All processes sorted by CPU usage</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by name, PID, user, status, CPU, or memory..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          {searchQuery && (
            <p className="text-sm text-muted-foreground">
              Showing {filteredProcesses.length} of {processes.length} processes
            </p>
          )}
          <div className="overflow-x-auto overflow-y-auto max-h-[600px] custom-scrollbar">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">PID</th>
                  <th className="text-left p-2">Name</th>
                  <th className="text-right p-2">CPU %</th>
                  <th className="text-right p-2">Memory (MB)</th>
                  <th className="text-left p-2">User</th>
                  <th className="text-left p-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredProcesses.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-muted-foreground">
                      No processes found matching "{searchQuery}"
                    </td>
                  </tr>
                ) : (
                  filteredProcesses.map((process) => (
                  <tr key={process.pid} className="border-b">
                    <td className="p-2 font-mono">{process.pid}</td>
                    <td className="p-2 font-medium">{process.name}</td>
                    <td className="p-2 text-right">{process.cpu.toFixed(2)}%</td>
                    <td className="p-2 text-right">{process.memory.toFixed(1)}</td>
                    <td className="p-2 text-muted-foreground">{process.user}</td>
                    <td className="p-2">
                      <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                        process.status === 'running' 
                          ? 'bg-green-500/10 text-green-400 ring-1 ring-inset ring-green-500/20'
                          : 'bg-gray-500/10 text-gray-400 ring-1 ring-inset ring-gray-500/20'
                      }`}>
                        {process.status}
                      </span>
                    </td>
                  </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

