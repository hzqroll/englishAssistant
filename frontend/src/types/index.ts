/**
 * Global TypeScript type definitions
 */

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

/**
 * API error response
 */
export interface ApiErrorResponse {
  success: false
  error: string
  code?: string
}

/**
 * Pagination params
 */
export interface PaginationParams {
  page?: number
  page_size?: number
}

/**
 * Pagination response
 */
export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/**
 * Generic component props
 */
export interface BaseComponentProps {
  class?: string
  style?: string | Record<string, any>
}
