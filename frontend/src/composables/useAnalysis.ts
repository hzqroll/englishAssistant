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
    hasErrors,
    errorCount,
    learningTips,
    analyzeText,
    setCorrectionMode,
    setViewMode,
    resetAnalysis,
    clearError,
  }
}
