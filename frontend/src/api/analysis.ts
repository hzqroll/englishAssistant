import apiClient from './index'
import type {
  CorrectionMode,
  AnalysisApiResponse,
  RuleBasedResult,
  LLMResult
} from '@/stores/types'

/**
 * Analysis API
 * Handles text analysis and correction
 */

export interface AnalyzeRequest {
  text: string
  mode: CorrectionMode
  language?: string
}

export interface OptimizeLLMRequest {
  analysis_id: string
}

export const analysisApi = {
  /**
   * Analyze text using LanguageTool only (fast, rule-based)
   */
  async analyzeRulesOnly(data: AnalyzeRequest) {
    return apiClient.post<{ success: boolean; data: RuleBasedResult }>('/api/v1/analyze/rules-only', {
      text: data.text,
      language: data.language || 'en-US',
      mode: data.mode
    })
  },

  /**
   * Optimize with LLM (requires existing analysis_id)
   */
  async optimizeWithLLM(data: OptimizeLLMRequest) {
    return apiClient.post<{ success: boolean; data: LLMResult }>('/api/v1/analyze/optimize-llm', {
      analysis_id: data.analysis_id
    })
  },

  /**
   * Legacy: Full analysis (both LanguageTool + LLM in one call)
   * @deprecated Use analyzeRulesOnly + optimizeWithLLM instead
   */
  async analyze(data: AnalyzeRequest) {
    return apiClient.post<AnalysisApiResponse>('/analyze', data)
  },
}
