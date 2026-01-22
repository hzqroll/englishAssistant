<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useAuth, useUI } from '@/composables'

// TODO: Implement navigation bar with logo, menu, and user info
const { isAuthenticated, user, logout } = useAuth()
const { toggleDarkMode, isDarkMode } = useUI()
</script>

<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center space-x-2">
          <!-- TODO: Add logo icon -->
          <span class="text-xl font-bold text-primary-600">English Transfer</span>
        </RouterLink>

        <!-- Navigation menu -->
        <div class="hidden md:flex items-center space-x-6">
          <RouterLink to="/" class="text-gray-700 hover:text-primary-600">
            Analyze
          </RouterLink>
          <RouterLink v-if="isAuthenticated" to="/history" class="text-gray-700 hover:text-primary-600">
            History
          </RouterLink>
          <RouterLink v-if="isAuthenticated" to="/statistics" class="text-gray-700 hover:text-primary-600">
            Statistics
          </RouterLink>
          <RouterLink v-if="isAuthenticated" to="/settings" class="text-gray-700 hover:text-primary-600">
            Settings
          </RouterLink>
        </div>

        <!-- Right side actions -->
        <div class="flex items-center space-x-4">
          <!-- Dark mode toggle -->
          <button
            @click="toggleDarkMode"
            class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title="Toggle dark mode"
          >
            <!-- TODO: Add sun/moon icon -->
            <span class="text-gray-600">{{ isDarkMode ? '🌙' : '☀️' }}</span>
          </button>

          <!-- User menu or login button -->
          <div v-if="isAuthenticated" class="flex items-center space-x-2">
            <span class="text-gray-700">{{ user?.username }}</span>
            <button
              @click="logout"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Logout
            </button>
          </div>
          <RouterLink
            v-else
            to="/auth"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Login
          </RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>
