<!-- moteur-recherche-frontend/components/ui/AdvancedPagination.vue -->
<template>
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
    <div class="text-sm text-gray-700 dark:text-gray-400">
      Affichage de <span class="font-semibold">{{ startItem }}</span> 
      à <span class="font-semibold">{{ endItem }}</span> 
      sur <span class="font-semibold">{{ totalItems }}</span> résultats
      <span v-if="searchTime" class="ml-2 text-gray-500 dark:text-gray-500">
        • {{ searchTime }}ms
      </span>
    </div>
    
    <nav class="flex items-center space-x-2">
      <!-- Bouton précédent -->
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        :class="[
          'px-4 py-2 rounded-xl border text-sm font-medium transition-all duration-200 flex items-center',
          currentPage === 1
            ? 'bg-gray-100/50 dark:bg-gray-800/50 text-gray-400 dark:text-gray-600 border-gray-300/50 dark:border-gray-700/50 cursor-not-allowed'
            : 'bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 border-gray-300/50 dark:border-gray-600/50 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 hover:scale-105'
        ]"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Précédent
      </button>
      
      <!-- Pages -->
      <div class="flex items-center space-x-1">
        <!-- Première page -->
        <button
          v-if="showFirstPage"
          @click="goToPage(1)"
          :class="[
            'w-10 h-10 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-center',
            1 === currentPage
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-105'
              : 'bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 border border-gray-300/50 dark:border-gray-600/50 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 hover:scale-105'
          ]"
        >
          1
        </button>
        
        <!-- Ellipsis avant -->
        <span v-if="showEllipsisBefore" class="px-2 text-gray-400 dark:text-gray-600">...</span>
        
        <!-- Pages intermédiaires -->
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="goToPage(page)"
          :class="[
            'w-10 h-10 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-center',
            page === currentPage
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-105'
              : 'bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 border border-gray-300/50 dark:border-gray-600/50 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 hover:scale-105'
          ]"
        >
          {{ page }}
        </button>
        
        <!-- Ellipsis après -->
        <span v-if="showEllipsisAfter" class="px-2 text-gray-400 dark:text-gray-600">...</span>
        
        <!-- Dernière page -->
        <button
          v-if="showLastPage"
          @click="goToPage(totalPages)"
          :class="[
            'w-10 h-10 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-center',
            totalPages === currentPage
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-105'
              : 'bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 border border-gray-300/50 dark:border-gray-600/50 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 hover:scale-105'
          ]"
        >
          {{ totalPages }}
        </button>
      </div>
      
      <!-- Sélecteur de page -->
      <div class="relative">
        <select
          :value="currentPage"
          @change="onPageSelectChange"
          class="px-3 py-2 bg-white/80 dark:bg-gray-800/80 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none pl-3 pr-8"
        >
          <option v-for="page in totalPages" :key="page" :value="page">
            Page {{ page }}
          </option>
        </select>
        <div class="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      
      <!-- Bouton suivant -->
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        :class="[
          'px-4 py-2 rounded-xl border text-sm font-medium transition-all duration-200 flex items-center',
          currentPage === totalPages
            ? 'bg-gray-100/50 dark:bg-gray-800/50 text-gray-400 dark:text-gray-600 border-gray-300/50 dark:border-gray-700/50 cursor-not-allowed'
            : 'bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 border-gray-300/50 dark:border-gray-600/50 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 hover:scale-105'
        ]"
      >
        Suivant
        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
      
      <!-- Sélecteur d'éléments par page -->
      <div class="relative">
        <select
          :value="itemsPerPage"
          @change="updateItemsPerPage"
          class="px-3 py-2 bg-white/80 dark:bg-gray-800/80 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none pl-3 pr-8"
        >
          <option value="10">10/page</option>
          <option value="20">20/page</option>
          <option value="50">50/page</option>
          <option value="100">100/page</option>
        </select>
        <div class="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    required: true
  },
  searchTime: {
    type: Number,
    default: null
  },
  maxVisiblePages: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits<{
  'page-change': [page: number]
  'items-per-page-change': [itemsPerPage: number]
}>()

// Calculs
const totalPages = computed(() => Math.ceil(props.totalItems / props.itemsPerPage))
const startItem = computed(() => (props.currentPage - 1) * props.itemsPerPage + 1)
const endItem = computed(() => Math.min(props.currentPage * props.itemsPerPage, props.totalItems))

// Pages visibles
const visiblePages = computed(() => {
  const pages = []
  const half = Math.floor(props.maxVisiblePages / 2)
  let start = Math.max(1, props.currentPage - half)
  let end = Math.min(totalPages.value, start + props.maxVisiblePages - 1)
  
  // Ajuster si on est proche de la fin
  if (end - start + 1 < props.maxVisiblePages) {
    start = Math.max(1, end - props.maxVisiblePages + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Affichage des ellipsis
const showFirstPage = computed(() => visiblePages.value[0] > 1)
const showLastPage = computed(() => visiblePages.value[visiblePages.value.length - 1] < totalPages.value)
const showEllipsisBefore = computed(() => visiblePages.value[0] > 2)
const showEllipsisAfter = computed(() => visiblePages.value[visiblePages.value.length - 1] < totalPages.value - 1)

// Navigation
const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value || page === props.currentPage) return
  emit('page-change', page)
}

const onPageSelectChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const page = parseInt(target.value, 10)
  if (!isNaN(page)) {
    goToPage(page)
  }
}

const updateItemsPerPage = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const itemsPerPage = parseInt(target.value, 10)
  if (!isNaN(itemsPerPage)) {
    emit('items-per-page-change', itemsPerPage)
  }
}
</script>