import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../authStore'
import { authApi } from '@/api/auth'

vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
    refresh: vi.fn()
  }
}))

describe('authStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('handles login successfully', async () => {
    const store = useAuthStore()
    
    // Mock login response
    vi.mocked(authApi.login).mockResolvedValue({
      data: {
        access_token: 'acc_token',
        refresh_token: 'ref_token',
        user_id: '123',
        email: 'test@test.com',
        tier: 'free'
      }
    })

    // Mock me response
    vi.mocked(authApi.me).mockResolvedValue({
      data: {
        id: '123',
        email: 'test@test.com',
        tier: 'free',
        created_at: '2024-01-01'
      }
    })

    await store.login('test@test.com', 'pass')

    expect(store.isAuthenticated).toBe(true)
    expect(store.accessToken).toBe('acc_token')
    expect(store.user).toEqual({
      id: '123',
      email: 'test@test.com',
      tier: 'free',
      createdAt: '2024-01-01'
    })
    expect(localStorage.getItem('access_token')).toBe('acc_token')
  })

  it('handles logout', async () => {
    const store = useAuthStore()
    store.accessToken = 'token'
    store.user = { id: '1', email: 'test', tier: 'free', createdAt: '' }
    localStorage.setItem('access_token', 'token')

    await store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.accessToken).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})
