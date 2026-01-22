import apiClient from './index'

/**
 * Export API
 * Handles export of analysis results
 */

export type ExportFormat = 'json' | 'markdown' | 'pdf'

export interface ExportRequest {
  analysis_id: string
  format: ExportFormat
}

export const exportApi = {
  /**
   * Export analysis result
   */
  async export(data: ExportRequest) {
    return apiClient.post<{ success: boolean; data: { download_url: string } }>('/export', data)
  },
}
