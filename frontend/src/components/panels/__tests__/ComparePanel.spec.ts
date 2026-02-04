import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ComparePanel from '../ComparePanel.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAnalysisStore } from '@/stores/analysisStore'

import { storeToRefs } from 'pinia'

// Mock composables
vi.mock('@/composables/useAnalysis', () => ({
  useAnalysis: () => {
    const store = useAnalysisStore()
    const { currentResult, viewMode } = storeToRefs(store)
    return {
      currentResult,
      viewMode,
      setViewMode: store.setViewMode
    }
  }
}))

describe('ComparePanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders stats correctly', () => {
    const wrapper = mount(ComparePanel, {
      global: {
        plugins: [createTestingPinia({
          initialState: {
            analysis: {
              currentResult: {
                id: '1',
                originalText: 'test',
                correctedText: 'Test',
                errors: [
                  { type: 'grammar', id: '1', severity: 'medium' },
                  { type: 'spelling', id: '2', severity: 'low' }
                ]
              },
              viewMode: 'side-by-side'
            }
          }
        })]
      }
    })

    // Debug: print text content to see what's rendered
    // console.log(wrapper.text())
    
    // The component renders stats in a v-if="stats" block.
    // stats is computed based on currentResult.
    // If we mocked currentResult correctly, it should render.
    // Maybe the store state injection structure is slightly off or Pinia testing mock isn't reactive as expected in setup.
    // Let's ensure the component can access the store.
    
    expect(wrapper.text()).toContain('语法')
    expect(wrapper.text()).toContain('拼写')
    // Check specific counts if rendered
    // Note: The component renders counts inside stats blocks.
    // Grammar count: 1
    // Spelling count: 1
  })

  it('emits actions', async () => {
    const wrapper = mount(ComparePanel, {
      global: {
        plugins: [createTestingPinia({
          initialState: {
            analysis: {
              currentResult: {
                id: '1',
                originalText: 'test',
                correctedText: 'Test',
                errors: []
              }
            }
          }
        })]
      }
    })

    // Find action buttons
    const buttons = wrapper.findAll('button')
    // Buttons: [TitleBarBack?, ViewMode1, ViewMode2, ViewMode3, Export, Save, Reanalyze]
    // The component has:
    // 1. Back button (optional/header) - Wait, header has a button? "button.p-1"
    // 2. View mode buttons (3)
    // 3. Action buttons (3) at bottom
    
    // Let's find by text content
    const exportBtn = buttons.find(b => b.text().includes('导出'))
    const saveBtn = buttons.find(b => b.text().includes('保存'))
    const reanalyzeBtn = buttons.find(b => b.text().includes('重新分析'))

    await exportBtn?.trigger('click')
    expect(wrapper.emitted('export')).toBeTruthy()

    await saveBtn?.trigger('click')
    expect(wrapper.emitted('save')).toBeTruthy()

    await reanalyzeBtn?.trigger('click')
    expect(wrapper.emitted('reanalyze')).toBeTruthy()
  })
})
