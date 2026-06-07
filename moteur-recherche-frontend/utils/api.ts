// moteur-recherche-frontend/utils/api.ts
import axios from 'axios'

const API_BASE_URL = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:80'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor pour ajouter le token d'authentification
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Services par microservice
export const searchService = {
  async search(query: string, filters: any = {}, page: number = 1, size: number = 20) {
    const response = await api.post('/api/search', {
      query,
      filters,
      page,
      size
    })
    return response.data
  },

  async autocomplete(query: string) {
    const response = await api.get(`/api/search/autocomplete?q=${encodeURIComponent(query)}`)
    return response.data
  },

  async getSearchHistory(userId: string) {
    const response = await api.get(`/api/search/history/${userId}`)
    return response.data
  }
}

export const userService = {
  async login(credentials: { email: string; password: string }) {
    const response = await api.post('/api/auth/login', credentials)
    return response.data
  },

  async register(userData: { email: string; password: string; name: string }) {
    const response = await api.post('/api/auth/register', userData)
    return response.data
  },

  async getProfile() {
    const response = await api.get('/api/user/profile')
    return response.data
  },

  async updateProfile(userData: any) {
    const response = await api.put('/api/user/profile', userData)
    return response.data
  }
}

export const adminService = {
  async getSystemStats() {
    const response = await api.get('/api/admin/stats')
    return response.data
  },

  async getServiceStatus() {
    const response = await api.get('/api/admin/services')
    return response.data
  },

  async restartService(serviceName: string) {
    const response = await api.post(`/api/admin/services/${serviceName}/restart`)
    return response.data
  },

  async getIndexingStatus() {
    const response = await api.get('/api/admin/indexing')
    return response.data
  }
}

export const indexingService = {
  async getStats() {
    const response = await api.get('/api/indexing/stats')
    return response.data
  },

  async triggerIndexing() {
    const response = await api.post('/api/indexing/trigger')
    return response.data
  }
}