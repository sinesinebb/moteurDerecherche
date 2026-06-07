<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-white dark:bg-[#202124]']">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

      <!-- États de chargement et d'erreur -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">Recherche en cours...</p>
      </div>

      <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg mb-6">
        <span class="text-red-700 dark:text-red-300 text-sm">{{ error }}</span>
      </div>

      <!-- Message hors domaine -->
      <OutOfDomainMessage
        v-else-if="outOfDomain"
        :message="domainMessage"
        :suggestions="['Python tutoriel', 'Docker débutant', 'Machine learning cours', 'SQL requêtes']"
        @search="performSearch"
      />

      <!-- Résultats -->
      <div v-else-if="results.length > 0" class="space-y-6">
        <div v-for="result in results" :key="result.id" class="pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0">
          <!-- URL / domaine -->
          <div class="text-xs text-green-700 dark:text-[#bdc1c6] mb-1 truncate">
            {{ result.url }}
          </div>
          <!-- Titre – lien visité en violet -->
          <h3 class="text-xl font-normal mb-1">
            <a
              :href="result.url"
              target="_blank"
              class="result-link text-blue-700 dark:text-[#8ab4f8] hover:underline cursor-pointer"
              @click="trackClick(result)"
            >
              {{ result.title || 'Document sans titre' }}
            </a>
          </h3>
          <!-- Extrait -->
          <p class="text-sm text-gray-600 dark:text-[#e8eaed] leading-relaxed line-clamp-2">
            {{ cleanSnippet(result.snippet) }}
          </p>
          <!-- Métadonnées secondaires -->
          <div class="flex flex-wrap items-center gap-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
            <span v-if="isValidDate(result.date)">{{ formatDate(result.date) }}</span>
            <span v-if="result.word_count">{{ formatNumber(result.word_count) }} mots</span>
            <span v-if="result.type && result.type !== 'unknown'" class="capitalize">{{ formatType(result.type) }}</span>
          </div>
        </div>
      </div>

      <!-- Aucun résultat -->
      <div v-else-if="query" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Aucun résultat trouvé pour <strong>{{ query }}</strong>.</p>
        <button @click="router.push('/')" class="mt-4 text-blue-600 dark:text-blue-400 hover:underline text-sm">
          Retour à l'accueil
        </button>
      </div>

      <!-- Pagination -->
      <div v-if="totalResults > itemsPerPage" class="flex justify-center items-center gap-2 mt-8">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'px-3 py-1.5 text-sm rounded-md border',
            currentPage === 1
              ? 'border-gray-200 dark:border-gray-700 text-gray-400 cursor-not-allowed'
              : 'border-gray-300 dark:border-gray-600 text-blue-600 dark:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
          ]"
        >
          Précédent
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="goToPage(page)"
          :class="[
            'px-3 py-1.5 text-sm rounded-md',
            page === currentPage
              ? 'bg-blue-600 text-white font-medium'
              : 'text-blue-600 dark:text-blue-400 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800'
          ]"
        >
          {{ page }}
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          :class="[
            'px-3 py-1.5 text-sm rounded-md border',
            currentPage === totalPages
              ? 'border-gray-200 dark:border-gray-700 text-gray-400 cursor-not-allowed'
              : 'border-gray-300 dark:border-gray-600 text-blue-600 dark:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
          ]"
        >
          Suivant
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from '#app'
import { useThemeStore } from '../../stores/theme.store'
import { useAuthStore } from '../../stores/auth.store'
import { useHistoryStore } from '../../stores/history.store'
import OutOfDomainMessage from '../../components/OutOfDomainMessage.vue'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const historyStore = useHistoryStore()

const outOfDomain = ref(false)
const domainMessage = ref('')

// Configuration API
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl || 'http://localhost:80'
const SEARCH_API_URL = `${API_BASE_URL}/api/search`

// Types d'interfaces
interface SearchResult {
  id: string
  title: string
  snippet: string
  url: string
  domain: string
  date: string
  type: string
  score: number
  word_count?: number
  language?: string
  metadata?: Record<string, any>
}

interface SearchResponse {
  results: SearchResult[]
  total: number
  took: number
  page?: number
  total_pages?: number
  is_informatics_domain?: boolean      // ← ajouté
  domain_message?: string               // ← ajouté
  processing_time?: number              // ← ajouté
}

// État réactif
const query = ref('')
const results = ref<SearchResult[]>([])
const isLoading = ref(false)
const error = ref('')
const totalResults = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalPages = ref(1)
const sortBy = ref('relevance')
const searchTime = ref<number | null>(null)

// Computed
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Nettoyage avancé du snippet (supprime HTML, scripts, entités)
const cleanSnippet = (html: string): string => {
  if (!html) return ''

  let text = ''

  if (process.client) {
    try {
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const elementsToRemove = doc.querySelectorAll('script, style, noscript, iframe, svg, head, meta, link')
      elementsToRemove.forEach(el => el.remove())
      text = doc.body.textContent || ''
      text = text.replace(/\s+/g, ' ').trim()
    } catch (e) {
      console.error('Erreur DOMParser', e)
    }
  }

  if (!text || text.length < 50) {
    let cleaned = html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, ' ')
      .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, ' ')
      .replace(/<noscript\b[^<]*(?:(?!<\/noscript>)<[^<]*)*<\/noscript>/gi, ' ')
      .replace(/<[^>]*>/g, ' ')

    const entities: { [key: string]: string } = {
      '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>',
      '&quot;': '"', '&#39;': "'", '&#x2F;': '/', '&#47;': '/',
      '&#60;': '<', '&#62;': '>', '&#40;': '(', '&#41;': ')',
      '&#123;': '{', '&#125;': '}', '&#91;': '[', '&#93;': ']',
      '&#58;': ':', '&#59;': ';', '&#61;': '=', '&#43;': '+',
      '&#45;': '-', '&#95;': '_', '&#42;': '*', '&#64;': '@',
      '&#36;': '$', '&#33;': '!', '&#63;': '?', '&#46;': '.', '&#44;': ',',
    }
    for (const [entity, char] of Object.entries(entities)) {
      cleaned = cleaned.replace(new RegExp(entity, 'g'), char)
    }
    cleaned = cleaned.replace(/\s+/g, ' ').trim()
    if (cleaned.length > text.length) {
      text = cleaned
    }
  }

  if (text.length > 200) {
    const truncated = text.substring(0, 200)
    const lastPeriod = truncated.lastIndexOf('.')
    const lastSpace = truncated.lastIndexOf(' ')
    if (lastPeriod > 100) {
      text = text.substring(0, lastPeriod + 1)
    } else if (lastSpace > 100) {
      text = text.substring(0, lastSpace) + '...'
    } else {
      text = truncated + '...'
    }
  }

  return text
}

const isValidDate = (dateString: string): boolean => {
  if (!dateString) return false
  const date = new Date(dateString)
  return !isNaN(date.getTime())
}

const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return ''
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return "Aujourd'hui"
    if (diffDays === 1) return 'Hier'
    if (diffDays < 7) return `Il y a ${diffDays} jours`
    if (diffDays < 30) return `Il y a ${Math.floor(diffDays / 7)} semaines`
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric', month: 'short', day: 'numeric'
    })
  } catch {
    return ''
  }
}

const formatType = (type: string) => {
  const types: Record<string, string> = {
    'web': 'Article Web',
    'documentation': 'Documentation',
    'tutorial': 'Tutoriel',
    'api': 'API',
    'forum': 'Forum',
    'research': 'Recherche',
    'video': 'Vidéo',
    'image': 'Image',
    'pdf': 'PDF',
    'github': 'GitHub'
  }
  return types[type] || type.charAt(0).toUpperCase() + type.slice(1)
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('fr-FR').format(num)
}

const trackClick = (result: SearchResult) => {
  if (authStore.isAuthenticated) {
    $fetch(`${API_BASE_URL}/api/history/clicks`, {
      method: 'POST',
      body: { result_id: result.id, query: query.value, url: result.url }
    }).catch(err => console.error('Erreur tracking clic:', err))
  }
  window.open(result.url, '_blank')
}

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return

  currentPage.value = page
  if (query.value) {
    router.push({
      path: '/search',
      query: {
        q: query.value,
        page: page.toString(),
        sort: sortBy.value
      }
    })
    performSearch(query.value)
  }
}

const performSearch = async (searchQuery: string) => {
  if (!searchQuery.trim()) {
    results.value = []
    totalResults.value = 0
    searchTime.value = null
    return
  }

  isLoading.value = true
  error.value = ''
  const startTime = Date.now()

  try {
    const params = {
      q: searchQuery,
      page: currentPage.value,
      limit: itemsPerPage.value,
      sort: sortBy.value,
      lang: 'fr'
    }

    const response = await $fetch<SearchResponse>(SEARCH_API_URL, {
      method: 'GET',
      params,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })

    if (response) {
      // Vérification hors domaine
      if (response.is_informatics_domain === false) {
        outOfDomain.value = true
        domainMessage.value = response.domain_message || "Votre recherche ne semble pas concerner le domaine informatique."
        results.value = []
        totalResults.value = 0
        searchTime.value = null
        return
      }

      outOfDomain.value = false
      if (Array.isArray(response.results)) {
        results.value = response.results
        totalResults.value = response.total || response.results.length
        searchTime.value = response.processing_time || response.took || Date.now() - startTime
        totalPages.value = Math.ceil(totalResults.value / itemsPerPage.value)

        if (authStore.isAuthenticated) {
          historyStore.addSearch(searchQuery, {
            type: 'search',
            results: results.value
          })
        }
      } else {
        results.value = []
        totalResults.value = 0
        searchTime.value = Date.now() - startTime
      }
    }

  } catch (err: any) {
    console.error('Erreur de recherche:', err)
    error.value = err.message || 'Erreur de connexion au serveur de recherche'
    results.value = []
    totalResults.value = 0
    searchTime.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const routeQuery = route.query.q as string
  const routePage = parseInt(route.query.page as string) || 1
  const routeSort = route.query.sort as string

  if (routeQuery) {
    query.value = routeQuery
    currentPage.value = routePage
    if (routeSort) sortBy.value = routeSort
    performSearch(routeQuery)
  }
})

watch(
  () => route.query,
  (newQuery) => {
    const routeQuery = newQuery.q as string
    const routePage = parseInt(newQuery.page as string) || 1
    const routeSort = newQuery.sort as string

    if (routeQuery) {
      query.value = routeQuery
      currentPage.value = routePage
      if (routeSort) sortBy.value = routeSort
      performSearch(routeQuery)
    } else {
      query.value = ''
      results.value = []
      totalResults.value = 0
      searchTime.value = null
    }
  }
)
</script>

<style scoped>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 { animation-delay: 2s; }
.animation-delay-4000 { animation-delay: 4s; }
.animation-delay-1000 { animation-delay: 1s; }

.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.fade-up-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.border-gradient-to-b {
  border-image: linear-gradient(to bottom, #3b82f6, #a855f7) 1;
}

.shadow-3xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.result-link:visited {
  color: #681da8 !important;
}
.dark .result-link:visited {
  color: #c084fc !important;
}
</style>