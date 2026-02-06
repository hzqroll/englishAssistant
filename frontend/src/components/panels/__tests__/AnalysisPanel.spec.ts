import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnalysisPanel from '../AnalysisPanel.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAnalysisStore } from '@/stores/analysisStore'
import { storeToRefs } from 'pinia'

// Mock composables
vi.mock('@/composables/useAnalysis', () => ({
  useAnalysis: () => {
    const store = useAnalysisStore()
    const { currentResult, isAnalyzing } = storeToRefs(store)
    return {
      currentResult,
      isAnalyzing
    }
  }
}))

describe('AnalysisPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders empty state when no result', () => {
    const wrapper = mount(AnalysisPanel, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              currentResult: null,
              isAnalyzing: false
            }
          }
        })]
      }
    })

    expect(wrapper.text()).toContain('暂无分析结果')
  })

  it('renders error categories when result exists', async () => {
    const mockErrors = [
      { type: 'grammar', message: 'Grammar error', originalText: 'bad', correctedText: 'good' },
      { type: 'spelling', message: 'Spelling error', originalText: 'speling', correctedText: 'spelling' }
    ]

    const wrapper = mount(AnalysisPanel, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              currentResult: {
                id: '1',
                errors: mockErrors
              },
              isAnalyzing: false
            }
          }
        })]
      }
    })

    expect(wrapper.text()).toContain('语法错误')
    expect(wrapper.text()).toContain('拼写错误')
    // Check counts
    expect(wrapper.text()).toContain('1') // 1 grammar, 1 spelling

    // Note: AnalysisPanel renders errors directly, no expand button logic in the version I read?
    // Let's check the content of AnalysisPanel.vue again.
    // It has `v-for="category in errorCategories"`
    // It has `v-for="(error, index) in category.errors.slice(0, 3)"`
    // So errors are always visible (up to 3).
    
    expect(wrapper.text()).toContain('Grammar error')
    expect(wrapper.text()).toContain('bad')
  })

  it('accepts search input', async () => {
    const wrapper = mount(AnalysisPanel, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              currentResult: {
                id: '1',
                errors: []
              },
              isAnalyzing: false
            }
          }
        })]
      }
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('test')
    expect(input.element.value).toBe('test')
  })
})
