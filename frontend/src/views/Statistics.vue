<script setup lang="ts">
import { onMounted } from 'vue'
import { useUI } from '@/composables/useUI'
import Navbar from '@/components/layout/Navbar.vue'

// TODO: Implement statistics page with charts and trends
const { loadDarkModePreference } = useUI()

onMounted(() => {
  loadDarkModePreference()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <main class="container mx-auto px-4 py-6">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Error Statistics</h1>
        <p class="text-gray-600 mt-2">Track your learning progress and error patterns</p>
      </div>

      <!-- TODO: Add overview cards -->
      <!-- TODO: Add error type distribution chart -->
      <!-- TODO: Add error trends over time -->
      <!-- TODO: Add token usage statistics -->
    </main>
  </div>
</template>
