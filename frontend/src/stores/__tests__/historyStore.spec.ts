import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useHistoryStore } from '../historyStore'
import { historyApi } from '@/api/history'

vi.mock('@/api/history', () => ({
  historyApi: {
    getList: vi.fn(),
    getDetail: vi.fn(),
    delete: vi.fn()
  }
}))

describe('historyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches history list and maps data correctly', async () => {
    const store = useHistoryStore()
    
    vi.mocked(historyApi.getList).mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            original_text: 'orig',
            corrected_text: 'corr',
            mode: 'accuracy',
            error_count: 1,
            created_at: 'date'
          }
        ],
        total: 1,
        page: 1,
        page_size: 10
      }
    } as any)

    await store.fetchHistory(1)

    expect(store.items).toHaveLength(1)
    expect(store.items[0]).toEqual({
      id: '1',
      originalText: 'orig',
      correctedText: 'corr',
      mode: 'accuracy',
      errorCount: 1,
      createdAt: 'date'
    })
    expect(store.total).toBe(1)
  })

  it('deletes history item', async () => {
    const store = useHistoryStore()
    store.items = [
      { id: '1', originalText: '', correctedText: '', mode: 'accuracy', errorCount: 0, createdAt: '' },
      { id: '2', originalText: '', correctedText: '', mode: 'accuracy', errorCount: 0, createdAt: '' }
    ]
    store.total = 2

    vi.mocked(historyApi.delete).mockResolvedValue({ data: { success: true } } as any)

    await store.deleteHistoryItem('1')

    expect(store.items).toHaveLength(1)
    expect(store.items[0]!.id).toBe('2')
    expect(store.total).toBe(1)
  })
})
