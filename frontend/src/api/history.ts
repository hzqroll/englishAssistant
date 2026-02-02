import apiClient from './index'
import type { HistoryItem, CorrectionMode } from '@/stores/types'

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
  items: HistoryItem[]
  total: number
  page: number
  page_size: number
}

export const historyApi = {
  /**
   * Get user's analysis history
   */
  async getList(params?: GetHistoryListParams) {
    return apiClient.get<{ success: boolean; data: HistoryListResponse }>('/history', { params })
  },

  /**
   * Get specific analysis detail
   */
  async getDetail(id: string) {
    return apiClient.get<{ success: boolean; data: any }>(`/history/${id}`)
  },

  /**
   * Delete analysis record
   */
  async delete(id: string) {
    return apiClient.delete<{ success: boolean }>(`/history/${id}`)
  },
}
