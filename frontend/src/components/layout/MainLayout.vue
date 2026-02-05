<script setup lang="ts">
import { useUI } from '@/composables/useUI'
import InputPanel from '@/components/panels/InputPanel.vue'
import RuleEnginePanel from '@/components/panels/RuleEnginePanel.vue'
import LLMPanel from '@/components/panels/LLMPanel.vue'
import AIOptimizeButton from '@/components/panels/AIOptimizeButton.vue'

const { panels } = useUI()
</script>

<template>
  <div class="relative grid grid-cols-1 lg:grid-cols-10 gap-6">
    <!-- Input Panel (30%) -->
    <div
      v-if="panels.input"
      class="lg:col-span-3"
    >
      <InputPanel />
    </div>

    <!-- Rule Engine Panel - LanguageTool (35%) -->
    <div
      v-if="panels.compare || panels.analysis"
      class="lg:col-span-3.5 relative"
    >
      <RuleEnginePanel />
    </div>

    <!-- LLM Panel - AI Optimization (35%) -->
    <div
      v-if="panels.analysis"
      class="lg:col-span-3.5 relative"
    >
      <LLMPanel />
    </div>

    <!-- Floating AI Optimize Button -->
    <AIOptimizeButton
      v-if="panels.input && panels.compare && panels.analysis"
      class="absolute left-1/2 top-1/2"
    />
  </div>
</template>
