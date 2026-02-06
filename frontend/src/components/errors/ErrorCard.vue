<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ErrorDetail } from '@/stores/types'

interface Props {
  error: ErrorDetail
  showPosition?: boolean
  allowCopy?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showPosition: true,
  allowCopy: true
})

const emit = defineEmits<{
  copy: [text: string]
  errorClick: [error: ErrorDetail]
}>()

const isExpanded = ref(false)

const severityColors = {
  low: 'border-blue-300 bg-blue-50 text-blue-800',
  medium: 'border-yellow-300 bg-yellow-50 text-yellow-800',
  high: 'border-red-300 bg-red-50 text-red-800'
}

const severityLabels = {
  low: 'Low',
  medium: 'Medium',
  high: 'High'
}

const errorTypeLabels = {
  grammar: 'Grammar',
  spelling: 'Spelling',
  tense: 'Tense',
  'word_choice': 'Word Choice',
  punctuation: 'Punctuation',
  style: 'Style',
  mixed_language: 'Mixed Language'
}

const errorColorClass = computed(() => severityColors[props.error.severity])
const severityLabel = computed(() => severityLabels[props.error.severity])
const errorTypeLabel = computed(() => {
  const key = props.error.type as keyof typeof errorTypeLabels
  return errorTypeLabels[key] || props.error.type
})

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
}

function handleCopy(text: string) {
  emit('copy', text)
}

function handleErrorClick() {
  emit('errorClick', props.error)
}
</script>

<template>
  <div
    class="rounded-lg overflow-hidden transition-all duration-200 hover:shadow-lg"
    :class="errorColorClass + ' border'"
  >
    <div
      class="p-4 cursor-pointer hover:bg-opacity-80 transition-colors"
      @click="toggleExpanded"
    >
      <div class="flex flex-col gap-2">
        <div class="flex items-center justify-between">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-wider px-2 py-1 rounded-full" :class="errorColorClass">
              {{ errorTypeLabel }}
            </span>
            <span class="text-xs font-semibold px-2 py-1 rounded-full bg-white bg-opacity-50">
              {{ severityLabel }} Severity
            </span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs text-opacity-70" v-if="showPosition">
              Pos: {{ props.error.startPosition }}-{{ props.error.endPosition }}
            </span>
            <button
              class="text-sm hover:scale-110 transition-transform"
              @click.stop="handleErrorClick"
              title="Highlight in text"
            >
              📍
            </button>
          </div>
        </div>

        <div class="flex items-center gap-3 text-base">
          <span class="line-through text-red-600 opacity-70">{{ error.originalText }}</span>
          <span class="text-gray-400">→</span>
          <span class="text-green-700 font-semibold">{{ error.correctedText }}</span>

          <button
            v-if="allowCopy"
            @click.stop="handleCopy(error.correctedText)"
            class="ml-auto text-gray-500 hover:text-gray-700 transition-colors"
            title="Copy corrected text"
          >
            📋
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="isExpanded"
      class="px-4 pb-4 border-t border-current border-opacity-20 bg-white bg-opacity-30"
    >
      <div class="space-y-3">
        <div>
          <h4 class="text-sm font-semibold mb-1">Explanation</h4>
          <p class="text-sm leading-relaxed">{{ error.message }}</p>
        </div>

        <div v-if="error.suggestion">
          <h4 class="text-sm font-semibold mb-1">💡 Suggestion</h4>
          <p class="text-sm italic leading-relaxed">{{ error.suggestion }}</p>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-current border-opacity-20">
          <div class="text-xs text-opacity-70">
            <span class="font-mono">{{ error.type }}</span>
            <span v-if="error.id" class="ml-2">ID: {{ error.id.slice(0, 8) }}</span>
          </div>

          <button
            @click.stop="handleCopy(error.correctedText)"
            class="px-3 py-1 text-xs rounded-md bg-white bg-opacity-50 hover:bg-opacity-80 transition-all"
          >
            Copy Correction
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.line-through) {
  text-decoration-thickness: 2px;
}
</style>
