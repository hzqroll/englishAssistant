<script setup lang="ts">
import { ref } from 'vue'
import type { ErrorDetail } from '@/stores/types'
import { SEVERITY_COLORS, ERROR_TYPE_LABELS } from '@/utils/constants'

// TODO: Implement error card with expand/collapse
interface Props {
  error: ErrorDetail
}

const props = defineProps<Props>()
const isExpanded = ref(false)

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div
    class="border rounded-lg overflow-hidden transition-all duration-200"
    :class="SEVERITY_COLORS[error.severity]"
  >
    <!-- Card header -->
    <div
      class="p-4 cursor-pointer hover:bg-opacity-80"
      @click="toggleExpanded"
    >
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-2 mb-1">
            <span class="text-xs font-semibold uppercase">{{ ERROR_TYPE_LABELS[error.type as keyof typeof ERROR_TYPE_LABELS] }}</span>
            <span class="text-xs">•</span>
            <span class="text-xs capitalize">{{ error.severity }} severity</span>
          </div>

          <div class="flex items-center space-x-2">
            <span class="line-through text-red-600">{{ error.originalText }}</span>
            <span>→</span>
            <span class="text-green-600 font-medium">{{ error.correctedText }}</span>
          </div>
        </div>

        <button class="ml-2 text-gray-500 hover:text-gray-700">
          <span class="transform transition-transform" :class="{ 'rotate-180': isExpanded }">
            ▼
          </span>
        </button>
      </div>
    </div>

    <!-- Expanded content -->
    <div v-if="isExpanded" class="px-4 pb-4 border-t border-current border-opacity-20">
      <p class="text-sm mb-2">{{ error.message }}</p>

      <p v-if="error.suggestion" class="text-sm italic">
        💡 Suggestion: {{ error.suggestion }}
      </p>

      <!-- TODO: Add position info -->
      <!-- TODO: Add copy button -->
      <!-- TODO: Add learn more link -->
    </div>
  </div>
</template>
