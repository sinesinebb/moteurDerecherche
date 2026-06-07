
<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-white dark:bg-[#202124]']">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Compteur discret -->
      <div v-if="query && !isLoading && !error && totalResults > 0" class="mb-4 text-xs text-gray-500 dark:text-gray-400">
        Environ {{ totalResults }} vidéo{{ totalResults > 1 ? 's' : '' }} ({{ searchTime }} ms)
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">Recherche de vidéos en cours...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg mb-6">
        <span class="text-red-700 dark:text-red-300 text-sm">{{ error }}</span>
      </div>

      <!-- Résultats vidéo -->
      <div v-else-if="videos.length > 0" class="space-y-6">
        <div v-for="video in videos" :key="video.id" class="group">
          <div class="flex flex-col md:flex-row gap-4 pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0">
            <!-- Miniature -->
            <div class="flex-shrink-0 md:w-40 lg:w-48">
              <div 
                class="relative aspect-video rounded-lg overflow-hidden bg-gray-300 dark:bg-gray-600 cursor-pointer"
                @click="openVideo(video)"
              >
                <img
                  :src="video.thumbnail"
                  :alt="video.title"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                  @error="onThumbnailError"
                />
                <!-- Badge durée -->
                <div v-if="video.duration" class="absolute bottom-1 right-1 px-1.5 py-0.5 bg-black/70 text-white text-xs rounded">
                  {{ video.duration }}
                </div>
              </div>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <!-- Domaine / Source -->
              <div class="text-xs text-green-700 dark:text-[#bdc1c6] mb-1 truncate">
                {{ video.url }}
              </div>

              <!-- Titre -->
              <h3 class="text-lg font-normal mb-1">
                <a
                  :href="video.url"
                  target="_blank"
                  class="result-link text-blue-700 dark:text-[#8ab4f8] hover:underline cursor-pointer"
                  @click="openVideo(video)"
                >
                  {{ video.title }}
                </a>
              </h3>

              <!-- Description (extrait) -->
              <p class="text-sm text-gray-600 dark:text-[#e8eaed] leading-relaxed line-clamp-2 mb-1">
                {{ video.description }}
              </p>

              <!-- Métadonnées -->
              <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                <span>{{ formatViews(video.views) }} vues</span>
                <span v-if="video.source">{{ video.source }}</span>
                <span v-if="video.tags && video.tags.length" class="hidden sm:inline">
                  {{ video.tags.slice(0, 3).join(', ') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Aucun résultat -->
      <div v-else-if="query" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Aucune vidéo trouvée pour <strong>{{ query }}</strong>.</p>
        <button @click="router.push('/')" class="mt-4 text-blue-600 dark:text-blue-400 hover:underline text-sm">
          Retour à l'accueil
        </button>
      </div>

      <!-- Page vide initiale -->
      <div v-else class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Recherchez des vidéos techniques.</p>
      </div>

      <!-- Pagination simple -->
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

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const historyStore = useHistoryStore()
const themeStore = useThemeStore()

const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl || 'http://localhost:80'
const SEARCH_API_URL = `${API_BASE_URL}/api/search`

interface VideoResult {
  id: string
  title: string
  description: string
  url: string
  thumbnail: string
  duration: string
  views: number
  source: string
  tags: string[]
  type: string
}

const query = ref('')
const videos = ref<VideoResult[]>([])
const isLoading = ref(false)
const error = ref('')
const totalResults = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(12)
const searchTime = ref<number | null>(null)

const totalPages = computed(() => Math.ceil(totalResults.value / itemsPerPage.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const formatViews = (views: number) => {
  if (views >= 1_000_000) return (views / 1_000_000).toFixed(1) + 'M'
  if (views >= 1_000) return (views / 1_000).toFixed(1) + 'K'
  return views.toString()
}

// Convertit des secondes en format lisible (MM:SS ou HH:MM:SS)
const formatDuration = (seconds: number): string => {
  if (!seconds) return ''
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${m}:${String(s).padStart(2, '0')}`
}

const openVideo = (video: VideoResult) => {
  window.open(video.url, '_blank')
}

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  router.push({
    path: '/videos',
    query: { ...route.query, page: page.toString() }
  })
}

// Enlève les balises HTML d'une chaîne
const stripHtml = (html: string): string => {
  if (!html) return ''
  // Crée un élément temporaire, lui assigne le HTML et récupère le texte
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

const performSearch = async (searchQuery: string, page: number) => {
  if (!searchQuery.trim()) {
    videos.value = []
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
      page: page,
      limit: itemsPerPage.value,
      content_type: 'youtube_video'  
    }

    const response = await $fetch<any>(SEARCH_API_URL, {
      method: 'GET',
      params,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })

    if (response && Array.isArray(response.results)) {
      // Le backend renvoie déjà les bons champs pour chaque vidéo YouTube
      const mappedVideos = response.results
        .filter((item: any) => item.content_type === 'youtube_video')
        .map((item: any) => ({
          id: item.id,
          title: item.title || 'Vidéo sans titre',
          // description: item.snippet || item.description || '',
          description: stripHtml(item.snippet || item.description || ''),// Enlever les balises HTML
          url: item.url,
          thumbnail: item.thumbnail || '',
          duration: formatDuration(item.duration),   // conversion en "MM:SS"
          views: item.views || 0,
          source: item.source || 'YouTube',
          tags: item.tags || [],
          type: 'youtube_video'
        }))

      videos.value = mappedVideos as any[]
      totalResults.value = mappedVideos.length
      searchTime.value = response.processing_time || (Date.now() - startTime)

      // Enregistrer dans l'historique si connecté
      if (authStore.isAuthenticated) {
        historyStore.addSearch(searchQuery, {
          type: 'videos',
          results: videos.value
        })
      }
    } else {
      videos.value = []
      totalResults.value = 0
      searchTime.value = Date.now() - startTime
    }
  } catch (err: any) {
    console.error('Erreur de recherche vidéo:', err)
    error.value = err.message || 'Erreur lors de la recherche de vidéos'
    videos.value = []
    totalResults.value = 0
    searchTime.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const routeQuery = route.query.q as string
  const routePage = parseInt(route.query.page as string) || 1
  if (routeQuery) {
    query.value = routeQuery
    currentPage.value = routePage
    performSearch(routeQuery, routePage)
  }
})

const onThumbnailError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) img.src = 'https://via.placeholder.com/320x180?text=No+Thumbnail'
}

watch(
  () => route.query,
  (newQuery) => {
    const newQ = newQuery.q as string
    const newPage = parseInt(newQuery.page as string) || 1
    if (newQ) {
      query.value = newQ
      currentPage.value = newPage
      performSearch(newQ, newPage)
    } else {
      query.value = ''
      videos.value = []
      totalResults.value = 0
      searchTime.value = null
    }
  },
  { deep: true, immediate: false }
)
</script>



<style scoped>
.aspect-video {
  aspect-ratio: 16 / 9;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
/* Lien visité en violet */
.result-link:visited {
  color: #681da8 !important;
}
.dark .result-link:visited {
  color: #c084fc !important;
}
</style>
