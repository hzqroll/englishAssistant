import apiClient from './index'

/**
 * Settings API
 * Handles user settings management
 */

export interface UserSettings {
  default_correction_mode: 'accuracy' | 'naturalness'
  email_notifications: boolean
  dark_mode: boolean
  language: string
}

export const settingsApi = {
  /**
   * Get user settings
   */
  async get() {
    return apiClient.get<{ success: boolean; data: UserSettings }>('/api/v1/settings')
  },

  /**
   * Update user settings
   */
  async update(data: Partial<UserSettings>) {
    return apiClient.put<{ success: boolean; data: UserSettings }>('/api/v1/settings', data)
  },
}
