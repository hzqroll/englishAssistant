<script setup lang="ts">
import { useUI } from '@/composables/useUI'

// TODO: Implement layout preset controls
const { togglePanel, panels } = useUI()
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-900">Layout Controls</h2>

      <div class="flex items-center space-x-2">
        <!-- Panel toggles -->
        <button
          @click="togglePanel('input')"
          class="px-3 py-1 text-sm rounded-md transition-colors"
          :class="panels.input ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'"
        >
          Input
        </button>
        <button
          @click="togglePanel('compare')"
          class="px-3 py-1 text-sm rounded-md transition-colors"
          :class="panels.compare ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'"
        >
          Compare
        </button>
        <button
          @click="togglePanel('analysis')"
          class="px-3 py-1 text-sm rounded-md transition-colors"
          :class="panels.analysis ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'"
        >
          Analysis
        </button>
      </div>
    </div>

    <!-- TODO: Add preset layout buttons (e.g., All, Input + Compare, etc.) -->
  </div>
</template>
