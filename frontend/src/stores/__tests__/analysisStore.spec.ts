import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAnalysisStore } from '../analysisStore'
import { analysisApi } from '@/api/analysis'

// Mock the API
vi.mock('@/api/analysis', () => ({
  analysisApi: {
    analyze: vi.fn()
  }
}))

describe('analysisStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('correctly maps backend snake_case response to frontend camelCase state', async () => {
    const store = useAnalysisStore()
    
    // Mock API response matching the structure we saw in the logs
    const mockResponse = {
      data: {
        analysis_id: '123',
        original_text: 'what is this',
        corrected_text: 'What is this',
        mode: 'accuracy',
        errors: [
          {
            error_type: 'grammar',
            error_subtype: 'start',
            original_span: 'what',
            corrected_span: 'What',
            start_index: 0,
            end_index: 4,
            explanation: 'Start with capital',
            rule_description: 'Rule 1',
            severity: 'medium'
          }
        ],
        statistics: {},
        processing_time_ms: 100,
        token_usage: {},
        created_at: '2024-01-01T00:00:00Z'
      }
    }

    // @ts-ignore
    vi.mocked(analysisApi.analyze).mockResolvedValue(mockResponse)

    await store.analyzeText('what is this', 'accuracy')

    const result = store.currentResult
    expect(result).toBeTruthy()
    
    // Verify mapping
    expect(result?.id).toBe('123')
    expect(result?.originalText).toBe('what is this')
    expect(result?.correctedText).toBe('What is this')
    expect(result?.mode).toBe('accuracy')
    
    // Verify error mapping
    expect(result?.errors).toHaveLength(1)
    const error = result?.errors[0]
    expect(error?.originalText).toBe('what')
    expect(error?.correctedText).toBe('What')
    expect(error?.startPosition).toBe(0)
    expect(error?.endPosition).toBe(4)
    expect(error?.type).toBe('grammar')
    
    // Verify progress
    expect(store.progress).toBe(100)
    expect(store.isAnalyzing).toBe(false)
  })

  it('handles API errors gracefully', async () => {
    const store = useAnalysisStore()
    
    vi.mocked(analysisApi.analyze).mockRejectedValue({
      response: {
        data: {
          message: 'API Error'
        }
      }
    })

    await expect(store.analyzeText('test', 'accuracy')).rejects.toBeTruthy()
    
    expect(store.error).toBe('API Error')
    expect(store.isAnalyzing).toBe(false)
  })
})
