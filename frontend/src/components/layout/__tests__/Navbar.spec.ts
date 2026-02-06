import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Navbar from '../Navbar.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

// Mock composables
vi.mock('@/composables/useAuth', () => ({
  useAuth: () => {
    const store = useAuthStore()
    return {
      isAuthenticated: store.isAuthenticated,
      user: store.user,
      logout: store.logout
    }
  }
}))

vi.mock('@/composables', () => ({
  useUI: () => ({
    isDarkMode: false
  })
}))

// Mock router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(),
  RouterLink: {
    template: '<a><slot /></a>'
  }
}))

describe('Navbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Setup default router mock
    vi.mocked(useRouter).mockReturnValue({
      push: vi.fn()
    } as any)
  })

  it('renders login button when not authenticated', () => {
    const wrapper = mount(Navbar, {
      global: {
        plugins: [createTestingPinia({
          initialState: {
            auth: { accessToken: null, user: null }
          },
          stubActions: false
        })]
      }
    })

    expect(wrapper.text()).toContain('登录')
    expect(wrapper.text()).not.toContain('登出')
  })

  it('renders user info and logout when authenticated', async () => {
    const wrapper = mount(Navbar, {
      global: {
        plugins: [createTestingPinia({
          initialState: {
            auth: { 
              accessToken: 'token', 
              user: { username: 'TestUser' }
            }
          },
          stubActions: false
        })]
      }
    })

    expect(wrapper.text()).toContain('TestUser')
    expect(wrapper.text()).toContain('登出')
    
    // Test logout action
    const logoutBtn = wrapper.findAll('button').find(b => b.text().includes('登出'))
    await logoutBtn?.trigger('click')
    
    const store = useAuthStore()
    expect(store.logout).toHaveBeenCalled()
  })
})
