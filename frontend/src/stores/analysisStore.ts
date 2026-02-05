import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  AnalysisState,
  AnalysisResult,
  CorrectionMode,
  ViewMode,
  RuleBasedResult,
  LLMResult
} from './types'
import { analysisApi } from '@/api/analysis'

export const useAnalysisStore = defineStore('analysis', () => {
  // State - Legacy
  const currentResult = ref<AnalysisResult | null>(null)
  const isAnalyzing = ref(false)
  const mode = ref<CorrectionMode>('accuracy')
  const viewMode = ref<ViewMode>('side-by-side')
  const error = ref<string | null>(null)
  const progress = ref(0)

  // State - New Split Analysis
  const ruleResult = ref<RuleBasedResult | null>(null)
  const llmResult = ref<LLMResult | null>(null)
  const isOptimizing = ref(false)
  const llmError = ref<string | null>(null)

  // Computed
  const analysisState = computed<AnalysisState>(() => ({
    currentResult: currentResult.value,
    isAnalyzing: isAnalyzing.value,
    mode: mode.value,
    viewMode: viewMode.value,
    error: error.value,
    progress: progress.value,
  }))

  const hasRuleResult = computed(() => ruleResult.value !== null)
  const hasLLMResult = computed(() => llmResult.value !== null)
  const canOptimize = computed(() => hasRuleResult.value && !hasLLMResult.value && !isOptimizing.value)

  // Actions - New Split Analysis

  /**
   * Step 1: Analyze with LanguageTool only (fast, rule-based)
   */
  async function analyzeWithRules(text: string, correctionMode: CorrectionMode) {
    isAnalyzing.value = true
    error.value = null
    ruleResult.value = null
    llmResult.value = null
    progress.value = 0

    try {
      const response = await analysisApi.analyzeRulesOnly({
        text,
        mode: correctionMode,
        language: 'en-US'
      })

      if (response.data.success) {
        ruleResult.value = response.data.data
        mode.value = correctionMode
        progress.value = 50
        return response.data.data
      } else {
        throw new Error('Rule analysis failed')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Rule analysis failed'
      throw err
    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * Step 2: Optimize with LLM (requires ruleResult to be present)
   */
  async function optimizeWithLLM(analysisId?: string) {
    const idToUse = analysisId || ruleResult.value?.analysis_id

    if (!idToUse) {
      const errorMsg = 'No analysis ID available. Please run rule analysis first.'
      llmError.value = errorMsg
      throw new Error(errorMsg)
    }

    isOptimizing.value = true
    llmError.value = null

    try {
      const response = await analysisApi.optimizeWithLLM({
        analysis_id: idToUse
      })

      if (response.data.success) {
        llmResult.value = response.data.data
        progress.value = 100
        return response.data.data
      } else {
        throw new Error('LLM optimization failed')
      }
    } catch (err: any) {
      llmError.value = err.response?.data?.message || 'LLM optimization failed'
      throw err
    } finally {
      isOptimizing.value = false
    }
  }

  // Actions - Legacy (for backward compatibility)

  async function analyzeText(text: string, correctionMode: CorrectionMode) {
    isAnalyzing.value = true
    error.value = null
    progress.value = 0

    try {
      const response = await analysisApi.analyze({ text, mode: correctionMode })
      const data = response.data

      const result: AnalysisResult = {
        id: data.analysis_id,
        originalText: data.original_text,
        correctedText: data.corrected_text,
        mode: data.mode as CorrectionMode,
        errors: data.errors.map((e, index) => ({
          id: `err-${index}-${e.start_index}`,
          type: e.error_type,
          severity: e.severity,
          originalText: e.original_span,
          correctedText: e.corrected_span,
          message: e.explanation || e.rule_description || 'Found an error',
          suggestion: e.corrected_span,
          startPosition: e.start_index,
          endPosition: e.end_index
        })),
        learningTips: [],
        createdAt: data.created_at
      }

      currentResult.value = result
      mode.value = correctionMode
      progress.value = 100
      return result
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Analysis failed'
      throw err
    } finally {
      isAnalyzing.value = false
    }
  }

  function setCorrectionMode(newMode: CorrectionMode) {
    mode.value = newMode
  }

  function setViewMode(newMode: ViewMode) {
    viewMode.value = newMode
  }

  function resetAnalysis() {
    currentResult.value = null
    ruleResult.value = null
    llmResult.value = null
    error.value = null
    llmError.value = null
    progress.value = 0
  }

  function clearError() {
    error.value = null
    llmError.value = null
  }

  return {
    // Legacy state
    currentResult,
    isAnalyzing,
    mode,
    viewMode,
    error,
    progress,
    analysisState,

    // New split analysis state
    ruleResult,
    llmResult,
    isOptimizing,
    llmError,
    hasRuleResult,
    hasLLMResult,
    canOptimize,

    // Actions
    analyzeText, // Legacy
    analyzeWithRules, // New
    optimizeWithLLM, // New
    setCorrectionMode,
    setViewMode,
    resetAnalysis,
    clearError,
  }
})
