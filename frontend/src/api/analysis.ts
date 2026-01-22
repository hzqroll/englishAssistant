import apiClient from './index'
import type { CorrectionMode, AnalysisResult } from '@/stores/types'

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
    return apiClient.post<{ success: boolean; data: AnalysisResult }>('/analyze', data)
  },
}
