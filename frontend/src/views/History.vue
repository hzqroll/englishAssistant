<script setup lang="ts">
import { onMounted } from 'vue'
import { useHistory, useUI } from '@/composables'
import Navbar from '@/components/layout/Navbar.vue'

// TODO: Implement history page with pagination and filters
const { fetchHistory } = useHistory()
const { loadDarkModePreference } = useUI()

onMounted(() => {
  loadDarkModePreference()
  fetchHistory()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <main class="container mx-auto px-4 py-6">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Analysis History</h1>
        <p class="text-gray-600 mt-2">View and manage your past analyses</p>
      </div>

      <!-- TODO: Add filters -->
      <!-- TODO: Add history list -->
      <!-- TODO: Add pagination -->
    </main>
  </div>
</template>
