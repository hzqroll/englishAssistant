import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Navbar from '../Navbar.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAuthStore } from '@/stores/authStore'

// Mock router link
const RouterLinkStub = {
  template: '<a><slot /></a>'
}

// Mock composables
vi.mock('@/composables', () => ({
  useAuth: () => {
    const store = useAuthStore()
    return {
      isAuthenticated: store.isAuthenticated,
      user: store.user,
      logout: store.logout
    }
  },
  useUI: () => ({
    isDarkMode: false
  })
}))

describe('Navbar', () => {
  it('renders login button when not authenticated', () => {
    const wrapper = mount(Navbar, {
      global: {
        stubs: { RouterLink: RouterLinkStub },
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
        stubs: { RouterLink: RouterLinkStub },
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
