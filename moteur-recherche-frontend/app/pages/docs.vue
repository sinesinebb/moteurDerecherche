<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-white dark:bg-[#202124]']">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Compteur discret + filtres -->
      <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div v-if="query && !isLoading && !error" class="text-xs text-gray-500 dark:text-gray-400">
          Environ {{ totalResults }} document{{ totalResults > 1 ? 's' : '' }} ({{ searchTime }} ms)
        </div>
        <div class="flex items-center gap-2">
          <select
            v-model="sortBy"
            @change="performSearch(query)"
            class="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-[#303134] text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="date_desc">Plus récent</option>
            <option value="size">Taille</option>
            <option value="pages">Nombre de pages</option>
          </select>
          <select
            v-model="fileType"
            @change="performSearch(query)"
            class="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-[#303134] text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="all">Tous formats</option>
            <option value="pdf">PDF</option>
            <option value="doc">DOC/DOCX</option>
            <option value="ppt">PPT/PPTX</option>
            <option value="xls">XLS/XLSX</option>
            <option value="txt">TXT</option>
            <option value="md">Markdown</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">Recherche de documents en cours...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg mb-6">
        <span class="text-red-700 dark:text-red-300 text-sm">{{ error }}</span>
        <button @click="performSearch(query)" class="ml-4 text-red-700 dark:text-red-300 underline text-sm">Réessayer</button>
      </div>

      <!-- Résultats -->
      <div v-else-if="documents.length > 0" class="space-y-6">
        <div v-for="doc in documents" :key="doc.id" class="pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0">
          <!-- URL / domaine -->
          <div class="text-xs text-green-700 dark:text-[#bdc1c6] mb-1 truncate">
            {{ doc.url }}
          </div>
          <!-- Titre -->
          <h3 class="text-lg font-normal mb-1">
            <a
              :href="doc.url"
              target="_blank"
              class="result-link text-blue-700 dark:text-[#8ab4f8] hover:underline cursor-pointer"
              @click="openDocument(doc)"
            >
              {{ doc.title }}
            </a>
          </h3>
          <!-- Description -->
          <p class="text-sm text-gray-600 dark:text-[#e8eaed] line-clamp-2 mb-2">
            {{ doc.description }}
          </p>
          <!-- Métadonnées -->
          <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
            <span class="flex items-center gap-1">{{ getFileTypeIcon(doc.type) }} {{ getFileTypeLabel(doc.type) }}</span>
            <span v-if="doc.size !== '—'">{{ doc.size }}</span>
            <span v-if="doc.pages !== '—'">{{ doc.pages }} page{{ doc.pages > 1 ? 's' : '' }}</span>
            <span v-if="doc.word_count">{{ formatNumber(doc.word_count) }} mots</span>
            <span>{{ doc.source }}</span>
            <span v-if="formatDate(doc.date)">{{ formatDate(doc.date) }}</span>
          </div>
          <!-- Actions (aperçu/télécharger) -->
          <div class="mt-2 flex items-center gap-3">
            <button @click="previewDocument(doc)" class="text-xs text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
              Aperçu
            </button>
            <a :href="doc.url" download class="text-blue-600 hover:underline">
            Télécharger
          </a>
          </div>
        </div>
      </div>

      <!-- Aucun résultat -->
      <div v-else-if="query" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Aucun document trouvé pour <strong>{{ query }}</strong>.</p>
        <div class="mt-4 flex flex-wrap justify-center gap-3">
          <button
            v-for="suggestion in searchSuggestions"
            :key="suggestion"
            @click="searchAlternative(suggestion)"
            class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>

      <!-- Vide (pas encore recherché) -->
      <div v-else class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Recherchez des documents techniques (PDF, DOC, PPT, etc.).</p>
      </div>

      <!-- Pagination  -->
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

definePageMeta({
  layout: 'default'
})

import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from '#app'
import { useThemeStore } from '../../stores/theme.store'
import { useAuthStore } from '../../stores/auth.store'
import { useHistoryStore } from '../../stores/history.store'
import { useRuntimeConfig } from '#app'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const historyStore = useHistoryStore()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl || 'http://localhost'

// Interface pour la réponse de l'API de recherche
interface SearchResponse {
  results: any[]
  total: number
  processing_time?: number
}

// État réactif
const query = ref('')
const documents = ref<any[]>([])
const isLoading = ref(false)
const error = ref('')
const totalResults = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalPages = ref(1)
const searchTime = ref<number | null>(null)

// Filtres
const fileType = ref('pdf')
const sortBy = ref('date_desc')  // Changé : 'relevance' supprimé, valeur par défaut 'date_desc'
const selectedLanguages = ref<string[]>(['fr', 'en']) // Gardé pour compatibilité mais UI retirée

// Données pour l'UI
const languages = [
  { code: 'fr', name: 'Français' },
  { code: 'en', name: 'Anglais' },
  { code: 'es', name: 'Espagnol' },
  { code: 'de', name: 'Allemand' }
]

const searchSuggestions = [
  'React documentation',
  'Docker guide',
  'Python tutorial',
  'API specification'
]

// Computed
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// Formatter les dates
const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return "Aujourd'hui"
    if (diffDays === 1) return 'Hier'
    if (diffDays < 7) return `Il y a ${diffDays} jours`
    if (diffDays < 30) return `Il y a ${Math.floor(diffDays / 7)} semaines`
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return 'Date inconnue'
  }
}

// Formatter les nombres
const formatNumber = (num: number) => new Intl.NumberFormat('fr-FR').format(num)

// Formatter la taille en octets
const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Obtenir l'étiquette du type de fichier
const getFileTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'pdf': 'PDF', 'doc': 'DOC', 'docx': 'DOCX', 'ppt': 'PPT', 'pptx': 'PPTX',
    'xls': 'XLS', 'xlsx': 'XLSX', 'txt': 'TXT', 'md': 'Markdown', 'web': 'Page Web'
  }
  return labels[type.toLowerCase()] || type.toUpperCase()
}

// Obtenir l'icône du type de fichier
const getFileTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    'pdf': '📄', 'doc': '📝', 'docx': '📝', 'ppt': '📊', 'pptx': '📊',
    'xls': '📈', 'xlsx': '📈', 'txt': '📃', 'md': '📋', 'web': '🌐'
  }
  return icons[type.toLowerCase()] || '📄'
}

// Obtenir la classe CSS pour le type de fichier
const getFileTypeClass = (type: string) => {
  const classes: Record<string, string> = {
    'pdf': 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
    'doc': 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    'docx': 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    'ppt': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
    'pptx': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
    'xls': 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    'xlsx': 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    'txt': 'bg-gray-100 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400',
    'md': 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    'web': 'bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400'
  }
  return classes[type.toLowerCase()] || 'bg-gray-100 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400'
}

// Basculer la sélection de langue (gardé mais UI retirée)
const toggleLanguage = (langCode: string) => {
  const index = selectedLanguages.value.indexOf(langCode)
  if (index > -1) selectedLanguages.value.splice(index, 1)
  else selectedLanguages.value.push(langCode)
  if (query.value) {
    currentPage.value = 1
    performSearch(query.value)
  }
}

// Ouvrir un document
const openDocument = async (doc: any) => window.open(doc.url, '_blank')

// Aperçu du document
const previewDocument = (doc: any) => window.open(doc.url, '_blank')

// Aller à une page
const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  if (query.value) {
    router.push({
      path: '/docs',
      query: { q: query.value, page: page.toString(), type: fileType.value, sort: sortBy.value }
    })
    performSearch(query.value)
  }
}

// Rechercher une alternative
const searchAlternative = (alternative: string) => {
  query.value = alternative
  currentPage.value = 1
  router.push({
    path: '/docs',
    query: { q: alternative, page: '1', type: fileType.value, sort: sortBy.value }
  })
  performSearch(alternative)
}

// Effectuer la recherche (appel API réel)
const performSearch = async (searchQuery: string) => {
  if (!searchQuery.trim()) {
    documents.value = []
    totalResults.value = 0
    searchTime.value = null
    return
  }

  isLoading.value = true
  error.value = ''
  const startTime = Date.now()

  try {
    const params: Record<string, any> = {
      q: searchQuery,
      page: currentPage.value,
      limit: itemsPerPage.value,
      sort: sortBy.value,
      content_type: 'all'
    }

    if (fileType.value !== 'all') {
      params.file_type = fileType.value
    }

    const response = await $fetch<SearchResponse>(`${API_BASE_URL}/api/search`, { params })

    if (response && Array.isArray(response.results)) {
      documents.value = response.results.map((item: any) => ({
        id: item.id,
        title: item.title || 'Sans titre',
        description: item.snippet || item.description || '',
        url: item.url,
        type: item.file_type || (item.url?.match(/\.(pdf|docx?|pptx?|xlsx?|txt|md)$/i) ? RegExp.$1 : 'web'),
        size: item.file_size ? formatBytes(item.file_size) : '—',
        pages: item.pages || '—',
        word_count: item.word_count || 0,
        source: item.domain || 'Inconnu',
        date: item.crawled_at || item.timestamp || new Date().toISOString(),
        language: item.language || 'en',
      }))

      totalResults.value = response.total || 0
      totalPages.value = Math.ceil(totalResults.value / itemsPerPage.value)
      searchTime.value = response.processing_time || (Date.now() - startTime)
      if (authStore.isAuthenticated) {
        historyStore.addSearch(searchQuery, {
          type: 'docs',
          results: documents.value 
        })
      }
    } else {
      documents.value = []
      totalResults.value = 0
      searchTime.value = Date.now() - startTime
    }

  } catch (err: any) {
    console.error('Erreur de recherche de documents:', err)
    error.value = err.message || 'Erreur lors de la connexion au serveur de recherche'
    documents.value = []
    totalResults.value = 0
    searchTime.value = null
  } finally {
    isLoading.value = false
  }
}

// Initialisation au montage
onMounted(() => {
  const routeQuery = route.query.q as string
  const routePage = parseInt(route.query.page as string) || 1
  const routeType = route.query.type as string
  const routeSort = route.query.sort as string
  if (routeQuery) {
    query.value = routeQuery
    currentPage.value = routePage
    if (routeType) fileType.value = routeType
    if (routeSort) sortBy.value = routeSort
    performSearch(routeQuery)
  }
})

// Surveiller les changements d'URL
watch(() => route.query, (newQuery) => {
  const routeQuery = newQuery.q as string
  const routePage = parseInt(newQuery.page as string) || 1
  const routeType = newQuery.type as string
  const routeSort = newQuery.sort as string
  if (routeQuery) {
    query.value = routeQuery
    currentPage.value = routePage
    if (routeType) fileType.value = routeType
    if (routeSort) sortBy.value = routeSort
    performSearch(routeQuery)
  } else {
    query.value = ''
    documents.value = []
    totalResults.value = 0
    searchTime.value = null
  }
})

// Surveiller les changements de filtres pour relancer la recherche
watch([fileType, sortBy], () => {
  if (query.value) {
    currentPage.value = 1
    performSearch(query.value)
  }
})
</script>


<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.result-link:visited {
  color: #681da8 !important;
}
.dark .result-link:visited {
  color: #c084fc !important;
}
</style>