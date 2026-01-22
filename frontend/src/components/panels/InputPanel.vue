<script setup lang="ts">
import { ref } from 'vue'
import { useAnalysis, useUI } from '@/composables'
import type { CorrectionMode } from '@/stores/types'

// TODO: Implement input panel with text area and mode selection
const { analyzeText, isAnalyzing, error } = useAnalysis()
const { showSuccess, showError } = useUI()

const text = ref('')
const selectedMode = ref<CorrectionMode>('accuracy')

async function handleAnalyze() {
  if (!text.value.trim()) {
    showError('Please enter some text to analyze')
    return
  }

  try {
    await analyzeText(text.value, selectedMode.value)
    showSuccess('Analysis completed successfully')
  } catch (err: any) {
    showError(err.message || 'Analysis failed')
  }
}

function clearText() {
  text.value = ''
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Input Text</h2>
      <button
        v-if="text"
        @click="clearText"
        class="text-sm text-gray-500 hover:text-gray-700"
      >
        Clear
      </button>
    </div>

    <!-- Correction mode selection -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">Correction Mode</label>
      <div class="flex space-x-2">
        <button
          @click="selectedMode = 'accuracy'"
          class="flex-1 px-4 py-2 rounded-lg transition-colors"
          :class="selectedMode === 'accuracy' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700'"
        >
          Accuracy First
        </button>
        <button
          @click="selectedMode = 'naturalness'"
          class="flex-1 px-4 py-2 rounded-lg transition-colors"
          :class="selectedMode === 'naturalness' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700'"
        >
          Naturalness First
        </button>
      </div>
    </div>

    <!-- Text input area -->
    <div class="flex-1 mb-4">
      <textarea
        v-model="text"
        placeholder="Enter your English text here..."
        class="w-full h-full min-h-[300px] p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
        :disabled="isAnalyzing"
      ></textarea>
    </div>

    <!-- Analyze button -->
    <button
      @click="handleAnalyze"
      :disabled="isAnalyzing || !text.trim()"
      class="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
    >
      {{ isAnalyzing ? 'Analyzing...' : 'Analyze' }}
    </button>

    <!-- Error display -->
    <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>
  </div>
</template>
