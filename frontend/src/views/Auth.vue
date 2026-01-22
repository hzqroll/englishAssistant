<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import LoginForm from '@/components/auth/LoginForm.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'

// TODO: Implement auth page with login/register tabs
const { login, register } = useAuth()
const isLogin = ref(true)

function toggleMode() {
  isLogin.value = !isLogin.value
}

async function handleLogin(data: { email: string; password: string }) {
  await login(data.email, data.password)
}

async function handleRegister(data: { email: string; password: string; username: string }) {
  await register(data.email, data.password, data.username)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">English Transfer Assistant</h1>
        <p class="text-gray-600 mt-2">{{ isLogin ? 'Sign in to your account' : 'Create a new account' }}</p>
      </div>

      <!-- Login/Register tabs -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex mb-6">
          <button
            @click="toggleMode"
            class="flex-1 py-2 text-center border-b-2 transition-colors"
            :class="isLogin ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600'"
          >
            Login
          </button>
          <button
            @click="toggleMode"
            class="flex-1 py-2 text-center border-b-2 transition-colors"
            :class="!isLogin ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600'"
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
