import { computed } from 'vue'
import { useHistoryStore } from '@/stores'
import type { HistoryFilters } from '@/stores/types'

/**
 * History composable
 * Provides history management utilities
 */
export function useHistory() {
  const historyStore = useHistoryStore()

  // Computed
  const items = computed(() => historyStore.items)
  const total = computed(() => historyStore.total)
  const page = computed(() => historyStore.page)
  const pageSize = computed(() => historyStore.pageSize)
  const totalPages = computed(() => historyStore.totalPages)
  const isLoading = computed(() => historyStore.isLoading)
  const error = computed(() => historyStore.error)
  const filters = computed(() => historyStore.filters)

  // Actions
  async function fetchHistory(pageNum?: number, filtersVal?: HistoryFilters) {
    await historyStore.fetchHistory(pageNum, filtersVal)
  }

  async function fetchHistoryDetail(id: string) {
    return await historyStore.fetchHistoryDetail(id)
  }

  async function deleteHistoryItem(id: string) {
    await historyStore.deleteHistoryItem(id)
  }

  function setFilters(newFilters: HistoryFilters) {
    historyStore.setFilters(newFilters)
  }

  function clearFilters() {
    historyStore.clearFilters()
  }

  function nextPage() {
    historyStore.nextPage()
  }

  function prevPage() {
    historyStore.prevPage()
  }

  function refresh() {
    fetchHistory(page.value, filters.value)
  }

  return {
    items,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    fetchHistory,
    fetchHistoryDetail,
    deleteHistoryItem,
    setFilters,
    clearFilters,
    nextPage,
    prevPage,
    refresh,
  }
}
