// plugins/auth-init.ts
import { defineNuxtPlugin } from '#app'
import { useAuthStore } from '../stores/auth.store'

export default defineNuxtPlugin(() => {
  const authStore = useAuthStore()
  // Charger les données du localStorage immédiatement
  authStore.loadFromStorage()
})