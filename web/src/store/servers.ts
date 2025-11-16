import { create } from 'zustand';
import type { Server } from '../utils/types';

interface ServersState {
  servers: Server[];
  selectedServer: Server | null;
  setServers: (servers: Server[]) => void;
  addServer: (server: Server) => void;
  updateServer: (id: string, server: Partial<Server>) => void;
  removeServer: (id: string) => void;
  setSelectedServer: (server: Server | null) => void;
}

export const useServersStore = create<ServersState>((set) => ({
  servers: [],
  selectedServer: null,
  
  setServers: (servers: Server[]) => set({ servers }),
  
  addServer: (server: Server) =>
    set((state) => ({ servers: [...state.servers, server] })),
  
  updateServer: (id: string, server: Partial<Server>) =>
    set((state) => ({
      servers: state.servers.map((s) => (s.id === id ? { ...s, ...server } : s)),
      selectedServer:
        state.selectedServer?.id === id
          ? { ...state.selectedServer, ...server }
          : state.selectedServer,
    })),
  
  removeServer: (id: string) =>
    set((state) => ({
      servers: state.servers.filter((s) => s.id !== id),
      selectedServer: state.selectedServer?.id === id ? null : state.selectedServer,
    })),
  
  setSelectedServer: (server: Server | null) => set({ selectedServer: server }),
}));

