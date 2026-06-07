<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gray-50 dark:bg-gray-900']">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- En-tête -->
      <div class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Historique de recherche</h1>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ historyStore.items.length }} recherche(s)
              <span v-if="historyStore.loading" class="ml-2 inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></span>
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <button 
            @click="historyStore.clearHistory()"
            class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
          >
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Effacer tout
          </button>
          <button 
            @click="exportHistory"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition shadow-sm"
          >
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Exporter
          </button>
        </div>
      </div>

      <!-- Non connecté -->
      <div v-if="!authStore.isAuthenticated" class="text-center py-16">
        <div class="w-24 h-24 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Connectez-vous</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">Pour accéder à votre historique de recherche</p>
        <div class="flex justify-center gap-4">
          <NuxtLink to="/login" class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">Se connecter</NuxtLink>
          <NuxtLink to="/register" class="px-5 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition">S'inscrire</NuxtLink>
        </div>
      </div>

      <!-- Chargement -->
      <div v-else-if="historyStore.loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
        <p class="text-gray-600 dark:text-gray-400">Chargement de l'historique...</p>
      </div>

      <!-- Historique vide -->
      <div v-else-if="historyStore.items.length === 0" class="text-center py-16">
        <div class="w-24 h-24 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Aucune recherche</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">Vos recherches apparaîtront ici</p>
        <NuxtLink to="/search" class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">Effectuer une recherche</NuxtLink>
      </div>

      <!-- Grille d'historique -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Liste des recherches -->
        <div class="lg:col-span-2 space-y-4">
          <div 
            v-for="item in historyStore.items" 
            :key="item.id"
            class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition"
          >
            <!-- Date + actions -->
            <div class="flex justify-between items-start mb-3">
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(item.created_at) }} à {{ formatTime(item.created_at) }}
              </div>
              <div class="flex items-center gap-2">
                <button 
                  @click="repeatSearch(item)"
                  class="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                >
                  Refaire
                </button>
                <button 
                  @click="historyStore.removeHistoryItem(item.id)"
                  class="text-gray-400 hover:text-red-500 transition"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Requête -->
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ item.query }}
            </h3>

            <!-- Badges -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                {{ item.total_results }} résultat(s)
              </span>
              <span v-if="item.execution_time" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                {{ item.execution_time }} ms
              </span>
              <span v-if="item.filters?.type" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                Type : {{ formatType(item.filters.type) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Sidebar statistiques -->
        <div class="space-y-6">
          <!-- Statistiques générales -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Statistiques</h3>
            <div class="space-y-3">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600 dark:text-gray-400">Recherches totales</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ historyStore.items.length }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600 dark:text-gray-400">Aujourd'hui</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ getTodayCount() }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600 dark:text-gray-400">7 derniers jours</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ getLastWeekCount() }}</span>
              </div>
            </div>
            <hr class="my-4 border-gray-200 dark:border-gray-700">
            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recherches récurrentes</h4>
            <div v-if="getMostFrequentQuery()" class="text-sm text-gray-900 dark:text-white">
              <span class="text-gray-500 dark:text-gray-400">La plus fréquente :</span> {{ getMostFrequentQuery() }}
            </div>
            <div v-else class="text-sm text-gray-500">Aucune donnée</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  requiresAuth: true
})

import { useRouter } from '#app'
import { useThemeStore } from '../../stores/theme.store'
import { useAuthStore } from '../../stores/auth.store'
import { useHistoryStore } from '../../stores/history.store'
import { watch, onUnmounted } from 'vue'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const historyStore = useHistoryStore()

// Formatters
const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return "Aujourd'hui"
    if (diffDays === 1) return 'Hier'
    if (diffDays < 7) return `Il y a ${diffDays} jours`
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch { return 'Date inconnue' }
}

const formatTime = (dateString: string) => {
  try {
    return new Date(dateString).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

const formatType = (type: string) => {
  const map: Record<string, string> = {
    search: 'Tous', images: 'Images', videos: 'Vidéos', docs: 'Documents',
    web: 'Web', documentation: 'Documentation', tutorial: 'Tutoriel', api: 'API'
  }
  return map[type] || type
}

// Actions
const repeatSearch = (item: any) => {
  router.push({ path: '/search', query: { q: item.query } })
}

const exportHistory = () => {
  const data = JSON.stringify(historyStore.items, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'historique-recherches.json'
  a.click()
  URL.revokeObjectURL(url)
}

// Statistiques calculées
const getTodayCount = () => {
  const today = new Date().toDateString()
  return historyStore.items.filter(item => new Date(item.created_at).toDateString() === today).length
}

const getLastWeekCount = () => {
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  return historyStore.items.filter(item => new Date(item.created_at) >= weekAgo).length
}

const getMostFrequentQuery = () => {
  if (!historyStore.items.length) return null
  const freq: Record<string, number> = {}
  historyStore.items.forEach(item => freq[item.query] = (freq[item.query] || 0) + 1)
  return Object.entries(freq).sort((a, b) => b[1] - a[1])[0]?.[0] || null
}

// Charger l'historique dès que l'utilisateur est authentifié
const stopWatcher = watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      historyStore.fetchHistory()
    } else {
      historyStore.items = []
    }
  },
  { immediate: true }
)

// Nettoyer le watcher à la destruction du composant
onUnmounted(() => {
  stopWatcher()
})
</script>