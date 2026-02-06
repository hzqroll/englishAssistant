// Authentication types
export interface User {
  id: string
  email: string
  name: string
  credits: number
  avatar?: string
  createdAt?: string
  updatedAt?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  success: boolean
  data: {
    user: User
    token: string
  }
  message?: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface RegisterResponse {
  success: boolean
  data: {
    user: User
    token: string
  }
  message?: string
}