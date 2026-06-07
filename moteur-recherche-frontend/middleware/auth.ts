import { useAuthStore } from '../stores/auth.store'
import { navigateTo } from '#imports'

export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  if (process.client) {
    authStore.loadFromStorage()
  }
  
  // Vérifier l'authentification
  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }
  
})