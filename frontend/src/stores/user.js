import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin || false
  },

  actions: {
    async login(credentials) {
      try {
        const response = await api.post('/auth/login', credentials)
        this.token = response.data.access_token
        this.user = response.data.user
        
        // 处理记住我功能
        if (credentials.remember) {
          localStorage.setItem('token', response.data.access_token)
          localStorage.setItem('rememberedEmail', credentials.email)
        } else {
          localStorage.setItem('token', response.data.access_token)
          localStorage.removeItem('rememberedEmail')
        }
        
        return response.data
      } catch (error) {
        throw error
      }
    },

    async register(username, email, password) {
      try {
        const response = await api.post('/auth/register', { username, email, password })
        return response.data
      } catch (error) {
        throw error
      }
    },

    async getCurrentUser() {
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
        return response.data
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async forgotPassword(email) {
      try {
        const response = await api.post('/auth/forgot-password', { email })
        return response.data
      } catch (error) {
        throw error
      }
    },

    async resetPassword(email, code, newPassword) {
      try {
        const response = await api.post('/auth/reset-password', {
          email,
          code,
          new_password: newPassword
        })
        return response.data
      } catch (error) {
        throw error
      }
    },

    getRememberedEmail() {
      return localStorage.getItem('rememberedEmail') || ''
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      // 注意:logout时不清除rememberedEmail,保留记住的邮箱
    }
  }
})
