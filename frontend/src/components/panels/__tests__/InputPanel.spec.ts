import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import InputPanel from '../InputPanel.vue'
import { useAnalysisStore } from '@/stores/analysisStore'

// Mock composables
vi.mock('@/composables', () => ({
  useAnalysis: () => {
    const store = useAnalysisStore()
    return {
      analyzeText: store.analyzeText,
      isAnalyzing: store.isAnalyzing,
      error: store.error,
      progress: store.progress
    }
  },
  useUI: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showToast: vi.fn()
  })
}))

describe('InputPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('validates input length', async () => {
    const wrapper = mount(InputPanel, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: { isAnalyzing: false }
          }
        })]
      }
    })

    const textarea = wrapper.find('textarea')
    const button = wrapper.find('button.w-full') // Analysis button

    // Empty input
    await textarea.setValue('')
    expect(button.attributes('disabled')).toBeDefined()

    // Too short input (< 10 chars)
    await textarea.setValue('Short')
    expect(button.attributes('disabled')).toBeDefined()

    // Valid input
    await textarea.setValue('This is a valid text longer than 10 characters')
    expect(button.attributes('disabled')).toBeUndefined()
  })

  it('disables interactions while analyzing', async () => {
    const wrapper = mount(InputPanel, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: { isAnalyzing: true }
          }
        })]
      }
    })

    const textarea = wrapper.find('textarea')
    const button = wrapper.find('button.w-full')

    expect(textarea.attributes('disabled')).toBeDefined()
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('分析中')
  })
})
