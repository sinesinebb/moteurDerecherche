// composables/useSearch.ts
import { ref } from 'vue'

export interface SearchOptions {
  query: string
  page?: number
  limit?: number
  filters?: Record<string, any>
  sort?: string
}

export const useSearch = () => {
  const isLoading = ref(false)
  const results = ref<any[]>([])
  const totalResults = ref(0)
  const searchTime = ref<number | null>(null)
  const error = ref<string | null>(null)

  const performSearch = async (options: SearchOptions) => {
    isLoading.value = true
    error.value = null
    const startTime = Date.now()

    try {
      const config = useRuntimeConfig()
      const response = await $fetch('/api/search', {
        method: 'GET',
        baseURL: config.public.apiBaseUrl,
        params: {
          q: options.query,
          page: options.page || 1,
          limit: options.limit || 20,
          ...options.filters,
          sort: options.sort
        }
      }) as any

      
      results.value = response.results || []
      totalResults.value = response.total || 0
      searchTime.value = Date.now() - startTime
      
      // Sauvegarder dans l'historique
      saveToHistory(options.query)
      
      return { success: true, data: response }
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la recherche'
      console.error('Search error:', err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const saveToHistory = (query: string) => {
    if (typeof window === 'undefined') return
    
    const history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
    
    // Éviter les doublons
    const existingIndex = history.findIndex((item: any) => item.query === query)
    if (existingIndex !== -1) {
      history.splice(existingIndex, 1)
    }
    
    history.unshift({
      id: Date.now().toString(),
      query,
      timestamp: new Date().toISOString()
    })

    // Limiter à 50 recherches
    if (history.length > 50) {
      history.pop()
    }

    localStorage.setItem('searchHistory', JSON.stringify(history))
  }

  const getSearchHistory = () => {
    if (typeof window === 'undefined') return []
    return JSON.parse(localStorage.getItem('searchHistory') || '[]')
  }

  const clearHistory = () => {
    if (typeof window === 'undefined') return
    localStorage.removeItem('searchHistory')
  }

  return {
    isLoading,
    results,
    totalResults,
    searchTime,
    error,
    performSearch,
    getSearchHistory,
    clearHistory
  }
}