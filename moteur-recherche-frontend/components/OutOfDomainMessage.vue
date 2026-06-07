<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center">
    <div class="relative mb-8">
      <div class="w-32 h-32 rounded-full bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/20 dark:to-cyan-900/20 flex items-center justify-center shadow-lg">
        <svg class="w-16 h-16 text-blue-500 dark:text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="absolute -top-2 -right-2 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center shadow-md">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    </div>
    <h2 class="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-3">
      Domaine non supporté
    </h2>
    <p class="text-gray-500 dark:text-gray-400 max-w-md">
      {{ message }}
    </p>
    <div class="mt-6 flex flex-wrap justify-center gap-2">
      <button
        v-for="suggestion in suggestions"
        :key="suggestion"
        @click="$emit('search', suggestion)"
        class="px-4 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-full hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
      >
        {{ suggestion }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string
  suggestions?: string[]
}>()
defineEmits(['search'])
</script>