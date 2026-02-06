import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AuthState, User } from './types'
import { authApi, type LoginRequest, type RegisterRequest } from '@/api/auth'

const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const refreshToken_val = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY))
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
  async function login(credentials: LoginRequest) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.login(credentials)
      setTokens(response.data.access_token, response.data.refresh_token)

      // Fetch full user profile
      await fetchUserProfile()
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function register(credentials: RegisterRequest) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.register(credentials)
      setTokens(response.data.access_token, response.data.refresh_token)

      // Fetch full user profile
      await fetchUserProfile()
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken_val.value = refresh
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }

  async function logout() {
    user.value = null
    accessToken.value = null
    refreshToken_val.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    error.value = null
  }

  async function fetchUserProfile() {
    if (!accessToken.value) return

    try {
      const response = await authApi.me()
      const userData = response.data
      user.value = {
        id: userData.id,
        email: userData.email,
        username: userData.email.split('@')[0], // Fallback if backend doesn't return username
        tier: userData.tier,
        createdAt: userData.created_at,
      }
    } catch (err: any) {
      console.error('Fetch profile failed:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch user profile'
      // If unauthorized, log out
      if (err.response?.status === 401) {
        await logout()
      }
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
      localStorage.setItem(TOKEN_KEY, response.data.access_token)
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
