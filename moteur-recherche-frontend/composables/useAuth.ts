// composables/useAuth.ts
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth.store'

export const useAuth = () => {
  const authStore = useAuthStore()
  
  // Charger l'état depuis le localStorage au démarrage
  if (process.client && typeof window !== 'undefined') {
    authStore.loadFromStorage()
  }
  
  const login = async (credentials: { email: string; password: string }) => {
    return await authStore.login(credentials)
  }
  
  const register = async (userData: { email: string; password: string; name: string }) => {
    return await authStore.register(userData)
  }
  
  const logout = async () => {
    await authStore.logout()
  }
  
  const getAuthHeaders = () => {
    if (!authStore.token) return {}
    return {
      'Authorization': `Bearer ${authStore.token}`,
      'X-User-Id': authStore.user?.id || ''
    }
  }
  
  const refreshToken = async () => {
    return await authStore.refreshAuthToken()
  }
  
  // Vérifier si le token est valide
  const checkTokenValidity = () => {
    if (!authStore.token) return false
    
    try {
      const payload = JSON.parse(atob(authStore.token.split('.')[1]))
      const now = Math.floor(Date.now() / 1000)
      return payload.exp > now
    } catch {
      return false
    }
  }
  
  return {
    // États
    user: computed(() => authStore.user),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    isAdmin: computed(() => authStore.isAdmin),
    token: computed(() => authStore.token),
    isLoading: computed(() => authStore.loading),
    error: computed(() => authStore.error),
    
    // Méthodes
    login,
    register,
    logout,
    refreshToken,
    getAuthHeaders,
    checkTokenValidity
  }
}