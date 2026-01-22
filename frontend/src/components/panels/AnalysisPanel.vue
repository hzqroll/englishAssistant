<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'
import ErrorCard from '@/components/errors/ErrorCard.vue'

// TODO: Implement analysis panel with error cards and learning tips
const { currentResult, learningTips } = useAnalysis()

const hasResult = computed(() => currentResult.value !== null)
const errorCount = computed(() => currentResult.value?.errors.length || 0)
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Analysis Results</h2>
      <span v-if="hasResult" class="text-sm text-gray-600">
        {{ errorCount }} error{{ errorCount !== 1 ? 's' : '' }} found
      </span>
    </div>

    <!-- Empty state -->
    <div v-if="!hasResult" class="flex-1 flex items-center justify-center text-gray-400">
      <div class="text-center">
        <p class="text-lg">No analysis result yet</p>
        <p class="text-sm mt-2">Errors and suggestions will appear here</p>
      </div>
    </div>

    <!-- Error cards -->
    <div v-else class="flex-1 overflow-y-auto space-y-4">
      <!-- Error list -->
      <div class="space-y-3">
        <ErrorCard
          v-for="error in currentResult?.errors"
          :key="error.id"
          :error="error"
        />
      </div>

      <!-- Learning tips -->
      <div v-if="learningTips.length > 0" class="mt-6">
        <h3 class="text-md font-semibold text-gray-900 mb-3">Learning Tips</h3>
        <div class="space-y-2">
          <div
            v-for="(tip, index) in learningTips"
            :key="index"
            class="p-3 bg-blue-50 border border-blue-200 rounded-lg"
          >
            <p class="text-sm text-blue-900">{{ tip }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
