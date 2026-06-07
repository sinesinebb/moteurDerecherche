import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDarkMode: false,
    theme: 'light' as 'light' | 'dark',
  }),

  actions: {
    initializeTheme() {
      if (typeof window === 'undefined') return
      
      const savedTheme = localStorage.getItem('theme')
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      
      if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        this.enableDarkMode()
      } else {
        this.enableLightMode()
      }
    },

    enableDarkMode() {
      this.isDarkMode = true
      this.theme = 'dark'
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    },

    enableLightMode() {
      this.isDarkMode = false
      this.theme = 'light'
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    },

    toggleTheme() {
      if (this.isDarkMode) {
        this.enableLightMode()
      } else {
        this.enableDarkMode()
      }
    },
  },
})