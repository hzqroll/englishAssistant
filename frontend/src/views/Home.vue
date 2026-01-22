<script setup lang="ts">
import { onMounted } from 'vue'
import { useUI } from '@/composables/useUI'
import Navbar from '@/components/layout/Navbar.vue'
import MainLayout from '@/components/layout/MainLayout.vue'
import LayoutControls from '@/components/layout/LayoutControls.vue'

// TODO: Implement main analysis interface
const { loadDarkModePreference } = useUI()

onMounted(() => {
  loadDarkModePreference()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <main class="container mx-auto px-4 py-6">
      <!-- Layout controls -->
      <LayoutControls class="mb-6" />

      <!-- Main layout with three panels -->
      <MainLayout />
    </main>
  </div>
</template>
