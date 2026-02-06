import { computed } from 'vue'
import { useAnalysisStore } from '@/stores'
import type { CorrectionMode, ViewMode } from '@/stores/types'

/**
 * Analysis composable
 * Provides text analysis utilities and state management
 */
export function useAnalysis() {
  const analysisStore = useAnalysisStore()

  // Computed
  const currentResult = computed(() => analysisStore.currentResult)
  const isAnalyzing = computed(() => analysisStore.isAnalyzing)
  const mode = computed(() => analysisStore.mode)
  const viewMode = computed(() => analysisStore.viewMode)
  const error = computed(() => analysisStore.error)
  const progress = computed(() => analysisStore.progress)
  const ruleResult = computed(() => analysisStore.ruleResult)
  const llmResult = computed(() => analysisStore.llmResult)
  const isOptimizing = computed(() => analysisStore.isOptimizing)
  const llmError = computed(() => analysisStore.llmError)

  // Derived computed
  const hasErrors = computed(() => {
    return currentResult.value && currentResult.value.errors.length > 0
  })

  const errorCount = computed(() => {
    return currentResult.value?.errors.length || 0
  })

  const learningTips = computed(() => {
    return currentResult.value?.learningTips || []
  })

  // Actions
  async function analyzeText(text: string, correctionMode: CorrectionMode) {
    return await analysisStore.analyzeText(text, correctionMode)
  }

  async function analyzeWithRules(text: string, correctionMode: CorrectionMode) {
    return await analysisStore.analyzeWithRules(text, correctionMode)
  }

  async function optimizeWithLLM(analysisId?: string) {
    return await analysisStore.optimizeWithLLM(analysisId)
  }

  function setCorrectionMode(newMode: CorrectionMode) {
    analysisStore.setCorrectionMode(newMode)
  }

  function setViewMode(newMode: ViewMode) {
    analysisStore.setViewMode(newMode)
  }

  function resetAnalysis() {
    analysisStore.resetAnalysis()
  }

  function clearError() {
    analysisStore.clearError()
  }

  return {
    currentResult,
    isAnalyzing,
    mode,
    viewMode,
    error,
    progress,
    ruleResult,
    llmResult,
    isOptimizing,
    llmError,
    hasErrors,
    errorCount,
    learningTips,
    analyzeText,
    analyzeWithRules,
    optimizeWithLLM,
    setCorrectionMode,
    setViewMode,
    resetAnalysis,
    clearError,
  }
}
