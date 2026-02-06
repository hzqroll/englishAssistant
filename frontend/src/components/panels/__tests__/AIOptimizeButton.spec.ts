import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AIOptimizeButton from '../AIOptimizeButton.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAnalysisStore } from '@/stores/analysisStore'
import { storeToRefs } from 'pinia'

// Mock composables
vi.mock('@/composables/useAnalysis', () => ({
  useAnalysis: () => {
    const store = useAnalysisStore()
    const { ruleResult, llmResult, isOptimizing } = storeToRefs(store)
    return {
      ruleResult,
      llmResult,
      isOptimizing,
      optimizeWithLLM: store.optimizeWithLLM
    }
  }
}))

describe('AIOptimizeButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders disabled state when no rule result', () => {
    const wrapper = mount(AIOptimizeButton, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              ruleResult: null,
              llmResult: null,
              isOptimizing: false
            }
          }
        })]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('等待规则检测完成')
  })

  it('renders enabled state when rule result exists', () => {
    const wrapper = mount(AIOptimizeButton, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              ruleResult: { analysis_id: '123', estimated_llm_tokens: 100 },
              llmResult: null,
              isOptimizing: false
            }
          }
        })]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeUndefined()
    expect(button.text()).toContain('AI 深度优化')
    expect(button.text()).toContain('100 tokens')
  })

  it('triggers optimization on click', async () => {
    const wrapper = mount(AIOptimizeButton, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              ruleResult: { analysis_id: '123', estimated_llm_tokens: 100 },
              llmResult: null,
              isOptimizing: false
            }
          }
        })]
      }
    })

    const store = useAnalysisStore()
    const button = wrapper.find('button')
    await button.trigger('click')
    expect(store.optimizeWithLLM).toHaveBeenCalledWith('123')
  })

  it('renders loading state', () => {
    const wrapper = mount(AIOptimizeButton, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              ruleResult: { analysis_id: '123' },
              llmResult: null,
              isOptimizing: true
            }
          }
        })]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('优化中')
  })

  it('renders completed state', () => {
    const wrapper = mount(AIOptimizeButton, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            analysis: {
              ruleResult: { analysis_id: '123' },
              llmResult: { token_usage: 150 },
              isOptimizing: false
            }
          }
        })]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('优化完成')
    expect(button.text()).toContain('150 tokens')
  })
})
