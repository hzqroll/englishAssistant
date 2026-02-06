import type { 
  RulesOnlyRequest, 
  RulesOnlyResponse, 
  OptimizeLLMRequest, 
  OptimizeLLMResponse 
} from '@/types/splitAnalysis'
import { apiClient } from './index'

export const splitAnalysisAPI = {
  // Phase 1: Rules-only analysis
  async analyzeRulesOnly(request: RulesOnlyRequest): Promise<RulesOnlyResponse> {
    const response = await apiClient.post('/api/v1/analyze/rules-only', request)
    return response.data
  },

  // Phase 2: LLM optimization
  async optimizeWithLLM(request: OptimizeLLMRequest): Promise<OptimizeLLMResponse> {
    const response = await apiClient.post('/api/v1/analyze/optimize-llm', request)
    return response.data
  }
}