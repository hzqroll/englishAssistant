<script setup lang="ts">
import { onMounted } from 'vue'
import { useUI } from '@/composables/useUI'
import Navbar from '@/components/layout/Navbar.vue'

// TODO: Implement settings page
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
        <h1 class="text-3xl font-bold text-gray-900">Settings</h1>
        <p class="text-gray-600 mt-2">Customize your experience</p>
      </div>

      <!-- TODO: Add correction mode setting -->
      <!-- TODO: Add email notifications setting -->
      <!-- TODO: Add dark mode toggle -->
      <!-- TODO: Add language setting -->
      <!-- TODO: Add account management -->
    </main>
  </div>
</template>
