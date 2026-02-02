import { computed } from 'vue'
import { useAuthStore } from '@/stores'
import { useRouter } from 'vue-router'

/**
 * Authentication composable
 * Provides authentication utilities and helpers
 */
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()

  // Computed
  const user = computed(() => authStore.user)
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const isLoading = computed(() => authStore.isLoading)
  const error = computed(() => authStore.error)
  const userTier = computed(() => authStore.user?.tier || 'free')

  // Actions
  async function login(email: string, password: string) {
    await authStore.login(email, password)
    // TODO: Redirect to intended page or home
    router.push({ name: 'Home' })
  }

  async function register(email: string, password: string, username: string) {
    await authStore.register(email, password, username)
    router.push({ name: 'Home' })
  }

  async function logout() {
    await authStore.logout()
    router.push({ name: 'Home' })
  }

  async function refreshProfile() {
    await authStore.fetchUserProfile()
  }

  // Permissions
  const canAccessHistory = computed(() => isAuthenticated.value)
  const canAccessStatistics = computed(() => isAuthenticated.value)
  const canAccessSettings = computed(() => isAuthenticated.value)

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    userTier,
    login,
    register,
    logout,
    refreshProfile,
    canAccessHistory,
    canAccessStatistics,
    canAccessSettings,
  }
}
