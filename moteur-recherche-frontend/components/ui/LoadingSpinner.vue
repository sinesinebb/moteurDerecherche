<!-- moteur-recherche-frontend/components/ui/LoadingSpinner.vue -->
<template>
  <div class="text-center py-8">
    <div class="relative inline-block">
      <div class="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 animate-spin"></div>
      <div class="absolute inset-0 flex items-center justify-center">
        <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>
    <p class="mt-4 text-gray-600 dark:text-gray-400">
      {{ message || 'Chargement en cours...' }}
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps({
  message: {
    type: String,
    default: ''
  }
})
</script>