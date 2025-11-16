// Application constants

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const METRIC_UPDATE_INTERVAL = 2000; // 2 seconds
export const LOG_BUFFER_SIZE = 1000; // Max log entries to keep in memory

export const HEALTH_STATUS_COLORS = {
  healthy: 'text-green-500',
  warning: 'text-yellow-500',
  critical: 'text-red-500',
} as const;

export const SERVER_STATUS_COLORS = {
  online: 'text-green-500',
  offline: 'text-red-500',
  unknown: 'text-gray-500',
} as const;

