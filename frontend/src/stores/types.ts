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

/**
 * New Split Analysis Types
 */

// LanguageTool Error Types
export interface LTError {
  rule_id: string
  category: string // GRAMMAR, TYPOS, PUNCTUATION, etc.
  severity: string // ERROR, WARNING
  position: { start: number; end: number }
  original_text: string
  replacements: string[]
  message: string
  context: string
}

export interface RuleBasedStatistics {
  total_errors: number
  by_category: Record<string, number>
}

export interface RuleBasedResult {
  analysis_id: string
  errors: LTError[]
  corrected_text: string
  statistics: RuleBasedStatistics
  processing_time_ms: number
  estimated_llm_tokens: number
}

// LLM Optimization Types
export interface LLMSuggestion {
  type: string // naturalness, style_variant, etc.
  sentence_index: number
  original: string
  suggestion: string
  explanation: string
  confidence: number
}

export interface ChineseCorrection {
  original: string
  corrected: string
}

export interface ErrorPattern {
  pattern_name: string
  frequency: string // "43%"
  examples: Array<{ original: string; corrected: string }>
  severity: 'high' | 'medium' | 'low'
}

export interface LearningResource {
  type: string // grammar_rule, practice_exercise
  title: string
  content?: string
  difficulty?: string
}

export interface LearningRecommendation {
  priority: number
  topic: string
  description: string
  resources: LearningResource[]
  estimated_study_time: string
}

export interface HistoricalTrend {
  comparison: 'improving' | 'stable' | 'worsening'
  since_last_week: string
  most_improved: string
  needs_attention: string
}

export interface LearningAnalysis {
  error_patterns: ErrorPattern[]
  learning_recommendations: LearningRecommendation[]
  personalized_tips: string[]
  historical_trend?: HistoricalTrend
}

export interface LLMResult {
  optimized_text: string
  suggestions: LLMSuggestion[]
  chinese_corrections: ChineseCorrection[]
  learning_analysis: LearningAnalysis
  token_usage: number
}

/**
 * Backend API Response Types
 */
export interface ErrorDetailResponse {
  error_type: string
  error_subtype?: string
  original_span: string
  corrected_span: string
  start_index: number
  end_index: number
  explanation?: string
  rule_description?: string
  severity: 'low' | 'medium' | 'high'
}

export interface AnalysisApiResponse {
  analysis_id: string
  original_text: string
  corrected_text: string
  mode: string
  errors: ErrorDetailResponse[]
  statistics: Record<string, any>
  processing_time_ms: number
  token_usage: Record<string, any>
  created_at: string
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
