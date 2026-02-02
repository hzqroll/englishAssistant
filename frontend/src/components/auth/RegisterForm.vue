<script setup lang="ts">
import { ref } from 'vue'
import { getValidationErrorMessage } from '@/utils/validators'

// TODO: Implement register form
interface RegisterData {
  email: string
  password: string
  username: string
}

const emit = defineEmits<{
  submit: [data: RegisterData]
}>()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const username = ref('')
const errors = ref<{ email?: string; password?: string; username?: string; confirmPassword?: string }>({})
const isLoading = ref(false)

function validate() {
  errors.value = {}

  const emailError = getValidationErrorMessage('email', email.value)
  if (emailError) errors.value.email = emailError

  const passwordError = getValidationErrorMessage('password', password.value)
  if (passwordError) errors.value.password = passwordError

  const usernameError = getValidationErrorMessage('username', username.value)
  if (usernameError) errors.value.username = usernameError

  if (password.value !== confirmPassword.value) {
    errors.value.confirmPassword = 'Passwords do not match'
  }

  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validate()) return

  isLoading.value = true
  try {
    emit('submit', {
      email: email.value,
      password: password.value,
      username: username.value,
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <!-- Username -->
    <div>
      <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
      <input
        id="username"
        v-model="username"
        type="text"
        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        :class="errors.username ? 'border-red-300' : 'border-gray-300'"
        placeholder="username"
      />
      <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
    </div>

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

    <!-- Confirm Password -->
    <div>
      <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
      <input
        id="confirmPassword"
        v-model="confirmPassword"
        type="password"
        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        :class="errors.confirmPassword ? 'border-red-300' : 'border-gray-300'"
        placeholder="••••••••"
      />
      <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ errors.confirmPassword }}</p>
    </div>

    <!-- Submit button -->
    <button
      type="submit"
      :disabled="isLoading"
      class="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
    >
      {{ isLoading ? 'Creating account...' : 'Register' }}
    </button>
  </form>
</template>
