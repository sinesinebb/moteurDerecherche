// stores/history.store.ts
import { defineStore } from 'pinia'
import { useAuthStore } from './auth.store'

export interface HistoryItem {
  id: string
  user: string
  query: string
  filters: any
  total_results: number
  execution_time: number | null
  created_at: string
  results: any[]
}

export const useHistoryStore = defineStore('history', {
  state: () => ({
    items: [] as HistoryItem[],
    loading: false,
    error: null as string | null
  }),

  actions: {
    // Méthode utilitaire sécurisée (refresh auto en cas de 401)
    async _authFetch(url: string, options: any = {}) {
      const authStore = useAuthStore()
      if (!authStore.token) throw new Error('Non authentifié')

      const headers = {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }

      const config = useRuntimeConfig()
      const baseURL = config.public.apiBaseUrl || 'http://localhost'
      const fullUrl = url.startsWith('http') ? url : `${baseURL}${url}`

      try {
        return await $fetch(fullUrl, { ...options, headers })
      } catch (err: any) {
        if (err.status === 401 && authStore.refreshToken) {
          console.warn('🔄 Token expiré, tentative de refresh...')
          const refreshSuccess = await authStore.refreshAuthToken()
          if (refreshSuccess) {
            headers.Authorization = `Bearer ${authStore.token}`
            return await $fetch(fullUrl, { ...options, headers })
          } else {
            await authStore.logout()
            throw new Error('Session expirée')
          }
        }
        throw err
      }
    },

    async fetchHistory() {
      const authStore = useAuthStore()
      if (!authStore.token) {
        console.warn('fetchHistory: token absent')
        return
      }
      this.loading = true
      this.error = null
      try {
        const response = await this._authFetch('/api/history/', { method: 'GET' }) as any
        this.items = Array.isArray(response) ? response : (response.results || [])
        console.log('✅ Historique reçu :', this.items.length, 'entrées')
      } catch (err: any) {
        console.error('❌ Erreur fetchHistory :', err)
        this.error = err.message
      } finally {
        this.loading = false
      }
    },

    async addSearch(query: string, options?: { type?: string; results?: any[] }) {
      const authStore = useAuthStore()
      if (!authStore.token) return
      try {
        const payload = {
          query,
          filters: options?.type ? { type: options.type } : {},
          total_results: options?.results?.length || 0,
          execution_time: 0
        }
        await this._authFetch('/api/history/', {
          method: 'POST',
          body: JSON.stringify(payload)
        })
        await this.fetchHistory()
      } catch (err: any) {
        console.error('Erreur addSearch :', err)
      }
    },

    async removeHistoryItem(id: string) {
      const authStore = useAuthStore()
      if (!authStore.token) return
      try {
        await this._authFetch(`/api/history/${id}/`, { method: 'DELETE' })
        this.items = this.items.filter(item => item.id !== id)
      } catch (err: any) {
        console.error('Erreur removeHistoryItem :', err)
      }
    },

    async clearHistory() {
      const authStore = useAuthStore()
      if (!authStore.token) return
      for (const item of this.items) {
        await this.removeHistoryItem(item.id)
      }
      this.items = []
    }
  }
})