/**
 * Application constants
 */

/**
 * Error types
 */
export const ERROR_TYPES = {
  GRAMMAR: 'grammar',
  TENSE: 'tense',
  WORD_CHOICE: 'word_choice',
  SPELLING: 'spelling',
  STYLE: 'style',
  PUNCTUATION: 'punctuation',
  CHINESE_ENGLISH: 'chinese_english',
  OTHER: 'other',
} as const

export type ErrorType = (typeof ERROR_TYPES)[keyof typeof ERROR_TYPES]

/**
 * Error type display names
 */
export const ERROR_TYPE_LABELS: Record<ErrorType, string> = {
  [ERROR_TYPES.GRAMMAR]: 'Grammar',
  [ERROR_TYPES.TENSE]: 'Tense',
  [ERROR_TYPES.WORD_CHOICE]: 'Word Choice',
  [ERROR_TYPES.SPELLING]: 'Spelling',
  [ERROR_TYPES.STYLE]: 'Style',
  [ERROR_TYPES.PUNCTUATION]: 'Punctuation',
  [ERROR_TYPES.CHINESE_ENGLISH]: 'Chinese-English',
  [ERROR_TYPES.OTHER]: 'Other',
}

/**
 * Severity levels
 */
export const SEVERITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
} as const

export type SeverityLevel = (typeof SEVERITY_LEVELS)[keyof typeof SEVERITY_LEVELS]

/**
 * Severity level colors
 */
export const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  [SEVERITY_LEVELS.LOW]: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  [SEVERITY_LEVELS.MEDIUM]: 'text-orange-600 bg-orange-50 border-orange-200',
  [SEVERITY_LEVELS.HIGH]: 'text-red-600 bg-red-50 border-red-200',
}

/**
 * Correction modes
 */
export const CORRECTION_MODES = {
  ACCURACY: 'accuracy',
  NATURALNESS: 'naturalness',
} as const

export type CorrectionMode = (typeof CORRECTION_MODES)[keyof typeof CORRECTION_MODES]

/**
 * View modes
 */
export const VIEW_MODES = {
  SIDE_BY_SIDE: 'side-by-side',
  ORIGINAL_ONLY: 'original-only',
  CORRECTED_ONLY: 'corrected-only',
} as const

export type ViewMode = (typeof VIEW_MODES)[keyof typeof VIEW_MODES]

/**
 * View mode labels
 */
export const VIEW_MODE_LABELS: Record<ViewMode, string> = {
  [VIEW_MODES.SIDE_BY_SIDE]: 'Side by Side',
  [VIEW_MODES.ORIGINAL_ONLY]: 'Original Only',
  [VIEW_MODES.CORRECTED_ONLY]: 'Corrected Only',
}

/**
 * User tiers
 */
export const USER_TIERS = {
  FREE: 'free',
  PAID: 'paid',
} as const

export type UserTier = (typeof USER_TIERS)[keyof typeof USER_TIERS]

/**
 * Rate limits
 */
export const RATE_LIMITS = {
  ANONYMOUS: { requests: 5, period: 'hour' },
  FREE: { requests: 50, period: 'day' },
  PAID: { requests: 500, period: 'day' },
} as const

/**
 * Pagination defaults
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
} as const

/**
 * Toast durations
 */
export const TOAST_DURATIONS = {
  SHORT: 2000,
  MEDIUM: 3000,
  LONG: 5000,
} as const

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  DARK_MODE: 'dark_mode',
  USER_SETTINGS: 'user_settings',
} as const

/**
 * API status codes
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
} as const
