import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AuthState, User } from './types'
import { authApi } from '@/api/auth'
// TODO: Import token refresh utilities

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken_val = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const authState = computed<AuthState>(() => ({
    user: user.value,
    accessToken: accessToken.value,
    refreshToken: refreshToken_val.value,
    isAuthenticated: isAuthenticated.value,
    isLoading: isLoading.value,
    error: error.value,
  }))

  // Actions
  async function login(email: string, password: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.login({ email, password })
      accessToken.value = response.data.access_token
      refreshToken_val.value = response.data.refresh_token
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      // Set user data from response
      user.value = {
        id: response.data.user_id,
        email: response.data.email,
        tier: response.data.tier,
        createdAt: new Date().toISOString(),
      }

      // Fetch full user profile
      await fetchUserProfile()
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function register(email: string, password: string, username?: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.register({ email, password, username: username || email.split('@')[0] })

      // Set tokens from registration response
      accessToken.value = response.data.access_token
      refreshToken_val.value = response.data.refresh_token
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      // Set user data
      user.value = {
        id: response.data.user_id,
        email: response.data.email,
        tier: response.data.tier,
        createdAt: new Date().toISOString(),
      }

      // Fetch full user profile
      await fetchUserProfile()
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    user.value = null
    accessToken.value = null
    refreshToken_val.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    error.value = null
  }

  async function fetchUserProfile() {
    if (!accessToken.value) return

    try {
      const response = await authApi.me()
      user.value = {
        id: response.data.id,
        email: response.data.email,
        tier: response.data.tier,
        createdAt: response.data.created_at,
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Failed to fetch user profile'
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken_val.value) {
      await logout()
      throw new Error('No refresh token available')
    }

    try {
      const response = await authApi.refresh({ refresh_token: refreshToken_val.value })
      accessToken.value = response.data.access_token
      refreshToken_val.value = response.data.refresh_token
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
    } catch (err) {
      await logout()
      throw err
    }
  }

  return {
    user,
    accessToken,
    refreshToken: refreshToken_val,
    isLoading,
    error,
    isAuthenticated,
    authState,
    login,
    register,
    logout,
    fetchUserProfile,
    refreshAccessToken,
  }
})
