/**
 * Input validation utilities
 */

/**
 * Email validation
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Password validation
 * At least 8 characters, 1 letter, 1 number
 */
export function isValidPassword(password: string): boolean {
  if (password.length < 8) return false

  const hasLetter = /[a-zA-Z]/.test(password)
  const hasNumber = /[0-9]/.test(password)

  return hasLetter && hasNumber
}

/**
 * Username validation
 * 3-20 characters, alphanumeric and underscore only
 */
export function isValidUsername(username: string): boolean {
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
  return usernameRegex.test(username)
}

/**
 * Text input validation for analysis
 * Max 10000 characters
 */
export function isValidAnalysisText(text: string): boolean {
  return text.trim().length > 0 && text.length <= 10000
}

/**
 * Check if text contains only English characters
 */
export function isEnglishText(text: string): boolean {
  // Allow English letters, numbers, common punctuation, and spaces
  const englishRegex = /^[\x00-\x7F\s\d.,!?;:'"()\[\]{}@#$%&*+\-_/|\\<>=~^`]+$/
  return englishRegex.test(text)
}

/**
 * Check if text contains Chinese characters
 */
export function containsChinese(text: string): boolean {
  const chineseRegex = /[\u4e00-\u9fa5]/
  return chineseRegex.test(text)
}

/**
 * Get validation error message
 */
export function getValidationErrorMessage(
  field: 'email' | 'password' | 'username' | 'text',
  value: string
): string | null {
  switch (field) {
    case 'email':
      if (!value) return 'Email is required'
      if (!isValidEmail(value)) return 'Please enter a valid email address'
      break

    case 'password':
      if (!value) return 'Password is required'
      if (!isValidPassword(value)) {
        return 'Password must be at least 8 characters with letters and numbers'
      }
      break

    case 'username':
      if (!value) return 'Username is required'
      if (!isValidUsername(value)) {
        return 'Username must be 3-20 characters (letters, numbers, underscore only)'
      }
      break

    case 'text':
      if (!value.trim()) return 'Text cannot be empty'
      if (value.length > 10000) return 'Text cannot exceed 10000 characters'
      break
  }

  return null
}
