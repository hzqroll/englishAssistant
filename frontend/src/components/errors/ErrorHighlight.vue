<script setup lang="ts">
import type { ErrorDetail } from '@/stores/types'

// TODO: Implement error highlight component for inline error display
interface Props {
  text: string
  errors: ErrorDetail[]
}

defineProps<Props>()
</script>

<template>
  <div class="whitespace-pre-wrap">
    <!-- TODO: Implement error highlighting in text -->
    <p>{{ text }}</p>

    <!--
      Idea: Split text by error positions and wrap error portions in styled spans
      Example:
      <span class="bg-red-100 line-through">{{ error.originalText }}</span>
      <span class="bg-green-100">{{ error.correctedText }}</span>
    -->
  </div>
</template>
