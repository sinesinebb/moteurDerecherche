<template>
  <button
    @click="toggleTheme"
    class="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    aria-label="Changer le thème"
  >
    <i v-if="themeStore.isDarkMode" class="fas fa-sun text-yellow-500 text-lg"></i>
    <i v-else class="fas fa-moon text-gray-600 dark:text-gray-400 text-lg"></i>
  </button>
</template>

<script setup lang="ts">
import { useThemeStore } from '../../stores/theme.store'

const themeStore = useThemeStore()

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>