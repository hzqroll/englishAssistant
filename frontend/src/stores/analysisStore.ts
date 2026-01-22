import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AnalysisState, AnalysisResult, CorrectionMode, ViewMode } from './types'
import { analysisApi } from '@/api/analysis'

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const currentResult = ref<AnalysisResult | null>(null)
  const isAnalyzing = ref(false)
  const mode = ref<CorrectionMode>('accuracy')
  const viewMode = ref<ViewMode>('side-by-side')
  const error = ref<string | null>(null)
  const progress = ref(0)

  // Computed
  const analysisState = computed<AnalysisState>(() => ({
    currentResult: currentResult.value,
    isAnalyzing: isAnalyzing.value,
    mode: mode.value,
    viewMode: viewMode.value,
    error: error.value,
    progress: progress.value,
  }))

  // Actions
  async function analyzeText(text: string, correctionMode: CorrectionMode) {
    // TODO: Implement text analysis logic
    isAnalyzing.value = true
    error.value = null
    progress.value = 0

    try {
      // TODO: Add progress simulation or real-time updates
      const response = await analysisApi.analyze({ text, mode: correctionMode })
      currentResult.value = response.data.data
      mode.value = correctionMode
      progress.value = 100
      return response.data.data
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
    error.value = null
    progress.value = 0
  }

  function clearError() {
    error.value = null
  }

  return {
    currentResult,
    isAnalyzing,
    mode,
    viewMode,
    error,
    progress,
    analysisState,
    analyzeText,
    setCorrectionMode,
    setViewMode,
    resetAnalysis,
    clearError,
  }
})
