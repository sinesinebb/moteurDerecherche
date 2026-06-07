<!-- moteur-recherche-frontend/components/search/SearchFilters.vue -->
<template>
  <div class="flex flex-wrap gap-3">
    <div class="relative">
      <select 
        v-model="selectedType"
        @change="emitFilters"
        class="px-5 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-gray-300/50 dark:border-gray-700/50 rounded-xl text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-600 appearance-none pr-10"
      >
        <option value="all">Tous types</option>
        <option value="web">Web</option>
        <option value="documentation">Documentation</option>
        <option value="tutorial">Tutoriel</option>
        <option value="video">Vidéo</option>
        <option value="image">Image</option>
      </select>
      <div class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
    
    <div class="relative">
      <select 
        v-model="selectedSort"
        @change="emitFilters"
        class="px-5 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-gray-300/50 dark:border-gray-700/50 rounded-xl text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-600 appearance-none pr-10"
      >
        <option value="relevance">Pertinence</option>
        <option value="date_desc">Plus récent</option>
        <option value="date_asc">Plus ancien</option>
        <option value="pagerank">Popularité</option>
      </select>
      <div class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
    
    <div class="relative">
      <select 
        v-model="selectedDate"
        @change="emitFilters"
        class="px-5 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-gray-300/50 dark:border-gray-700/50 rounded-xl text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-600 appearance-none pr-10"
      >
        <option value="all">Toutes dates</option>
        <option value="today">Aujourd'hui</option>
        <option value="week">Cette semaine</option>
        <option value="month">Ce mois</option>
        <option value="year">Cette année</option>
      </select>
      <div class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedType = ref('all')
const selectedSort = ref('relevance')
const selectedDate = ref('all')

const emit = defineEmits(['filter-change'])

const emitFilters = () => {
  emit('filter-change', {
    type: selectedType.value,
    sort: selectedSort.value,
    date: selectedDate.value
  })
}
</script>