/**
 * Utilitaires pour la gestion des tokens JWT
 */

// Décode un token JWT (partie payload)
export const decodeJWT = (token: string): any | null => {
  try {
    // Un vrai JWT a 3 parties séparées par des points
    const parts = token.split('.')
    if (parts.length !== 3) {
      // Notre token simulé est juste en base64
      return JSON.parse(atob(token))
    }
    
    // Pour un vrai JWT
    const base64Url = parts[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Error decoding JWT:', error)
    return null
  }
}

// Vérifie si un token JWT est expiré
export const isTokenExpired = (token: string): boolean => {
  const decoded = decodeJWT(token)
  if (!decoded || !decoded.exp) return true
  
  const currentTime = Math.floor(Date.now() / 1000)
  return decoded.exp < currentTime
}

// Extrait l'utilisateur depuis le token
export const getUserFromToken = (token: string): any | null => {
  const decoded = decodeJWT(token)
  if (!decoded) return null
  
  return {
    id: decoded.sub || decoded.id,
    email: decoded.email,
    name: decoded.name || `${decoded.first_name || ''} ${decoded.last_name || ''}`.trim(),
    role: decoded.role || (decoded.is_superuser ? 'admin' : 'user')
  }
}

// Fonction pour utiliser les cookies (version compatible SSR)
const useAuthCookie = (name: string, options?: any) => {
  if (process.server) return { value: null }
  
  // Créer un cookie simple côté client
  return {
    get value() {
      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
      return match ? decodeURIComponent(match[2]) : null
    },
    set value(val: string | null) {
      if (val === null) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
      } else {
        const cookieOptions = {
          maxAge: options?.maxAge || 60 * 60 * 24,
          sameSite: options?.sameSite || 'strict',
          secure: options?.secure || process.env.NODE_ENV === 'production',
          path: '/'
        }
        
        let cookieString = `${name}=${encodeURIComponent(val)}`
        if (cookieOptions.maxAge) cookieString += `; max-age=${cookieOptions.maxAge}`
        if (cookieOptions.sameSite) cookieString += `; samesite=${cookieOptions.sameSite}`
        if (cookieOptions.secure) cookieString += `; secure`
        cookieString += `; path=${cookieOptions.path}`
        
        document.cookie = cookieString
      }
    }
  }
}

// Stocke le token dans les cookies (pour SSR)
export const setAuthCookies = (token: string, refreshToken?: string) => {
  if (process.client && typeof window !== 'undefined') {
    const tokenCookie = useAuthCookie('auth_token', {
      maxAge: 60 * 60 * 24, // 24h
      sameSite: 'strict',
      secure: process.env.NODE_ENV === 'production'
    })
    
    tokenCookie.value = token
    
    if (refreshToken) {
      const refreshCookie = useAuthCookie('auth_refresh_token', {
        maxAge: 60 * 60 * 24 * 7, // 7 jours
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production'
      })
      
      refreshCookie.value = refreshToken
    }
  }
}

// Nettoie les cookies d'authentification
export const clearAuthCookies = () => {
  if (process.client && typeof window !== 'undefined') {
    const tokenCookie = useAuthCookie('auth_token')
    tokenCookie.value = null
    
    const refreshCookie = useAuthCookie('auth_refresh_token')
    refreshCookie.value = null
    
    const userCookie = useAuthCookie('auth_user')
    userCookie.value = null
  }
}

// Vérifie les permissions depuis le token
export const checkPermission = (token: string, requiredRole: 'user' | 'admin'): boolean => {
  const user = getUserFromToken(token)
  if (!user) return false
  
  if (requiredRole === 'admin' && user.role !== 'admin') return false
  return true
}