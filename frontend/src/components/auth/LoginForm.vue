<script setup lang="ts">
import { ref } from 'vue'
import { getValidationErrorMessage } from '@/utils/validators'

// TODO: Implement login form
interface LoginData {
  email: string
  password: string
}

const emit = defineEmits<{
  submit: [data: LoginData]
}>()

const email = ref('')
const password = ref('')
const errors = ref<{ email?: string; password?: string }>({})
const isLoading = ref(false)

function validate() {
  errors.value = {}

  const emailError = getValidationErrorMessage('email', email.value)
  if (emailError) errors.value.email = emailError

  const passwordError = getValidationErrorMessage('password', password.value)
  if (passwordError) errors.value.password = passwordError

  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validate()) return

  isLoading.value = true
  try {
    emit('submit', {
      email: email.value,
      password: password.value,
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <!-- Email -->
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        :class="errors.email ? 'border-red-300' : 'border-gray-300'"
        placeholder="your@email.com"
      />
      <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
    </div>

    <!-- Password -->
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
      <input
        id="password"
        v-model="password"
        type="password"
        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        :class="errors.password ? 'border-red-300' : 'border-gray-300'"
        placeholder="••••••••"
      />
      <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
    </div>

    <!-- Submit button -->
    <button
      type="submit"
      :disabled="isLoading"
      class="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
    >
      {{ isLoading ? 'Logging in...' : 'Login' }}
    </button>
  </form>
</template>
