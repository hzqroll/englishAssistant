import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UIState, PanelState, PanelType, ToastMessage } from './types'

export const useUIStore = defineStore('ui', () => {
  // State
  const panels = ref<PanelState>({
    input: true,
    compare: true,
    analysis: true,
  })
  const activePanel = ref<PanelType | null>(null)
  const isDarkMode = ref(false)
  const toasts = ref<ToastMessage[]>([])
  const sidebarOpen = ref(true)
  const isLoginModalOpen = ref(false)

  // Computed
  const uiState = computed<UIState>(() => ({
    panels: panels.value,
    activePanel: activePanel.value,
    isDarkMode: isDarkMode.value,
    toasts: toasts.value,
    sidebarOpen: sidebarOpen.value,
  }))

  // Modal actions
  function openLoginModal() {
    isLoginModalOpen.value = true
  }

  function closeLoginModal() {
    isLoginModalOpen.value = false
  }

  // Panel actions
  function togglePanel(panel: PanelType) {
    panels.value[panel] = !panels.value[panel]
  }

  function setPanelState(panel: PanelType, state: boolean) {
    panels.value[panel] = state
  }

  function setActivePanel(panel: PanelType | null) {
    activePanel.value = panel
  }

  function resetPanels() {
    panels.value = {
      input: true,
      compare: true,
      analysis: true,
    }
    activePanel.value = null
  }

  // Theme actions
  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value
    // TODO: Apply dark mode class to document
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    // TODO: Save to localStorage
    localStorage.setItem('dark_mode', String(isDarkMode.value))
  }

  function setDarkMode(enabled: boolean) {
    isDarkMode.value = enabled
    if (enabled) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('dark_mode', String(enabled))
  }

  function loadDarkModePreference() {
    // TODO: Load from localStorage
    const saved = localStorage.getItem('dark_mode')
    if (saved !== null) {
      setDarkMode(saved === 'true')
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setDarkMode(prefersDark)
    }
  }

  // Toast actions
  function showToast(message: string, type: ToastMessage['type'] = 'info', duration = 3000) {
    const id = Date.now().toString() + Math.random()
    const toast: ToastMessage = { id, message, type, duration }
    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  function removeToast(id: string) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  function clearToasts() {
    toasts.value = []
  }

  // Sidebar actions
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function setSidebarState(open: boolean) {
    sidebarOpen.value = open
  }

  return {
    panels,
    activePanel,
    isDarkMode,
    toasts,
    sidebarOpen,
    isLoginModalOpen,
    uiState,
    togglePanel,
    setPanelState,
    setActivePanel,
    resetPanels,
    toggleDarkMode,
    setDarkMode,
    loadDarkModePreference,
    showToast,
    removeToast,
    clearToasts,
    toggleSidebar,
    setSidebarState,
    openLoginModal,
    closeLoginModal,
  }
})
