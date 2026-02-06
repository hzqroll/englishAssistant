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

  it('clears text on button click', async () => {
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
    await textarea.setValue('Some text to clear')
    
    // Find clear button (there are two, one in header one in footer)
    // Let's find the footer one which has text "清空"
    const buttons = wrapper.findAll('button')
    const clearBtn = buttons.find(b => b.text().includes('清空'))
    
    expect(clearBtn).toBeDefined()
    await clearBtn?.trigger('click')
    
    expect(textarea.element.value).toBe('')
  })

  it('switches correction mode', async () => {
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

    // Find mode buttons
    const buttons = wrapper.findAll('button')
    const naturalBtn = buttons.find(b => b.text().includes('自然度优先'))
    const accuracyBtn = buttons.find(b => b.text().includes('准确性优先'))

    expect(naturalBtn).toBeDefined()
    expect(accuracyBtn).toBeDefined()

    // Click natural mode
    await naturalBtn?.trigger('click')
    // Check if class changed (it has logic :class="selectedMode === ...")
    // Since we can't easily check component internal state ref without exposing it,
    // we check the visual class change.
    // 'border-blue-500' indicates active.
    
    expect(naturalBtn?.classes()).toContain('border-blue-500')
    expect(accuracyBtn?.classes()).not.toContain('border-blue-500')

    // Click accuracy mode
    await accuracyBtn?.trigger('click')
    expect(accuracyBtn?.classes()).toContain('border-blue-500')
    expect(naturalBtn?.classes()).not.toContain('border-blue-500')
  })
})
