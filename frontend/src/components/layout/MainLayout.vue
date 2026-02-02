<script setup lang="ts">
import { useUI } from '@/composables/useUI'
import InputPanel from '@/components/panels/InputPanel.vue'
import ComparePanel from '@/components/panels/ComparePanel.vue'
import AnalysisPanel from '@/components/panels/AnalysisPanel.vue'

// TODO: Implement responsive three-panel layout
const { panels } = useUI()
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Input Panel -->
    <div
      v-if="panels.input"
      class="lg:col-span-1"
    >
      <InputPanel />
    </div>

    <!-- Compare Panel -->
    <div
      v-if="panels.compare"
      class="lg:col-span-1"
    >
      <ComparePanel />
    </div>

    <!-- Analysis Panel -->
    <div
      v-if="panels.analysis"
      class="lg:col-span-1"
    >
      <AnalysisPanel />
    </div>
  </div>
</template>
