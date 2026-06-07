// plugins/auth.client.ts
import { defineNuxtPlugin } from '#app'
import { useAuthStore } from '../stores/auth.store'

export default defineNuxtPlugin({
  name: 'auth-client',
  enforce: 'pre',
  setup() {
    // Vérifier si on est côté client
    if (typeof window !== 'undefined') {
      const authStore = useAuthStore()
      
      // Charger l'état depuis le localStorage
      authStore.loadFromStorage()
      
      // Vérifier la validité du token au démarrage
      const checkToken = () => {
        if (authStore.token) {
          try {
            const payload = JSON.parse(atob(authStore.token.split('.')[1]))
            const now = Math.floor(Date.now() / 1000)
            if (payload.exp < now) {
              // Token expiré, essayer de le rafraîchir
              authStore.refreshAuthToken()
            }
          } catch (error) {
            console.error('Erreur de vérification du token:', error)
          }
        }
      }
      
      checkToken()
    }
  }
})