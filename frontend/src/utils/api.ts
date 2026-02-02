import type { AxiosError } from 'axios'

/**
 * API utility functions
 */

export interface ApiError {
  message: string
  code?: string
  status?: number
}

/**
 * Extract error message from API error response
 */
export function getApiErrorMessage(error: AxiosError<any>): string {
  if (error.response?.data?.message) {
    return error.response.data.message
  }

  if (error.response?.data?.error) {
    return error.response.data.error
  }

  if (error.message) {
    return error.message
  }

  return 'An unexpected error occurred'
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: AxiosError): boolean {
  return !error.response && !!error.request
}

/**
 * Check if error is a server error (5xx)
 */
export function isServerError(error: AxiosError): boolean {
  return !!error.response && error.response.status >= 500
}

/**
 * Check if error is a client error (4xx)
 */
export function isClientError(error: AxiosError): boolean {
  return !!error.response && error.response.status >= 400 && error.response.status < 500
}

/**
 * Check if error is unauthorized (401)
 */
export function isUnauthorized(error: AxiosError): boolean {
  return error.response?.status === 401
}

/**
 * Check if error is rate limited (429)
 */
export function isRateLimited(error: AxiosError): boolean {
  return error.response?.status === 429
}
