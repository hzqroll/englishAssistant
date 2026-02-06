// Types for split analysis feature
export interface RuleBasedResult {
  analysisId: string
  originalText: string
  correctedText: string
  mode: string
  status: string
  errors: GrammarError[]
  warnings: GrammarWarning[]
  statistics: Record<string, any>
  processingTimeMs: number
  stageTimes: Record<string, number>
  createdAt: string
}

export interface LLMResult {
  analysisId: string
  originalText: string
  correctedText: string
  mode: string
  status: string
  tokenUsage: TokenUsage
  statistics: Record<string, any>
  processingTimeMs: number
  stageTimes: Record<string, number>
  createdAt: string
  learningAnalysis?: LearningAnalysis
}

export interface GrammarError {
  id: string
  type: string
  subtype?: string
  original: string
  suggestion: string
  message: string
  startIndex: number
  endIndex: number
  severity: 'error' | 'warning'
  ruleId?: string
  category?: string
  context?: string
}

export interface GrammarWarning {
  id: string
  type: string
  original: string
  suggestion: string
  message: string
  startIndex: number
  endIndex: number
  severity: 'warning'
}

export interface TokenUsage {
  totalTokens: number
  promptTokens: number
  completionTokens: number
  estimatedCost: number
}

export interface LearningAnalysis {
  errorPatterns: ErrorPattern[]
  recommendations: LearningRecommendation[]
  tips: string[]
}

export interface ErrorPattern {
  patternName: string
  description: string
  frequency?: string
  examples?: Array<{
    incorrect: string
    correct: string
  }>
  severity?: 'high' | 'medium' | 'low'
}

export interface LearningRecommendation {
  priority: number
  topic: string
  description: string
  resources?: Array<{
    type: string
    title: string
    content: string
  }>
  estimatedStudyTime?: string
}

// API Request/Response types
export interface RulesOnlyRequest {
  text: string
  mode: string
  language?: string
}

export interface RulesOnlyResponse {
  success: boolean
  data: RuleBasedResult
  message?: string
}

export interface OptimizeLLMRequest {
  analysisId: string
}

export interface OptimizeLLMResponse {
  success: boolean
  data: LLMResult
  message?: string
}