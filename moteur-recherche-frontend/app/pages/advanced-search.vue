<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-white dark:bg-[#202124]']">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Titre -->
      <div class="mb-8">
        <h1 class="text-2xl font-normal text-gray-900 dark:text-white">
          Recherche avancée
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Filtres puissants pour vos recherches techniques
        </p>
      </div>

      <!-- Formulaire -->
      <form @submit.prevent="performAdvancedSearch" class="space-y-6">
        <!-- Barre de recherche principale -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
            Requête principale
          </label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Ex : Python Django déploiement API REST"
            class="w-full px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-[#303134] text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Utilisez guillemets pour une expression exacte, opérateurs AND, OR, NOT.
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Colonne gauche : filtres structurés -->
          <div class="space-y-4">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">Filtres structurés</h3>

            <!-- Type de contenu -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-2">Type de contenu</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="type in documentTypes"
                  :key="type.value"
                  type="button"
                  @click="toggleArrayItem(filters.documentTypes, type.value)"
                  :class="[
                    'px-2 py-1 text-xs rounded border',
                    filters.documentTypes.includes(type.value)
                      ? 'bg-blue-50 border-blue-300 text-blue-700 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-300'
                      : 'bg-white border-gray-300 text-gray-700 dark:bg-[#303134] dark:border-gray-600 dark:text-gray-300 hover:border-gray-400'
                  ]"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>

            <!-- Domaine technique -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-2">Domaine technique</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="domain in technicalDomains"
                  :key="domain.value"
                  type="button"
                  @click="toggleArrayItem(filters.domains, domain.value)"
                  :class="[
                    'px-2 py-1 text-xs rounded border',
                    filters.domains.includes(domain.value)
                      ? 'bg-blue-50 border-blue-300 text-blue-700 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-300'
                      : 'bg-white border-gray-300 text-gray-700 dark:bg-[#303134] dark:border-gray-600 dark:text-gray-300 hover:border-gray-400'
                  ]"
                >
                  {{ domain.label }}
                </button>
              </div>
            </div>

            <!-- Langue -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Langue</label>
              <select
                v-model="filters.language"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-[#303134] text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Toutes les langues</option>
                <option value="fr">Français</option>
                <option value="en">Anglais</option>
                <option value="es">Espagnol</option>
                <option value="de">Allemand</option>
              </select>
            </div>

            <!-- Plage de dates -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-2">Date de publication</label>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-gray-500 dark:text-gray-400">Du</label>
                  <input
                    v-model="filters.dateFrom"
                    type="date"
                    class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-[#303134] text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="text-xs text-gray-500 dark:text-gray-400">Au</label>
                  <input
                    v-model="filters.dateTo"
                    type="date"
                    class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-[#303134] text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- Colonne droite : paramètres avancés -->
          <div class="space-y-4">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">Paramètres avancés</h3>

            <!-- Mots-clés à exclure -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Technologies / mots à exclure
              </label>
              <div class="flex flex-wrap gap-1 p-2 bg-white dark:bg-[#303134] border border-gray-300 dark:border-gray-600 rounded-md min-h-[36px]">
                <span
                  v-for="(tag, index) in filters.excludeTags"
                  :key="index"
                  class="inline-flex items-center px-2 py-0.5 text-xs rounded bg-red-50 border border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300"
                >
                  {{ tag }}
                  <button type="button" @click="filters.excludeTags.splice(index, 1)" class="ml-1 focus:outline-none">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </span>
                <input
                  v-model="newExcludeTag"
                  @keydown.enter.prevent="addExcludeTag"
                  @keydown.comma.prevent="addExcludeTag"
                  type="text"
                  placeholder="Ajouter un mot-clé..."
                  class="flex-1 min-w-[120px] bg-transparent border-none focus:outline-none text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                >
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Entrée ou virgule pour ajouter. Ex : Java, PHP, .NET
              </p>
            </div>

            <!-- Seuil de pertinence -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Niveau de pertinence minimum
              </label>
              <div class="flex gap-2">
                <button
                  v-for="level in relevanceLevels"
                  :key="level.value"
                  type="button"
                  @click="filters.relevance = level.value"
                  :class="[
                    'flex-1 py-1 px-2 text-xs rounded border',
                    filters.relevance === level.value
                      ? 'bg-blue-50 border-blue-300 text-blue-700 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-300'
                      : 'bg-white border-gray-300 text-gray-700 dark:bg-[#303134] dark:border-gray-600 dark:text-gray-300 hover:border-gray-400'
                  ]"
                >
                  {{ level.label }}
                </button>
              </div>
            </div>

            <!-- Sites restreints -->
            <div>
              <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Restreindre aux sites
              </label>
              <input
                v-model="filters.siteRestriction"
                type="text"
                placeholder="docs.python.org, developer.mozilla.org"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-[#303134] text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Séparez les domaines par des virgules.
              </p>
            </div>
          </div>
        </div>

        <!-- Boutons d'action -->
        <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="submit"
            :disabled="isSearching"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            <svg v-if="isSearching" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ isSearching ? 'Recherche en cours…' : 'Lancer la recherche' }}
          </button>
          <button
            type="button"
            @click="resetForm"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-[#303134] border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            Réinitialiser tous les filtres
          </button>
        </div>
      </form>

      <!-- Guide des opérateurs booléens -->
      <div class="mt-8 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
        <h3 class="text-lg font-normal text-gray-900 dark:text-white mb-3">
          Syntaxe de recherche avancée
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div class="space-y-2">
            <div class="flex items-start gap-2">
              <span class="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-1 rounded">AND</span>
              <span class="text-gray-600 dark:text-gray-400">Python AND Django → les deux termes</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-1 rounded">OR</span>
              <span class="text-gray-600 dark:text-gray-400">React OR Vue → l'un ou l'autre</span>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex items-start gap-2">
              <span class="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-1 rounded">NOT</span>
              <span class="text-gray-600 dark:text-gray-400">Java NOT Spring → Java sans Spring</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-1 rounded">" "</span>
              <span class="text-gray-600 dark:text-gray-400">"machine learning" → expression exacte</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

import { ref } from 'vue'
import { useRouter } from '#app'
import { useThemeStore } from '../../stores/theme.store'

const router = useRouter()
const themeStore = useThemeStore()

// Requête principale
const searchQuery = ref('')

// Tags d'exclusion
const newExcludeTag = ref('')

// Filtres structurés
const filters = ref({
  documentTypes: [] as string[],        // types sélectionnés
  domains: [] as string[],              // domaines techniques
  language: '',
  dateFrom: '',
  dateTo: '',
  relevance: 'medium',                  // 'low', 'medium', 'high'
  excludeTags: [] as string[],
  siteRestriction: ''                   // domaines séparés par des virgules
})

// Options
const documentTypes = [
  { value: 'tutorial', label: 'Tutoriel' },
  { value: 'documentation', label: 'Documentation' },
  { value: 'api', label: 'API' },
  { value: 'article', label: 'Article' },
  { value: 'research', label: 'Recherche' },
  { value: 'video', label: 'Vidéo' },
  { value: 'pdf', label: 'PDF' },
  { value: 'github', label: 'GitHub' }
]

const technicalDomains = [
  { value: 'web', label: 'Web' },
  { value: 'mobile', label: 'Mobile' },
  { value: 'data', label: 'Data Science' },
  { value: 'ai', label: 'IA / ML' },
  { value: 'devops', label: 'DevOps' },
  { value: 'security', label: 'Cybersécurité' },
  { value: 'cloud', label: 'Cloud' },
  { value: 'database', label: 'Bases de données' },
  { value: 'language', label: 'Langages' },
  { value: 'architecture', label: 'Architecture' }
]

const relevanceLevels = [
  { value: 'low', label: 'Faible' },
  { value: 'medium', label: 'Moyen' },
  { value: 'high', label: 'Élevé' }
]

const isSearching = ref(false)

// Utilitaires pour les tableaux
const toggleArrayItem = (arr: string[], value: string) => {
  const index = arr.indexOf(value)
  if (index === -1) {
    arr.push(value)
  } else {
    arr.splice(index, 1)
  }
}

const addExcludeTag = () => {
  const tag = newExcludeTag.value.trim().replace(/,/g, '')
  if (tag && !filters.value.excludeTags.includes(tag)) {
    filters.value.excludeTags.push(tag)
  }
  newExcludeTag.value = ''
}

// Recherche
const performAdvancedSearch = async () => {
  isSearching.value = true
  
  const queryParams: any = {
    q: searchQuery.value.trim() || '',
    advanced: 'true'
  }

  if (filters.value.documentTypes.length > 0) {
    queryParams.type = filters.value.documentTypes.join(',')
  }
  if (filters.value.domains.length > 0) {
    queryParams.domain = filters.value.domains.join(',')
  }
  if (filters.value.language) {
    queryParams.lang = filters.value.language
  }
  if (filters.value.dateFrom) {
    queryParams.from = filters.value.dateFrom
  }
  if (filters.value.dateTo) {
    queryParams.to = filters.value.dateTo
  }
  if (filters.value.relevance) {
    // Mapper 'low' → 0.3, 'medium' → 0.5, 'high' → 0.8 pour le backend
    const minScoreMap: Record<string, number> = { low: 0.3, medium: 0.5, high: 0.8 }
    queryParams.min_score = minScoreMap[filters.value.relevance]
  }
  if (filters.value.excludeTags.length > 0) {
    queryParams.exclude = filters.value.excludeTags.join(',')
  }
  if (filters.value.siteRestriction) {
    queryParams.sites = filters.value.siteRestriction
  }

  // Simulation de délai (pour l'UX) – à retirer une fois l'API branchée
  await new Promise(resolve => setTimeout(resolve, 800))

  router.push({
    path: '/search',
    query: queryParams
  })

  isSearching.value = false
}

const resetForm = () => {
  searchQuery.value = ''
  filters.value = {
    documentTypes: [],
    domains: [],
    language: '',
    dateFrom: '',
    dateTo: '',
    relevance: 'medium',
    excludeTags: [],
    siteRestriction: ''
  }
  newExcludeTag.value = ''
}
</script>

<style scoped>
@keyframes fade-in-down {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-down {
  animation: fade-in-down 0.6s ease-out;
}
</style>