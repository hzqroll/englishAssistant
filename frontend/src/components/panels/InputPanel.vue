<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAnalysis, useUI } from '@/composables'
import type { CorrectionMode } from '@/stores/types'

const { analyzeText, isAnalyzing, error, progress } = useAnalysis()
const { showSuccess, showError, showToast } = useUI()

const text = ref('')
const selectedMode = ref<CorrectionMode>('accuracy')
const maxLength = 5000
const minLength = 10

const charCount = computed(() => text.value.length)
const wordCount = computed(() => {
  return text.value.trim() ? text.value.trim().split(/\s+/).length : 0
})
const remainingChars = computed(() => maxLength - text.value.length)
const isTooLong = computed(() => text.value.length > maxLength)
const isTooShort = computed(() => text.value.trim().length > 0 && text.value.trim().length < minLength)
const canAnalyze = computed(() => {
  return !isAnalyzing.value &&
         text.value.trim().length >= minLength &&
         text.value.length <= maxLength &&
         !isTooLong.value
})

const progressPercentage = computed(() => progress.value)

watch(text, (newValue) => {
  if (newValue.length > maxLength) {
    text.value = newValue.slice(0, maxLength)
    showToast('Text exceeds maximum length of 5000 characters', 'warning')
  }
})

async function handleAnalyze() {
  if (!text.value.trim()) {
    showError('Please enter some text to analyze')
    return
  }

  if (text.value.trim().length < minLength) {
    showError(`Please enter at least ${minLength} characters`)
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

function handlePaste(event: ClipboardEvent) {
  event.preventDefault()
  const paste = event.clipboardData?.getData('text')
  if (paste) {
    const newText = text.value + paste
    if (newText.length <= maxLength) {
      text.value = newText
    } else {
      text.value = newText.slice(0, maxLength)
    }
  }
}

const modeDescriptions = {
  accuracy: 'Fix grammatical, spelling, and tense errors while preserving style',
  natural: 'Improve naturalness and flow of the text'
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Input Text</h2>
      <button
        v-if="text"
        @click="clearText"
        class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
      >
        Clear
      </button>
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">Correction Mode</label>
      <div class="flex gap-2">
        <button
          @click="selectedMode = 'accuracy'"
          class="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
          :class="selectedMode === 'accuracy'
            ? 'bg-primary-600 text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        "
        :title="modeDescriptions.accuracy"
        >
          <div class="flex flex-col items-center">
            <span class="font-semibold">Accuracy</span>
            <span class="text-xs opacity-80">Fix errors first</span>
          </div>
        </button>
        <button
          @click="selectedMode = 'naturalness'"
          class="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
          :class="selectedMode === 'naturalness'
            ? 'bg-primary-600 text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        "
          :title="modeDescriptions.natural"
        >
          <div class="flex flex-col items-center">
            <span class="font-semibold">Naturalness</span>
            <span class="text-xs opacity-80">Improve flow</span>
          </div>
        </button>
      </div>
    </div>

    <div class="flex-1 mb-4">
      <textarea
        v-model="text"
        @paste="handlePaste"
        placeholder="Enter your English text here... (minimum 10 characters)"
        class="w-full h-full min-h-[300px] p-4 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-base leading-relaxed"
        :disabled="isAnalyzing"
        :maxlength="maxLength"
      ></textarea>

      <div class="flex items-center justify-between mt-2 text-sm">
        <div class="flex items-center gap-4">
          <span class="text-gray-500">{{ charCount }} chars</span>
          <span class="text-gray-400">|</span>
          <span class="text-gray-500">{{ wordCount }} words</span>
        </div>
        <div
          class="font-medium"
          :class="{
            'text-red-600': remainingChars < 100,
            'text-yellow-600': remainingChars < 500 && remainingChars >= 100,
            'text-gray-500': remainingChars >= 500
          }"
        >
          {{ remainingChars }} remaining
        </div>
      </div>
    </div>

    <div
      v-if="isAnalyzing"
      class="mb-4"
    >
      <div class="flex items-center justify-center py-3 bg-gray-50 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm text-gray-700">Analyzing...</span>
        </div>
      </div>

      <div class="mt-3">
        <div class="flex justify-between text-xs text-gray-500 mb-1">
          <span>Progress</span>
          <span>{{ progressPercentage }}%</span>
        </div>
        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            class="h-full bg-primary-600 transition-all duration-300 ease-out"
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <button
      @click="handleAnalyze"
      :disabled="!canAnalyze"
      class="w-full py-3 px-6 bg-primary-600 text-white rounded-lg font-semibold text-base transition-all duration-200"
      :class="{
        'opacity-50 cursor-not-allowed': !canAnalyze,
        'hover:bg-primary-700 hover:shadow-lg': canAnalyze,
        'disabled:bg-gray-300': isAnalyzing
      }"
    >
      <span v-if="isAnalyzing" class="flex items-center justify-center gap-2">
        <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        Analyzing...
      </span>
      <span v-else class="flex items-center justify-center gap-2">
        <span>🔍</span>
        Analyze Text
      </span>
    </button>

    <div v-if="error" class="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
      <div class="flex items-start gap-2">
        <span class="text-red-600 text-lg">⚠️</span>
        <div class="flex-1">
          <p class="text-sm font-medium text-red-800">Analysis Error</p>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <div v-if="isTooLong && !isAnalyzing" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div class="flex items-center gap-2">
        <span class="text-yellow-600">⚠️</span>
        <p class="text-sm text-yellow-800">
          Text exceeds maximum length ({{ maxLength }} characters). Please shorten it.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 0.8s linear infinite;
}
</style>
