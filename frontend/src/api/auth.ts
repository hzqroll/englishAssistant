import apiClient from './index'

/**
 * Authentication API
 * Handles login, register, token refresh, and user profile
 */

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  username: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export const authApi = {
  /**
   * Login user
   */
  async login(data: LoginRequest) {
    return apiClient.post<AuthResponse>('/api/v1/auth/login', data)
  },

  /**
   * Register new user
   */
  async register(data: RegisterRequest) {
    return apiClient.post<AuthResponse>('/api/v1/auth/register', data)
  },

  /**
   * Refresh access token
   */
  async refresh(data: RefreshTokenRequest) {
    return apiClient.post<{ access_token: string }>('/api/v1/auth/refresh', data)
  },

  /**
   * Get current user profile
   */
  async me() {
    return apiClient.get<{
      id: string
      email: string
      tier: 'free' | 'paid'
      created_at: string
    }>('/api/v1/auth/me')
  },
}
