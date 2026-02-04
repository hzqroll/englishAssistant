<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useUIStore } from '@/stores/uiStore'
import LoginForm from '@/components/auth/LoginForm.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'

const { login, register } = useAuth()
const uiStore = useUIStore()
const isLogin = ref(true)

function toggleMode() {
  isLogin.value = !isLogin.value
}

async function handleLogin(data: { email: string; password: string }) {
  await login(data.email, data.password)
  uiStore.closeLoginModal()
}

async function handleRegister(data: { email: string; password: string; username: string }) {
  await register(data.email, data.password, data.username)
  uiStore.closeLoginModal()
}

function close() {
  uiStore.closeLoginModal()
}
</script>

<template>
  <div v-if="uiStore.isLoginModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="close">
    <div class="relative w-full max-w-md bg-white rounded-lg shadow-xl overflow-hidden">
      <!-- Close button -->
      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="p-8">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ isLogin ? 'Welcome Back' : 'Create Account' }}
          </h2>
          <p class="text-gray-600 mt-2">
            {{ isLogin ? 'Sign in to continue' : 'Join English Transfer Assistant' }}
          </p>
        </div>

        <!-- Login/Register tabs -->
        <div class="flex mb-6 bg-gray-100 p-1 rounded-lg">
          <button
            @click="isLogin = true"
            class="flex-1 py-2 text-sm font-medium rounded-md transition-colors"
            :class="isLogin ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'"
          >
            Login
          </button>
          <button
            @click="isLogin = false"
            class="flex-1 py-2 text-sm font-medium rounded-md transition-colors"
            :class="!isLogin ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'"
          >
            Register
          </button>
        </div>

        <LoginForm v-if="isLogin" @submit="handleLogin" />
        <RegisterForm v-else @submit="handleRegister" />
      </div>
    </div>
  </div>
</template>
