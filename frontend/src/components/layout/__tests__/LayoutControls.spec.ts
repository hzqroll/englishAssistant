import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import LayoutControls from '../LayoutControls.vue'
import { createTestingPinia } from '@pinia/testing'
import { useUIStore } from '@/stores/uiStore'

// Mock composables
vi.mock('@/composables/useUI', () => ({
  useUI: () => {
    const store = useUIStore()
    return {
      panels: store.panels,
      togglePanel: store.togglePanel
    }
  }
}))

describe('LayoutControls', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders panel toggle buttons correctly', () => {
    const wrapper = mount(LayoutControls, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            ui: {
              panels: {
                input: true,
                compare: false,
                analysis: true
              }
            }
          }
        })]
      }
    })

    const buttons = wrapper.findAll('button')
    // Expect 3 buttons: Input, Compare, Analysis
    expect(buttons).toHaveLength(3)

    // Check Input button (active)
    expect(buttons[0].text()).toBe('Input')
    expect(buttons[0].classes()).toContain('bg-primary-100')

    // Check Compare button (inactive)
    expect(buttons[1].text()).toBe('Compare')
    expect(buttons[1].classes()).toContain('bg-gray-100')

    // Check Analysis button (active)
    expect(buttons[2].text()).toBe('Analysis')
    expect(buttons[2].classes()).toContain('bg-primary-100')
  })

  it('toggles panels on click', async () => {
    const wrapper = mount(LayoutControls, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            ui: {
              panels: {
                input: true,
                compare: false,
                analysis: true
              }
            }
          }
        })]
      }
    })

    const store = useUIStore()
    const buttons = wrapper.findAll('button')

    // Click Input
    await buttons[0].trigger('click')
    expect(store.togglePanel).toHaveBeenCalledWith('input')

    // Click Compare
    await buttons[1].trigger('click')
    expect(store.togglePanel).toHaveBeenCalledWith('compare')
  })
})
