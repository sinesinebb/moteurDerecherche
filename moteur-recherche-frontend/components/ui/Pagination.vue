<!-- moteur-recherche-frontend/components/ui/Pagination.vue -->
<template>
  <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="text-gray-700 dark:text-gray-300">
        Page <span class="font-bold text-blue-600 dark:text-blue-400">{{ currentPage }}</span> 
        sur <span class="font-bold text-gray-900 dark:text-white">{{ totalPages }}</span>
        • <span class="text-gray-600 dark:text-gray-400">
          Affichage de <span class="font-semibold">{{ startItem }}</span>
          à <span class="font-semibold">{{ endItem }}</span>
          sur <span class="font-semibold">{{ totalItems }}</span> résultats
        </span>
      </div>
      
      <nav class="flex items-center space-x-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'px-5 py-2.5 rounded-xl border text-sm font-medium transition-all duration-200 flex items-center',
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
        
        <div class="flex items-center space-x-1">
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
        </div>
        
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          :class="[
            'px-5 py-2.5 rounded-xl border text-sm font-medium transition-all duration-200 flex items-center',
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
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 20
  }
})

const emit = defineEmits(['page-change'])

const startItem = computed(() => {
  return (props.currentPage - 1) * props.itemsPerPage + 1
})

const endItem = computed(() => {
  return Math.min(props.currentPage * props.itemsPerPage, props.totalItems)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, props.currentPage - 2)
  const end = Math.min(props.totalPages, props.currentPage + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const goToPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('page-change', page)
  }
}
</script>