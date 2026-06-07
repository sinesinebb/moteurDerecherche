// plugins/api.ts
import { defineNuxtPlugin } from '#app'
import { useAuthStore } from '../stores/auth.store'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  
  // Vérifier le token au démarrage côté client
  if (typeof window !== 'undefined') {
    authStore.loadFromStorage()
  }
  console.log('Plugin auth: token chargé', authStore.token)
  const $api = $fetch.create({
    baseURL: config.public.apiBaseUrl || 'http://localhost/api',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    async onRequest({ request, options }) {
      // Ajouter le token d'authentification côté client
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token')
        if (token) {
          // Créer un nouvel objet headers pour éviter les problèmes de type
          const headers = new Headers(options.headers as HeadersInit)
          headers.set('Authorization', `Bearer ${token}`)
          options.headers = headers
        }
      }
    },
    onResponse({ response }) {
      return response._data
    },
    async onResponseError({ response }) {
      const status = response.status
      
      if (status === 401 && typeof window !== 'undefined') {
        // Nettoyer le localStorage
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('isAuthenticated')
        
        // Rediriger vers la page de login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login?session=expired'
        }
      }
      
      throw new Error(response._data?.detail || response._data?.message || 'Une erreur est survenue')
    }
  })
  
  // Fournir l'instance API
  nuxtApp.provide('api', $api)
})