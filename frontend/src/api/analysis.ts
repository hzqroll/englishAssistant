import apiClient from './index'
import type { CorrectionMode, AnalysisApiResponse } from '@/stores/types'

/**
 * Analysis API
 * Handles text analysis and correction
 */

export interface AnalyzeRequest {
  text: string
  mode: CorrectionMode
}

export const analysisApi = {
  /**
   * Analyze and correct text
   */
  async analyze(data: AnalyzeRequest) {
    return apiClient.post<AnalysisApiResponse>('/analyze', data)
  },
}
