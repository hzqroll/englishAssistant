<script setup lang="ts">
// TODO: Implement error display component
interface Props {
  error: string | null
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: 'Error',
})
</script>

<template>
  <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
    <div class="flex items-start">
      <span class="text-red-600 mr-2">✕</span>
      <div class="flex-1">
        <h3 class="text-sm font-semibold text-red-900">{{ title }}</h3>
        <p class="text-sm text-red-700 mt-1">{{ error }}</p>
      </div>
    </div>
  </div>
</template>
