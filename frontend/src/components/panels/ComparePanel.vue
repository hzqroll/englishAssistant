<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'
import type { ViewMode } from '@/stores/types'
import ErrorHighlight from '@/components/errors/ErrorHighlight.vue'

interface Props {
  showActions?: boolean
}

withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<{
  save: [result: any]
  export: [result: any]
  reanalyze: [text: string]
}>()

const { currentResult, viewMode, setViewMode } = useAnalysis()

const hasResult = computed(() => currentResult.value !== null)
const correctedText = computed(() => currentResult.value?.correctedText || '')
const originalText = computed(() => currentResult.value?.correctedText || '')

const viewModes = [
  { key: 'original-only', label: 'Original', icon: '📝' },
  { key: 'side-by-side', label: 'Side by Side', icon: '⚖️' },
  { key: 'corrected-only', label: 'Corrected', icon: '✅' }
] as const

const stats = computed(() => {
  if (!currentResult.value) return null

  return {
    totalErrors: currentResult.value.errors.length,
    highSeverity: currentResult.value.errors.filter(e => e.severity === 'high').length,
    mediumSeverity: currentResult.value.errors.filter(e => e.severity === 'medium').length,
    lowSeverity: currentResult.value.errors.filter(e => e.severity === 'low').length,
    processingTime: currentResult.value.processingTimeMs || 0
  }
})

function setView(mode: ViewMode) {
  if (viewMode.value === mode) {
    setViewMode('side-by-side')
  } else {
    setViewMode(mode)
  }
}

function handleSave() {
  emit('save', currentResult.value)
}

function handleExport() {
  emit('export', currentResult.value)
}

function handleReanalyze() {
  emit('reanalyze', originalText.value)
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'high': return 'text-red-600 bg-red-50'
    case 'medium': return 'text-yellow-600 bg-yellow-50'
    case 'low': return 'text-blue-600 bg-blue-50'
    default: return 'text-gray-600 bg-gray-50'
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Comparison</h2>

      <div v-if="hasResult" class="flex items-center gap-2">
        <span class="text-sm text-gray-500">{{ stats?.totalErrors }} errors</span>
        <span class="text-gray-300">|</span>
        <span class="text-sm text-gray-500">{{ stats?.processingTime }}ms</span>
      </div>
    </div>

    <div v-if="!hasResult" class="flex-1 flex items-center justify-center text-gray-400">
      <div class="text-center p-8">
        <div class="text-4xl mb-4">📄</div>
        <p class="text-lg font-medium text-gray-600">No analysis result yet</p>
        <p class="text-sm text-gray-500 mt-2">Enter text in the input panel to start</p>
      </div>
    </div>

    <div v-else class="flex-1 flex flex-col min-h-0">
      <div class="flex items-center justify-between mb-4 bg-gray-50 rounded-lg p-2">
        <div class="flex gap-1">
          <button
            v-for="mode in viewModes"
            :key="mode.key"
            @click="setView(mode.key as ViewMode)"
            class="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all"
            :class="viewMode === mode.key
              ? 'bg-primary-600 text-white shadow-md'
              : 'bg-white text-gray-600 hover:bg-gray-100'"
          "
          >
            <span>{{ mode.icon }}</span>
            <span>{{ mode.label }}</span>
          </button>
        </div>

        <div v-if="showActions" class="flex gap-2">
          <button
            @click="handleReanalyze"
            class="px-3 py-2 rounded-md text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
            title="Re-analyze"
          >
            🔄
          </button>
          <button
            @click="handleSave"
            class="px-3 py-2 rounded-md text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
            title="Save"
          >
            💾
          </button>
          <button
            @click="handleExport"
            class="px-3 py-2 rounded-md text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
            title="Export"
          >
            📥
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto space-y-4">
        <ErrorHighlight
          :original-text="originalText"
          :corrected-text="correctedText"
          :errors="currentResult.errors"
          :view-mode="viewMode"
        />
      </div>

      <div v-if="stats" class="mt-4 pt-4 border-t border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Error Statistics</h3>
        <div class="grid grid-cols-2 gap-3">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-600">High</span>
            <span class="font-semibold" :class="getSeverityColor('high')">
              {{ stats.highSeverity }}
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-600">Medium</span>
            <span class="font-semibold" :class="getSeverityColor('medium')">
              {{ stats.mediumSeverity }}
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-600">Low</span>
            <span class="font-semibold" :class="getSeverityColor('low')">
              {{ stats.lowSeverity }}
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg col-span-2">
            <span class="text-xs text-gray-600">Total</span>
            <span class="font-semibold text-primary-600">
              {{ stats.totalErrors }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
