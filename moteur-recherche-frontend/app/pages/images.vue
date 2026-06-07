<!-- moteur-recherche-frontend/app/pages/images.vue -->
<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-white dark:bg-[#202124]']">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- En-tête : compteur et filtres -->
      <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <!-- Compteur de résultats -->
        <div v-if="query && !isLoading && !error" class="text-xs text-gray-500 dark:text-gray-400">
          Environ {{ totalResults }} image{{ totalResults > 1 ? 's' : '' }} ({{ searchTime }} ms)
        </div>

        <!-- Filtres (discrets) -->
        <div class="flex flex-wrap items-center gap-2">
          <select v-model="imageType" class="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-[#303134] text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
            <option value="all">Tous types</option>
            <option value="photo">Photo</option>
            <option value="illustration">Illustration</option>
            <option value="vector">Vecteur</option>
            <option value="gif">GIF</option>
          </select>
          <select v-model="imageSize" class="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-[#303134] text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
            <option value="all">Toutes tailles</option>
            <option value="small">Petite</option>
            <option value="medium">Moyenne</option>
            <option value="large">Grande</option>
          </select>
          <select v-model="orientationFilter" class="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-[#303134] text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
            <option value="all">Toute orientation</option>
            <option value="landscape">Paysage</option>
            <option value="portrait">Portrait</option>
            <option value="square">Carré</option>
          </select>
          <select v-model="colorFilter" class="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-[#303134] text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
            <option value="all">Toutes couleurs</option>
            <option value="color">Couleur</option>
            <option value="monochrome">Monochrome</option>
          </select>
        </div>
      </div>

      <!-- États de chargement et d'erreur -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">Recherche d'images en cours...</p>
      </div>

      <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg mb-6">
        <span class="text-red-700 dark:text-red-300 text-sm">{{ error }}</span>
      </div>

      <!-- Grille d'images -->
      <div v-else-if="images.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <div 
          v-for="image in images" 
          :key="image.id"
          class="group relative bg-white dark:bg-[#303134] rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition-shadow duration-200"
        >
          <!-- Image -->
          <div class="relative aspect-square overflow-hidden bg-gray-200 dark:bg-gray-700">
            <img 
              :src="image.thumbnail" 
              :alt="image.title || 'Image'"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              loading="lazy"
              @error="onImageError"
            />
            <!-- Overlay au survol avec lien -->
            <a 
              :href="image.media_url || image.url" 
              target="_blank"
              @click.prevent="openImage(image)"
              class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200 flex items-end p-2 opacity-0 group-hover:opacity-100"
            >
              <span class="text-xs text-white bg-black/60 px-2 py-1 rounded">
                {{ image.title?.substring(0, 50) }}
              </span>
            </a>
          </div>
          <!-- Infos sous l'image (discrètes) -->
          <div class="p-2">
            <p class="text-xs font-medium text-gray-900 dark:text-white truncate">{{ image.title || 'Image sans titre' }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{{ image.source }}</p>
          </div>
        </div>
      </div>

      <!-- Aucun résultat -->
      <div v-else-if="query" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Aucune image trouvée pour <strong>{{ query }}</strong>.</p>
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
const themeStore = useThemeStore()
const authStore = useAuthStore()
const historyStore = useHistoryStore()

// Configuration API via nginx
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl || 'http://localhost:80'
// On utilise la même route que la recherche textuelle avec le filtre content_type=image
const SEARCH_API_URL = `${API_BASE_URL}/api/search`

// Types d'interfaces (adaptés à la réponse de l'API de recherche)
interface SearchImageResult {
  id: string
  title: string
  url: string
  domain?: string
  image_urls?: string[]
  // autres ...
}

interface SearchResponse {
  results: SearchImageResult[]
  total: number
  processing_time?: number
  page?: number
  total_pages?: number
}

// Interface pour l'affichage
interface ImageResult {
  id: string
  title: string
  thumbnail: string
  url: string
  media_url: string
  source: string
  type: 'photo' | 'illustration' | 'vector' | 'gif'
  size: string
  dimensions: string
  resolution?: string
  quality?: string
  tags?: string[]
  score?: number
  date?: string
  format?: string
}

// État réactif 
const query = ref('')
const images = ref<ImageResult[]>([])
const isLoading = ref(false)
const error = ref('')
const totalResults = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(20)
const totalPages = ref(1)
const searchTime = ref<number | null>(null)

// Filtres
const imageType = ref('all')
const imageSize = ref('all')
const colorFilter = ref('all')
const orientationFilter = ref('all')
const licenceFilter = ref('all')

// Computed 
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// Formatter les types 
const formatType = (type: string) => {
  const types: Record<string, string> = {
    'photo': 'Photo',
    'illustration': 'Illustration',
    'vector': 'Vecteur',
    'gif': 'GIF',
    'web': 'Web',
    'diagram': 'Diagramme'
  }
  return types[type] || type.charAt(0).toUpperCase() + type.slice(1)
}

// Ouvrir une image 
const openImage = async (image: ImageResult) => {
  if (authStore.isAuthenticated) {
    try {
      const config = useRuntimeConfig()
      const baseURL = config.public.apiBaseUrl || 'http://localhost'
      await $fetch(`${baseURL}/api/history/clicks/`, {   // ← slash final
        method: 'POST',
        body: {
          result_id: image.id,
          query: query.value,
          url: image.url,
          type: 'image'
        },
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
    } catch (error) {
      console.error('Erreur lors du tracking du clic:', error)
    }
  }
  window.open(image.media_url || image.url, '_blank')
}

const onImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://via.placeholder.com/400x300?text=Image+non+disponible'
}


// Aller à une page 
const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  if (query.value) {
    router.push({
      path: '/images',
      query: { 
        q: query.value,
        page: page.toString(),
        type: imageType.value,
        size: imageSize.value,
        color: colorFilter.value,
        orientation: orientationFilter.value,
        licence: licenceFilter.value
      }
    })
    performSearch(query.value)
  }
}

// Effectuer la recherche d'images 
const performSearch = async (searchQuery: string) => {
  if (!searchQuery.trim()) {
    images.value = []
    totalResults.value = 0
    searchTime.value = null
    return
  }

  isLoading.value = true
  error.value = ''
  const startTime = Date.now()

  try {
    // Construction des paramètres de recherche (on utilise content_type=image)
    const params: Record<string, any> = {
      q: searchQuery,
      page: currentPage.value,
      limit: itemsPerPage.value,
      lang: 'fr',
      content_type: 'images'  //  pour ne récupérer que les pages avec images
    }

    // Ajouter les filtres uniquement s'ils ne sont pas "all" (mais le backend ne les supporte pas encore)
    // On les laisse pour l'instant, ils seront ignorés par le backend
    if (imageType.value !== 'all') params.image_type = imageType.value
    if (imageSize.value !== 'all') params.image_size = imageSize.value
    if (colorFilter.value !== 'all') params.color = colorFilter.value
    if (orientationFilter.value !== 'all') params.orientation = orientationFilter.value
    if (licenceFilter.value !== 'all') params.licence = licenceFilter.value

    // Appel API via nginx
    const response = await $fetch<SearchResponse>(SEARCH_API_URL, {
      method: 'GET',
      params,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })

    // Traitement de la réponse pour la transformer en format ImageResult
    if (response && Array.isArray(response.results)) {
      images.value = response.results.flatMap((item: any) => {
        // Récupérer les URLs d'images (tableau) ou fallback sur la miniature
        const imageUrls: string[] = item.image_urls || []
        const thumbnailFromResponse = item.thumbnail || ''
        
        // S'il y a plusieurs images, on les éclate
        if (imageUrls.length > 0) {
          return imageUrls.map((imgUrl: string, index: number) => ({
            id: `${item.id}_img${index}`,
            title: item.title || 'Image sans titre',
            thumbnail: imgUrl,
            url: item.url,
            media_url: imgUrl,
            source: item.domain || (() => { try { return new URL(item.url).hostname } catch { return 'inconnu' } })(),
            type: 'photo' as const,
            size: '',
            dimensions: '',
            resolution: '',
            quality: '',
            tags: item.keywords_found || [],
            score: item.score || 0,
            date: item.crawled_at || item.timestamp,
          }))
        }
        
        // Sinon, on crée une seule entrée avec la miniature (ancien comportement)
        if (thumbnailFromResponse) {
          return [{
            id: item.id,
            title: item.title || 'Image sans titre',
            thumbnail: thumbnailFromResponse,
            url: item.url,
            media_url: thumbnailFromResponse, // ouvrir l'image en grand
            source: item.domain || (() => { try { return new URL(item.url).hostname } catch { return 'inconnu' } })(),
            type: 'photo' as const,
            size: '',
            dimensions: '',
            resolution: '',
            quality: '',
            tags: item.keywords_found || [],
            score: item.score || 0,
            date: item.crawled_at || item.timestamp,
          }]
        }
        
        // Aucune image du tout → on ignore ce document
        return []
      })
      totalResults.value = response.total || response.results.length
      searchTime.value = response.processing_time || Date.now() - startTime
      totalPages.value = Math.ceil(totalResults.value / itemsPerPage.value)
      
      // Enregistrer dans l'historique
      if (authStore.isAuthenticated) {
        historyStore.addSearch(searchQuery, {
          type: 'images',
          results: images.value // ou totalResults.value 
        })
      }
    } else {
      console.warn('Format de réponse inattendu:', response)
      images.value = []
      totalResults.value = 0
      searchTime.value = Date.now() - startTime
    }

  } catch (err: any) {
    console.error('Erreur de recherche d\'images:', err)
    
    // Fallback : données de démonstration 
    if (err.statusCode === 404 || err.statusCode === 500) {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const mockData: any = {
        results: Array.from({ length: itemsPerPage.value }, (_, i) => ({
          id: `image-${i + (currentPage.value - 1) * itemsPerPage.value}`,
          title: `${searchQuery} - Image technique #${i + 1}`,
          thumbnail: `https://picsum.photos/400/300?random=${i + 1}&blur=2`,
          url: `https://picsum.photos/1920/1080?random=${i + 1}`,
          source: 'example.com',
          type: ['photo', 'illustration', 'vector', 'gif'][Math.floor(Math.random() * 4)] as any,
          size: `${Math.floor(Math.random() * 500) + 100} KB`,
          dimensions: `${Math.floor(Math.random() * 1000) + 800}x${Math.floor(Math.random() * 800) + 600}`,
          resolution: 'HD',
          quality: ['HD', 'Full HD', '2K'][Math.floor(Math.random() * 3)],
          tags: ['technique', searchQuery.toLowerCase(), 'informatique'],
          score: 0.9 - (i * 0.01)
        })),
        total: 124,
        took: 42
      }

      images.value = mockData.results
      totalResults.value = mockData.total
      searchTime.value = mockData.took
      totalPages.value = Math.ceil(totalResults.value / itemsPerPage.value)
    } else {
      error.value = err.message || 'Erreur de connexion au serveur d\'images'
      images.value = []
      totalResults.value = 0
      searchTime.value = null
    }
  } finally {
    isLoading.value = false
  }
}

// Surveiller les changements de filtres
watch([imageType, imageSize, colorFilter, orientationFilter, licenceFilter], () => {
  if (query.value) {
    currentPage.value = 1
    performSearch(query.value)
  }
})

// Initialisation au montage 
onMounted(() => {
  const routeQuery = route.query.q as string
  const routePage = parseInt(route.query.page as string) || 1
  const routeType = route.query.type as string
  const routeSize = route.query.size as string
  const routeColor = route.query.color as string
  const routeOrientation = route.query.orientation as string
  const routeLicence = route.query.licence as string
  
  if (routeQuery) {
    query.value = routeQuery
    currentPage.value = routePage
    if (routeType) imageType.value = routeType
    if (routeSize) imageSize.value = routeSize
    if (routeColor) colorFilter.value = routeColor
    if (routeOrientation) orientationFilter.value = routeOrientation
    if (routeLicence) licenceFilter.value = routeLicence
    performSearch(routeQuery)
  }
})

// Surveiller les changements d'URL 
watch(
  () => route.query,
  (newQuery) => {
    const routeQuery = newQuery.q as string
    const routePage = parseInt(newQuery.page as string) || 1
    const routeType = newQuery.type as string
    const routeSize = newQuery.size as string
    const routeColor = newQuery.color as string
    const routeOrientation = newQuery.orientation as string
    const routeLicence = newQuery.licence as string
    
    if (routeQuery) {
      query.value = routeQuery
      currentPage.value = routePage
      if (routeType) imageType.value = routeType
      if (routeSize) imageSize.value = routeSize
      if (routeColor) colorFilter.value = routeColor
      if (routeOrientation) orientationFilter.value = routeOrientation
      if (routeLicence) licenceFilter.value = routeLicence
      performSearch(routeQuery)
    } else {
      query.value = ''
      images.value = []
      totalResults.value = 0
      searchTime.value = null
    }
  }
)
</script>

<style scoped>
/* Animations et styles identiques aux autres pages */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animation-delay-4000 {
  animation-delay: 4s;
}
.animation-delay-1000 {
  animation-delay: 1s;
}

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
.aspect-square {
  aspect-ratio: 1 / 1;
}
.shadow-3xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
</style>