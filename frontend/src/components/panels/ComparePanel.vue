<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysis } from '@/composables'
import type { ViewMode } from '@/stores/types'

// TODO: Implement side-by-side comparison panel
const { currentResult, viewMode, setViewMode } = useAnalysis()

const hasResult = computed(() => currentResult.value !== null)

function toggleViewMode(mode: ViewMode) {
  if (viewMode.value === mode) {
    setViewMode('side-by-side')
  } else {
    setViewMode(mode)
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Comparison</h2>

      <!-- View mode toggles -->
      <div v-if="hasResult" class="flex space-x-1">
        <button
          @click="toggleViewMode('original-only')"
          class="px-2 py-1 text-xs rounded transition-colors"
          :class="viewMode === 'original-only' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'"
          title="Show original only"
        >
          Original
        </button>
        <button
          @click="toggleViewMode('side-by-side')"
          class="px-2 py-1 text-xs rounded transition-colors"
          :class="viewMode === 'side-by-side' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'"
          title="Show side by side"
        >
          Both
        </button>
        <button
          @click="toggleViewMode('corrected-only')"
          class="px-2 py-1 text-xs rounded transition-colors"
          :class="viewMode === 'corrected-only' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'"
          title="Show corrected only"
        >
          Corrected
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!hasResult" class="flex-1 flex items-center justify-center text-gray-400">
      <div class="text-center">
        <p class="text-lg">No analysis result yet</p>
        <p class="text-sm mt-2">Enter text in the input panel to start</p>
      </div>
    </div>

    <!-- Comparison content -->
    <div v-else class="flex-1 flex flex-col space-y-4 overflow-y-auto">
      <!-- Original text -->
      <div
        v-if="viewMode === 'side-by-side' || viewMode === 'original-only'"
        class="flex-1 p-4 bg-gray-50 rounded-lg border border-gray-200"
      >
        <h3 class="text-sm font-medium text-gray-700 mb-2">Original</h3>
        <p class="text-gray-900 whitespace-pre-wrap">{{ currentResult?.originalText }}</p>
      </div>

      <!-- Corrected text -->
      <div
        v-if="viewMode === 'side-by-side' || viewMode === 'corrected-only'"
        class="flex-1 p-4 bg-green-50 rounded-lg border border-green-200"
      >
        <h3 class="text-sm font-medium text-gray-700 mb-2">Corrected</h3>
        <p class="text-gray-900 whitespace-pre-wrap">{{ currentResult?.correctedText }}</p>
      </div>
    </div>
  </div>
</template>
