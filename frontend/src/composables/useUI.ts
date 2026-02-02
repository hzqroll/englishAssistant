import { computed } from 'vue'
import { useUIStore } from '@/stores'
import type { PanelType, ToastMessage } from '@/stores/types'

/**
 * UI composable
 * Provides UI state management utilities
 */
export function useUI() {
  const uiStore = useUIStore()

  // Computed
  const panels = computed(() => uiStore.panels)
  const activePanel = computed(() => uiStore.activePanel)
  const isDarkMode = computed(() => uiStore.isDarkMode)
  const toasts = computed(() => uiStore.toasts)
  const sidebarOpen = computed(() => uiStore.sidebarOpen)

  // Panel actions
  function togglePanel(panel: PanelType) {
    uiStore.togglePanel(panel)
  }

  function setPanelState(panel: PanelType, state: boolean) {
    uiStore.setPanelState(panel, state)
  }

  function setActivePanel(panel: PanelType | null) {
    uiStore.setActivePanel(panel)
  }

  function resetPanels() {
    uiStore.resetPanels()
  }

  // Theme actions
  function toggleDarkMode() {
    uiStore.toggleDarkMode()
  }

  function setDarkMode(enabled: boolean) {
    uiStore.setDarkMode(enabled)
  }

  function loadDarkModePreference() {
    uiStore.loadDarkModePreference()
  }

  // Toast actions
  function showToast(
    message: string,
    type: ToastMessage['type'] = 'info',
    duration = 3000
  ) {
    return uiStore.showToast(message, type, duration)
  }

  function showSuccess(message: string, duration = 3000) {
    return showToast(message, 'success', duration)
  }

  function showError(message: string, duration = 5000) {
    return showToast(message, 'error', duration)
  }

  function showWarning(message: string, duration = 3000) {
    return showToast(message, 'warning', duration)
  }

  function removeToast(id: string) {
    uiStore.removeToast(id)
  }

  function clearToasts() {
    uiStore.clearToasts()
  }

  // Sidebar actions
  function toggleSidebar() {
    uiStore.toggleSidebar()
  }

  function setSidebarState(open: boolean) {
    uiStore.setSidebarState(open)
  }

  return {
    panels,
    activePanel,
    isDarkMode,
    toasts,
    sidebarOpen,
    togglePanel,
    setPanelState,
    setActivePanel,
    resetPanels,
    toggleDarkMode,
    setDarkMode,
    loadDarkModePreference,
    showToast,
    showSuccess,
    showError,
    showWarning,
    removeToast,
    clearToasts,
    toggleSidebar,
    setSidebarState,
  }
}
