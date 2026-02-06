<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ErrorDetail } from '@/stores/types'

interface Props {
  originalText: string
  correctedText: string
  errors: ErrorDetail[]
  viewMode: 'side-by-side' | 'original-only' | 'corrected-only'
  selectedErrorId?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedErrorId: null
})

const emit = defineEmits<{
  errorClick: [error: ErrorDetail]
  errorHover: [error: ErrorDetail | null]
}>()

const hoveredErrorId = ref<string | null>(null)

const severityColors = {
  low: 'bg-blue-200',
  medium: 'bg-yellow-200',
  high: 'bg-red-200'
}

const severityBorders = {
  low: 'border-blue-400 border-l-4',
  medium: 'border-yellow-400 border-l-4',
  high: 'border-red-400 border-l-4'
}

const highlightedOriginal = computed(() => {
  return applyHighlights(props.originalText, props.errors, true)
})

const highlightedCorrected = computed(() => {
  return applyHighlights(props.originalText, props.errors, false)
})

function applyHighlights(
  text: string,
  errors: ErrorDetail[],
  isOriginal: boolean
): string {
  if (!text) return ''
  if (!errors || errors.length === 0) return text

  const sortedErrors = [...errors].sort((a, b) =>
    a.startPosition - b.startPosition
  )

  let result = ''
  let lastIndex = 0

  sortedErrors.forEach(error => {
    const startPos = error.startPosition
    const endPos = error.endPosition

    if (startPos >= lastIndex && endPos <= text.length) {
      result += text.slice(lastIndex, startPos)

      const spanText = isOriginal ? error.originalText : error.correctedText
      const isSelected = props.selectedErrorId === error.id
      const isHovered = hoveredErrorId.value === error.id

      const errorClass = [
        severityColors[error.severity],
        severityBorders[error.severity],
        isSelected ? 'ring-2 ring-primary-500' : '',
        isHovered ? 'ring-2 ring-primary-300' : ''
      ].join(' ')

      result += `<span
        class="cursor-pointer rounded px-1 transition-all duration-150 ${errorClass}"
        data-error-id="${error.id}"
        style="text-decoration: ${isOriginal ? 'line-through' : 'none'}; opacity: ${isOriginal ? '0.7' : '1'};"
      >${spanText}</span>`

      lastIndex = endPos
    }
  })

  result += text.slice(lastIndex)
  return result
}

function handleContainerClick(event: MouseEvent) {
  const target = event.target as HTMLElement
  const errorId = target.getAttribute('data-error-id')
  if (errorId) {
    handleErrorClick(errorId)
  }
}

function handleContainerHover(event: MouseEvent) {
  const target = event.target as HTMLElement
  const errorId = target.getAttribute('data-error-id')
  
  if (errorId) {
    if (hoveredErrorId.value !== errorId) {
      const error = props.errors.find(e => e.id === errorId)
      if (error) {
        emit('errorHover', error)
        hoveredErrorId.value = errorId
      }
    }
  } else if (hoveredErrorId.value) {
    emit('errorHover', null)
    hoveredErrorId.value = null
  }
}

function handleErrorClick(errorId: string) {
  const error = props.errors.find(e => e.id === errorId)
  if (error) {
    emit('errorClick', error)
  }
}

function handleErrorHover(errorId: string | null) {
  const error = errorId
    ? props.errors.find(e => e.id === errorId)
    : null
  
  // Only emit if error exists or we are clearing it (errorId is null)
  if (error || errorId === null) {
    emit('errorHover', error || null)
    hoveredErrorId.value = errorId
  }
}

function scrollToError(errorId: string) {
  const element = document.querySelector(`[data-error-id="${errorId}"]`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

defineExpose({
  scrollToError
})

watch(() => props.selectedErrorId, (newId) => {
  if (newId) {
    setTimeout(() => scrollToError(newId), 100)
  }
})
</script>

<template>
  <div class="flex-1 flex flex-col gap-4">
    <div
      v-if="viewMode === 'side-by-side' || viewMode === 'original-only'"
      class="flex-1"
    >
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xs font-semibold uppercase text-gray-600">Original</span>
        <span class="text-xs text-gray-400">{{ originalText.length }} chars</span>
      </div>
      <div
        class="flex-1 min-h-[200px] p-4 bg-gray-50 rounded-lg border-2 border-gray-200 overflow-auto whitespace-pre-wrap text-gray-900"
        v-html="highlightedOriginal"
        @click="handleContainerClick"
        @mouseover="handleContainerHover"
        @mouseleave="handleErrorHover(null)"
      />
    </div>

    <div
      v-if="viewMode === 'side-by-side' || viewMode === 'corrected-only'"
      class="flex-1"
    >
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xs font-semibold uppercase text-gray-600">Corrected</span>
        <span class="text-xs text-gray-400">{{ correctedText.length }} chars</span>
      </div>
      <div
        class="flex-1 min-h-[200px] p-4 bg-green-50 rounded-lg border-2 border-green-200 overflow-auto whitespace-pre-wrap text-gray-900"
        v-html="highlightedCorrected"
        @click="handleContainerClick"
        @mouseover="handleContainerHover"
        @mouseleave="handleErrorHover(null)"
      />
    </div>

    <div v-if="errors.length === 0" class="flex items-center justify-center p-8 text-center text-gray-400">
      <div>
        <div class="text-4xl mb-4">✨</div>
        <p class="text-lg font-medium">No errors found!</p>
        <p class="text-sm mt-2">Your text looks great.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep([data-error-id]) {
  transition: all 0.15s ease;
}

:deep([data-error-id]:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep([data-error-id].ring-2) {
  z-index: 10;
}
</style>
