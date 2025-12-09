import { AxiosError } from 'axios';
import type { ApiError } from './types';

/**
 * Maps authentication errors to user-friendly messages
 */
export const getAuthErrorMessage = (error: unknown): string => {
  if (!error) {
    return 'An unexpected error occurred';
  }

  // Check if it's an Axios error
  if (error instanceof Error && 'isAxiosError' in error) {
    const axiosError = error as AxiosError<ApiError>;
    
    // Try to get the error detail from the response
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }

    // Map status codes to friendly messages
    const status = axiosError.response?.status;
    
    switch (status) {
      case 400:
        return 'Invalid email or password format';
      case 401:
        return 'Invalid email or password';
      case 403:
        return 'Access forbidden. Your account may be disabled';
      case 404:
        return 'Service not found. Please try again later';
      case 422:
        return 'Please check your input and try again';
      case 429:
        return 'Too many login attempts. Please try again later';
      case 500:
        return 'Server error. Please try again later';
      case 503:
        return 'Service temporarily unavailable. Please try again later';
      default:
        // Network errors
        if (axiosError.code === 'ERR_NETWORK' || !axiosError.response) {
          return 'Unable to connect to the server. Please check your internet connection';
        }
        return 'An error occurred during authentication. Please try again';
    }
  }

  // Generic error handling
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
};

/**
 * Maps registration errors to user-friendly messages
 */
export const getRegisterErrorMessage = (error: unknown): string => {
  if (!error) {
    return 'An unexpected error occurred';
  }

  // Check if it's an Axios error
  if (error instanceof Error && 'isAxiosError' in error) {
    const axiosError = error as AxiosError<ApiError>;
    
    // Try to get the error detail from the response
    if (axiosError.response?.data?.detail) {
      const detail = axiosError.response.data.detail;
      
      // Make common error messages more user-friendly
      if (detail.toLowerCase().includes('already exists') || detail.toLowerCase().includes('duplicate')) {
        return 'An account with this email or username already exists';
      }
      
      return detail;
    }

    // Map status codes to friendly messages
    const status = axiosError.response?.status;
    
    switch (status) {
      case 400:
        return 'Please check your information and try again';
      case 422:
        return 'Invalid information provided. Please check all fields';
      case 429:
        return 'Too many registration attempts. Please try again later';
      case 500:
        return 'Server error. Please try again later';
      case 503:
        return 'Service temporarily unavailable. Please try again later';
      default:
        // Network errors
        if (axiosError.code === 'ERR_NETWORK' || !axiosError.response) {
          return 'Unable to connect to the server. Please check your internet connection';
        }
        return 'An error occurred during registration. Please try again';
    }
  }

  // Generic error handling
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
};
