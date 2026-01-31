import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface User {
  id: string
  username: string
  email: string
  created_at: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Initialize from stored token
  const initAuth = async () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      // Validate token by fetching current user (don't logout on failure - keep localStorage)
      try {
        await fetchCurrentUser()
      } catch {
        // API validation failed, but keep the existing token and user data
        // The user might have network issues or the API might be temporarily unavailable
        console.warn('Auth validation failed, but keeping existing session')
      }
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return

    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      user.value = response.data.data.user
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      // Don't logout on API failure - keep the session alive
      // The user might have network issues or the API might be temporarily unavailable
      console.warn('Failed to fetch current user:', error)
    }
  }

  const login = async (email: string, password: string) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password
      })

      const { user: userData, token: authToken } = response.data.data
      token.value = authToken
      user.value = userData

      localStorage.setItem('token', authToken)
      localStorage.setItem('user', JSON.stringify(userData))

      return { success: true }
    } catch (error: any) {
      error.value = error.response?.data?.message || '登录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (
    username: string,
    email: string,
    password: string,
    confirmPassword: string
  ) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        username,
        email,
        password,
        confirm_password: confirmPassword
      })

      const { user: userData, token: authToken } = response.data.data
      token.value = authToken
      user.value = userData

      localStorage.setItem('token', authToken)
      localStorage.setItem('user', JSON.stringify(userData))

      return { success: true }
    } catch (error: any) {
      error.value = error.response?.data?.message || '注册失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const updateProfile = async (profileData: { username: string; email: string }) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null
    try {
      const response = await axios.put(
        `${API_BASE_URL}/auth/profile`,
        profileData,
        {
          headers: { Authorization: `Bearer ${token.value}` }
        }
      )

      if (response.data.success) {
        user.value = { ...user.value, ...profileData }
        localStorage.setItem('user', JSON.stringify(user.value))
        return true
      }
      error.value = response.data.message || '更新失败'
      return false
    } catch (error: any) {
      error.value = error.response?.data?.detail || '更新失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    if (!token.value) return false

    isLoading.value = true
    error.value = null
    try {
      const response = await axios.put(
        `${API_BASE_URL}/auth/password`,
        {
          current_password: currentPassword,
          new_password: newPassword
        },
        {
          headers: { Authorization: `Bearer ${token.value}` }
        }
      )

      if (response.data.success) {
        return true
      }
      error.value = response.data.message || '密码修改失败'
      return false
    } catch (error: any) {
      error.value = error.response?.data?.detail || '密码修改失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    initAuth,
    login,
    register,
    updateProfile,
    changePassword,
    logout
  }
})
