// moteur-recherche-frontend/composables/useAdvancedSearch.ts
import { ref } from 'vue'

export interface AdvancedSearchOptions {
  query: string
  booleanQuery?: string
  filters: {
    domains: string[]
    types: string[]
    sources: string[]
    dateRange: { start: string; end: string }
    language: string
    minScore: number
    size: string
    includeImages: boolean
    includeCode: boolean
    includeVideos: boolean
  }
  sortBy: string
  page: number
  size: number
}

export const useAdvancedSearch = () => {
  const isLoading = ref(false)
  const results = ref<any[]>([])
  const totalResults = ref(0)
  const searchTime = ref<number | null>(null)
  const error = ref<string | null>(null)

  const performSearch = async (options: AdvancedSearchOptions) => {
    isLoading.value = true
    error.value = null
    const startTime = Date.now()

    try {
      // Utiliser $fetch directement au lieu de searchService
      const config = useRuntimeConfig()
      const response = await $fetch('/api/search/advanced', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        body: options
      }) as any
      
      results.value = response.results || []
      totalResults.value = response.total || 0
      searchTime.value = Date.now() - startTime
      
      // Sauvegarder dans l'historique
      saveToHistory(options)
      
      return { success: true, data: response }
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la recherche avancée'
      console.error('Advanced search error:', err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const saveToHistory = (options: AdvancedSearchOptions) => {
    if (typeof window === 'undefined') return
    
    const history = JSON.parse(localStorage.getItem('advancedSearchHistory') || '[]')
    
    history.unshift({
      id: Date.now().toString(),
      query: options.query || options.booleanQuery || '',
      options,
      timestamp: new Date().toISOString()
    })

    // Limiter à 20 recherches
    if (history.length > 20) {
      history.pop()
    }

    localStorage.setItem('advancedSearchHistory', JSON.stringify(history))
  }

  const getSearchHistory = () => {
    if (typeof window === 'undefined') return []
    return JSON.parse(localStorage.getItem('advancedSearchHistory') || '[]')
  }

  const clearHistory = () => {
    if (typeof window === 'undefined') return
    localStorage.removeItem('advancedSearchHistory')
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