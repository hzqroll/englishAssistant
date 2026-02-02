import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { HistoryState, HistoryItem, HistoryFilters } from './types'
import { historyApi } from '@/api/history'

export const useHistoryStore = defineStore('history', () => {
  // State
  const items = ref<HistoryItem[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<HistoryFilters>({})

  // Computed
  const historyState = computed<HistoryState>(() => ({
    items: items.value,
    total: total.value,
    page: page.value,
    pageSize: pageSize.value,
    isLoading: isLoading.value,
    error: error.value,
    filters: filters.value,
  }))

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // Actions
  async function fetchHistory(pageNum?: number, filtersVal?: HistoryFilters) {
    // TODO: Implement history fetching logic
    isLoading.value = true
    error.value = null

    try {
      const currentPage = pageNum || page.value
      const currentFilters = filtersVal || filters.value

      const response = await historyApi.getList({
        page: currentPage,
        page_size: pageSize.value,
        ...currentFilters,
      })

      items.value = response.data.data.items
      total.value = response.data.data.total
      page.value = currentPage
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch history'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchHistoryDetail(id: string) {
    // TODO: Implement fetch history detail logic
    try {
      const response = await historyApi.getDetail(id)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch history detail'
      throw err
    }
  }

  async function deleteHistoryItem(id: string) {
    // TODO: Implement delete history item logic
    try {
      await historyApi.delete(id)
      // Remove from local state
      items.value = items.value.filter(item => item.id !== id)
      total.value -= 1
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete history item'
      throw err
    }
  }

  function setFilters(newFilters: HistoryFilters) {
    filters.value = newFilters
    page.value = 1 // Reset to first page when filters change
  }

  function clearFilters() {
    filters.value = {}
    page.value = 1
  }

  function nextPage() {
    if (page.value < totalPages.value) {
      fetchHistory(page.value + 1)
    }
  }

  function prevPage() {
    if (page.value > 1) {
      fetchHistory(page.value - 1)
    }
  }

  return {
    items,
    total,
    page,
    pageSize,
    isLoading,
    error,
    filters,
    historyState,
    totalPages,
    fetchHistory,
    fetchHistoryDetail,
    deleteHistoryItem,
    setFilters,
    clearFilters,
    nextPage,
    prevPage,
  }
})
