import { format, formatDistanceToNow, differenceInMinutes, differenceInHours } from 'date-fns'

/**
 * Date formatting utilities
 */

/**
 * Format date to readable string
 */
export function formatDate(date: string | Date, formatStr: string = 'MMM dd, yyyy'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return format(dateObj, formatStr)
}

/**
 * Format date with time
 */
export function formatDateTime(date: string | Date): string {
  return formatDate(date, 'MMM dd, yyyy HH:mm')
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return formatDistanceToNow(dateObj, { addSuffix: true })
}

/**
 * Format date in short format (e.g., "Jan 15")
 */
export function formatShortDate(date: string | Date): string {
  return formatDate(date, 'MMM dd')
}

/**
 * Check if date is today
 */
export function isToday(date: string | Date): boolean {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const today = new Date()
  return (
    dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear()
  )
}

/**
 * Check if date is within last N minutes
 */
export function isWithinMinutes(date: string | Date, minutes: number): boolean {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return differenceInMinutes(new Date(), dateObj) <= minutes
}

/**
 * Check if date is within last N hours
 */
export function isWithinHours(date: string | Date, hours: number): boolean {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return differenceInHours(new Date(), dateObj) <= hours
}

/**
 * Token formatting utilities
 */

/**
 * Format token count with appropriate unit
 */
export function formatTokenCount(count: number): string {
  if (count < 1000) {
    return count.toString()
  } else if (count < 1000000) {
    return `${(count / 1000).toFixed(1)}K`
  } else {
    return `${(count / 1000000).toFixed(1)}M`
  }
}

/**
 * Calculate percentage
 */
export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}
