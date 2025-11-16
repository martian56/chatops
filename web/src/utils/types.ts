// Core types for the ChatOps application

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
}

export interface Server {
  id: string;
  name: string;
  host?: string;
  port?: number;
  status: 'online' | 'offline' | 'unknown';
  health_status: 'healthy' | 'warning' | 'critical';
  last_seen: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface ServerMetrics {
  server_id: string;
  timestamp: string;
  cpu: {
    usage_percent: number;
    cores: number;
    frequency_mhz: number;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
  };
  network: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  containers?: DockerContainer[];
  processes?: Process[];
}

export interface Process {
  pid: number;
  name: string;
  cpu: number;
  memory: number;
  status: string;
  user: string;
}

export interface DockerContainer {
  id: string;
  name: string;
  image: string;
  status: string;
  state: 'running' | 'stopped' | 'paused' | 'restarting';
  created: string;
  ports: Array<{
    private_port: number;
    public_port?: number;
    type: string;
  }>;
}

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug' | 'critical';
  message: string;
  source?: string;
}

export interface Alert {
  id: string;
  server_id: string;
  server_name?: string;
  type: 'cpu' | 'memory' | 'disk' | 'network' | 'service';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  threshold?: number;
  current_value?: number;
  resolved: boolean;
  created_at: string;
  resolved_at?: string;
}

export interface AlertThreshold {
  id: string;
  server_id: string;
  metric_type: 'cpu' | 'memory' | 'disk' | 'network';
  threshold_value: number;
  comparison: 'gt' | 'lt';
  enabled: boolean;
}

export interface CommandResponse {
  success: boolean;
  output: string;
  error?: string;
  exit_code?: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

