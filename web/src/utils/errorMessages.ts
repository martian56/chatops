import { AxiosError } from 'axios';
import type { ApiError } from './types';

/**
 * Custom transformations for API error details
 */
type DetailTransformer = (detail: string) => string | null;

/**
 * Status code to message mapping
 */
type StatusCodeMap = Record<number, string>;

/**
 * Common error processing logic for Axios errors
 */
const processError = (
  error: unknown,
  statusCodeMap: StatusCodeMap,
  defaultMessage: string,
  detailTransformer?: DetailTransformer
): string => {
  if (!error) {
    return 'An unexpected error occurred';
  }

  // Check if it's an Axios error
  if (error instanceof Error && 'isAxiosError' in error) {
    const axiosError = error as AxiosError<ApiError>;
    
    // Try to get the error detail from the response
    if (axiosError.response?.data?.detail) {
      const detail = axiosError.response.data.detail;
      
      // Apply custom transformation if provided
      if (detailTransformer) {
        const transformed = detailTransformer(detail);
        if (transformed) {
          return transformed;
        }
      }
      
      return detail;
    }

    // Map status codes to friendly messages
    const status = axiosError.response?.status;
    
    if (status && statusCodeMap[status]) {
      return statusCodeMap[status];
    }

    // Network errors
    if (axiosError.code === 'ERR_NETWORK' || !axiosError.response) {
      return 'Unable to connect to the server. Please check your internet connection';
    }

    return defaultMessage;
  }

  // Generic error handling
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
};

/**
 * Maps authentication errors to user-friendly messages
 */
export const getAuthErrorMessage = (error: unknown): string => {
  const statusCodeMap: StatusCodeMap = {
    400: 'Invalid email or password format',
    401: 'Invalid email or password',
    403: 'Access forbidden. Your account may be disabled',
    404: 'Service not found. Please try again later',
    422: 'Please check your input and try again',
    429: 'Too many login attempts. Please try again later',
    500: 'Server error. Please try again later',
    503: 'Service temporarily unavailable. Please try again later',
  };

  return processError(
    error,
    statusCodeMap,
    'An error occurred during authentication. Please try again'
  );
};

/**
 * Maps registration errors to user-friendly messages
 */
export const getRegisterErrorMessage = (error: unknown): string => {
  const statusCodeMap: StatusCodeMap = {
    400: 'Please check your information and try again',
    422: 'Invalid information provided. Please check all fields',
    429: 'Too many registration attempts. Please try again later',
    500: 'Server error. Please try again later',
    503: 'Service temporarily unavailable. Please try again later',
  };

  // Custom transformer for registration-specific error details
  const detailTransformer: DetailTransformer = (detail: string) => {
    if (detail.toLowerCase().includes('already exists') || detail.toLowerCase().includes('duplicate')) {
      return 'An account with this email or username already exists';
    }
    return null;
  };

  return processError(
    error,
    statusCodeMap,
    'An error occurred during registration. Please try again',
    detailTransformer
  );
};
