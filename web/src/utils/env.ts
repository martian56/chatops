/**
 * Environment variable validation and configuration
 */

interface EnvConfig {
  apiUrl: string;
  wsUrl: string;
  environment: 'development' | 'production' | 'test';
}

/**
 * Validates and returns environment configuration
 * @throws Error if required environment variables are missing or invalid
 */
export function getEnvConfig(): EnvConfig {
  const apiUrl = import.meta.env.VITE_API_URL;
  const environment = import.meta.env.MODE as 'development' | 'production' | 'test';

  // Default to localhost in development
  const finalApiUrl = apiUrl || 'http://localhost:8000';

  // Validate API URL format
  try {
    new URL(finalApiUrl);
  } catch (error) {
    throw new Error(`Invalid API URL: ${finalApiUrl}`);
  }

  // Convert http(s) to ws(s) for WebSocket
  const wsUrl = finalApiUrl.replace(/^http/, 'ws');

  return {
    apiUrl: finalApiUrl,
    wsUrl,
    environment,
  };
}

// Export config for use throughout the app
export const config = getEnvConfig();

