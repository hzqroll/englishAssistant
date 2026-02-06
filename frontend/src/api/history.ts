import apiClient from './index'
import type { CorrectionMode } from '@/stores/types'

/**
 * History API
 * Handles analysis history retrieval and management
 */

export interface GetHistoryListParams {
  page?: number
  page_size?: number
  mode?: CorrectionMode
  date_from?: string
  date_to?: string
  search?: string
}

export interface HistoryListResponse {
  items: Array<{
    id: string
    original_text: string
    corrected_text: string
    mode: string
    error_count: number
    created_at: string
  }>
  total: number
  page: number
  page_size: number
}

export const historyApi = {
  /**
   * Get user's analysis history
   */
  async getList(params?: GetHistoryListParams) {
    return apiClient.get<HistoryListResponse>('/api/v1/history', { params })
  },

  /**
   * Get specific analysis detail
   */
  async getDetail(id: string) {
    return apiClient.get<{ success: boolean; data: any }>(`/api/v1/history/${id}`)
  },

  /**
   * Delete analysis record
   */
  async delete(id: string) {
    return apiClient.delete<{ success: boolean }>(`/api/v1/history/${id}`)
  },
}
