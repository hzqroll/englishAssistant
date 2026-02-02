/**
 * Authentication State Types
 */
export interface User {
  id: string
  email: string
  username: string
  tier: 'free' | 'paid'
  createdAt: string
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

/**
 * Analysis State Types
 */
export type CorrectionMode = 'accuracy' | 'naturalness'
export type ViewMode = 'side-by-side' | 'original-only' | 'corrected-only'

export interface ErrorDetail {
  id: string
  type: string
  severity: 'low' | 'medium' | 'high'
  originalText: string
  correctedText: string
  message: string
  suggestion?: string
  startPosition: number
  endPosition: number
}

export interface AnalysisResult {
  id: string
  originalText: string
  correctedText: string
  mode: CorrectionMode
  errors: ErrorDetail[]
  learningTips: string[]
  createdAt: string
}

export interface AnalysisState {
  currentResult: AnalysisResult | null
  isAnalyzing: boolean
  mode: CorrectionMode
  viewMode: ViewMode
  error: string | null
  progress: number
}

/**
 * History State Types
 */
export interface HistoryItem {
  id: string
  originalText: string
  correctedText: string
  mode: CorrectionMode
  errorCount: number
  createdAt: string
}

export interface HistoryFilters {
  mode?: CorrectionMode
  dateFrom?: string
  dateTo?: string
  search?: string
}

export interface HistoryState {
  items: HistoryItem[]
  total: number
  page: number
  pageSize: number
  isLoading: boolean
  error: string | null
  filters: HistoryFilters
}

/**
 * UI State Types
 */
export type PanelType = 'input' | 'compare' | 'analysis'

export interface PanelState {
  input: boolean
  compare: boolean
  analysis: boolean
}

export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export interface UIState {
  panels: PanelState
  activePanel: PanelType | null
  isDarkMode: boolean
  toasts: ToastMessage[]
  sidebarOpen: boolean
}
