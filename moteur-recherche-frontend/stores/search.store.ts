// moteur-recherche-frontend/stores/search.store.ts
import { defineStore } from 'pinia'

interface SearchResult {
  id: string
  title: string
  snippet: string
  url: string
  type: string
  score: number
  date: string
  domain?: string
}

interface SearchFilters {
  type: string
  sort: string
  date: string
  [key: string]: any
}

export const useSearchStore = defineStore('search', {
  state: () => ({
    query: '',
    results: [] as SearchResult[],
    filters: {
      type: 'all',
      sort: 'relevance',
      date: 'all'
    } as SearchFilters,
    isLoading: false,
    error: null as string | null,
    totalResults: 0,
    currentPage: 1,
    itemsPerPage: 20,
    searchTime: null as number | null,
    searchHistory: [] as Array<{
      id: string
      query: string
      timestamp: string
      results: number
      type: string
    }>
  }),

  getters: {
    // Correction : utiliser state.results au lieu de state.filteredResults
    filteredResults: (state) => {
      let filtered = [...state.results]
      
      // Filtrer par type
      if (state.filters.type !== 'all') {
        filtered = filtered.filter(result => result.type === state.filters.type)
      }
      
      // Filtrer par date (simplifié)
      if (state.filters.date !== 'all') {
        const now = new Date()
        filtered = filtered.filter(result => {
          const resultDate = new Date(result.date)
          const diffTime = Math.abs(now.getTime() - resultDate.getTime())
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          
          switch (state.filters.date) {
            case 'today': return diffDays === 0
            case 'week': return diffDays <= 7
            case 'month': return diffDays <= 30
            case 'year': return diffDays <= 365
            default: return true
          }
        })
      }
      
      // Trier
      switch (state.filters.sort) {
        case 'date_desc':
          filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
          break
        case 'date_asc':
          filtered.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
          break
        case 'pagerank':
          filtered.sort((a, b) => b.score - a.score)
          break
        default: // 'relevance'
          filtered.sort((a, b) => b.score - a.score)
      }
      
      return filtered
    },
    
    paginatedResults: (state) => {
      const store = useSearchStore()
      const filtered = store.filteredResults
      const start = (state.currentPage - 1) * state.itemsPerPage
      const end = start + state.itemsPerPage
      return filtered.slice(start, end)
    },
    
    totalPages: (state) => {
      const store = useSearchStore()
      return Math.ceil(store.filteredResults.length / state.itemsPerPage)
    }
  },

  actions: {
    setQuery(query: string) {
      this.query = query
    },
    
    setFilters(filters: Partial<SearchFilters>) {
      this.filters = { ...this.filters, ...filters }
    },
    
    setPage(page: number) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    
    async performSearch() {
      if (!this.query.trim()) {
        this.results = []
        this.totalResults = 0
        return
      }

      this.isLoading = true
      this.error = null
      const startTime = Date.now()

      try {
        // Simulation d'appel API
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Données simulées
        this.results = Array.from({ length: 50 }, (_, i) => ({
          id: `result-${i}`,
          title: `${this.query} - Résultat #${i + 1}`,
          snippet: `Ceci est un résultat de recherche pour "${this.query}". Il contient des informations pertinentes sur le sujet recherché.`,
          url: `https://example.com/result-${i}`,
          type: ['web', 'documentation', 'tutorial', 'video', 'image'][Math.floor(Math.random() * 5)],
          score: 0.9 - (i * 0.01),
          date: new Date(Date.now() - Math.random() * 10000000000).toISOString(),
          domain: 'example.com'
        }))
        
        this.totalResults = this.results.length
        this.searchTime = Date.now() - startTime
        
        // Ajouter à l'historique
        this.addToHistory()
        
      } catch (err: any) {
        this.error = err.message || 'Erreur lors de la recherche'
        this.results = []
        this.totalResults = 0
        this.searchTime = null
      } finally {
        this.isLoading = false
      }
    },
    
    addToHistory() {
      const historyEntry = {
        id: Date.now().toString(),
        query: this.query,
        timestamp: new Date().toISOString(),
        results: this.totalResults,
        type: 'general'
      }
      
      this.searchHistory.unshift(historyEntry)
      
      // Garder seulement les 50 dernières recherches
      if (this.searchHistory.length > 50) {
        this.searchHistory = this.searchHistory.slice(0, 50)
      }
      
      // Sauvegarder dans localStorage
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
    },
    
    loadHistory() {
      const stored = localStorage.getItem('searchHistory')
      if (stored) {
        this.searchHistory = JSON.parse(stored)
      }
    },
    
    clearHistory() {
      this.searchHistory = []
      localStorage.removeItem('searchHistory')
    },
    
    removeFromHistory(id: string) {
      this.searchHistory = this.searchHistory.filter(entry => entry.id !== id)
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
    }
  },
})