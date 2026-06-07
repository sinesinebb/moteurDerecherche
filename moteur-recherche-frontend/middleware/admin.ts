// middleware/admin.ts
import { navigateTo } from '#app'

export default defineNuxtRouteMiddleware((to, from) => {
  if (process.client) {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (!token || !userStr) {
      return navigateTo('/login')
    }

    try {
      const user = JSON.parse(userStr)
      if (!user.is_superuser && user.role !== 'admin') {
        return navigateTo('/')
      }
    } catch {
      return navigateTo('/login')
    }
  }
})