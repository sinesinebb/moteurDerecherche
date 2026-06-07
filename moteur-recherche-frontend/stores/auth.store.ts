// stores/auth.store.ts

import { defineStore } from 'pinia'

// Interfaces
interface User {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
  avatar?: string
  first_name?: string
  last_name?: string
  is_superuser?: boolean
  is_2fa_enabled?: boolean
  email_verified?: boolean  // Ajout
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  email: string
  password: string
  name: string
}

// Fonction pour créer l'instance API
const createApi = () => {
  const config = useRuntimeConfig()
  console.log('API baseURL:', config.public.apiBaseUrl)
  return $fetch.create({
    baseURL: config.public.apiBaseUrl || 'http://localhost',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    credentials: 'include'
  })
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: null as string | null,
    refreshToken: null as string | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null,
    is2FAEnabled: false,
    sessionId: null as string | null,
  }),

  getters: {
    displayName: (state) => state.user?.name || 'Utilisateur',
    userEmail: (state) => state.user?.email || '',
    userInitial: (state) => state.user?.name?.charAt(0).toUpperCase() || 'U',
    userPhoto: (state) => state.user?.avatar || null,
    isAdmin: (state) => {
      if (!state.user) return false
      return state.user.role === 'admin' || 
             state.user.is_superuser === true ||
             state.user.email?.includes('admin') ||
             state.user.email === 'admin@search.dev'
    },
    userRole: (state) => state.user?.role || 'user',
    getToken: (state) => state.token,
  },

  actions: {
    async login(credentials: LoginCredentials) {
      try {
        this.loading = true
        this.error = null
        
        const api = createApi()
        
        const response = await api('/api/auth/login/', {
          method: 'POST',
          body: {
            email: credentials.email,
            password: credentials.password
          }
        }) as any
        
        console.log('Login - token reçu:', response.access)
        console.log('Login - user reçu:', response.user)
        
        this.token = response.access
        this.refreshToken = response.refresh
        this.sessionId = response.session_id
        this.user = {
          id: response.user.id,
          email: response.user.email,
          name: `${response.user.first_name || ''} ${response.user.last_name || ''}`.trim() || response.user.username,
          role: response.user.is_superuser ? 'admin' : 'user',
          first_name: response.user.first_name,
          last_name: response.user.last_name,
          is_superuser: response.user.is_superuser,
          is_2fa_enabled: response.user.is_2fa_enabled || false,
          email_verified: response.user.email_verified || false
        }
        this.is2FAEnabled = response.user.is_2fa_enabled || false
        this.isAuthenticated = true
        
        this.saveToStorage()
        
        return { success: true, data: response }
      } catch (error: any) {
        console.error('Login error:', error)
        this.error = error.data?.detail || error.message || 'Échec de la connexion'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async register(userData: RegisterData) {
      try {
        this.loading = true
        this.error = null
        
        const api = createApi()
        
        const nameParts = userData.name.trim().split(' ')
        const firstName = nameParts[0] || ''
        const lastName = nameParts.slice(1).join(' ') || ''
        const username = userData.name.toLowerCase()
          .replace(/\s+/g, '_')
          .replace(/[^a-z0-9_]/g, '')
        
        const response = await api('/api/auth/register/', {
          method: 'POST',
          body: {
            email: userData.email,
            username: username,
            first_name: firstName,
            last_name: lastName,
            password: userData.password,
            password_confirm: userData.password
          }
        }) as any
        
        this.token = response.access
        this.refreshToken = response.refresh
        this.user = {
          id: response.user.id,
          email: response.user.email,
          name: userData.name,
          role: response.user.is_superuser ? 'admin' : 'user',
          first_name: firstName,
          last_name: lastName,
          is_superuser: response.user.is_superuser,
          is_2fa_enabled: false,
          email_verified: false  // Par défaut, email non vérifié
        }
        this.is2FAEnabled = false
        this.isAuthenticated = true
        
        this.saveToStorage()
        
        return { success: true, data: response }
      } catch (error: any) {
        console.error('Register error:', error)
        let errorMessage = "Échec de l'inscription"
        if (error.data) {
          if (error.data.detail) {
            errorMessage = error.data.detail
          } else {
            const fieldErrors = Object.entries(error.data)
              .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
              .join('; ')
            if (fieldErrors) errorMessage = fieldErrors
          }
        } else if (error.message) {
          errorMessage = error.message
        }
        this.error = errorMessage
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        if (this.token) {
          const api = createApi()
          await api('/api/auth/logout/', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${this.token}`
            },
            body: {
              refresh: this.refreshToken,
              session_id: this.sessionId
            }
          })
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.token = null
        this.refreshToken = null
        this.sessionId = null
        this.isAuthenticated = false
        this.is2FAEnabled = false
        this.error = null
        
        if (process.client) {
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('user')
          localStorage.removeItem('isAuthenticated')
          localStorage.removeItem('is2FAEnabled')
          localStorage.removeItem('sessionId')
        }
      }
    },

    async changePassword(oldPassword: string, newPassword: string, confirmPassword: string) {
      try {
        this.loading = true
        this.error = null
        
        const api = createApi()
        
        const response = await api('/api/users/change_password/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          },
          body: {
            old_password: oldPassword,
            new_password: newPassword,
            new_password_confirm: confirmPassword
          }
        }) as any
        
        return { success: true, message: response.message || 'Mot de passe changé avec succès' }
      } catch (error: any) {
        console.error('Change password error:', error)
        let errorMessage = 'Échec du changement de mot de passe'
        if (error.data) {
          if (error.data.detail) {
            errorMessage = error.data.detail
          } else {
            const fieldErrors = Object.entries(error.data)
              .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
              .join('; ')
            if (fieldErrors) errorMessage = fieldErrors
          }
        } else if (error.message) {
          errorMessage = error.message
        }
        this.error = errorMessage
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async uploadAvatar(file: File) {
      try {
        this.loading = true
        this.error = null
        console.log('Uploading avatar, token:', this.token)

        const config = useRuntimeConfig()
        const baseURL = config.public.apiBaseUrl || 'http://localhost'

        const formData = new FormData()
        formData.append('avatar', file)

        const performUpload = async (token: string) => {
          return await $fetch('/api/users/upload_avatar/', {
            baseURL,
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
          })
        }

        let response
        try {
          response = await performUpload(this.token!)
        } catch (error: any) {
          if (error?.status === 401) {
            console.log('Token expiré, tentative de rafraîchissement...')
            const refreshed = await this.refreshAuthToken()
            if (refreshed) {
              console.log('Token rafraîchi, nouvelle tentative')
              response = await performUpload(this.token!)
            } else {
              throw new Error('SESSION_EXPIRED')
            }
          } else if (error?.status === 413) {
            throw new Error('Fichier trop volumineux. Taille max : 10 Mo.')
          } else {
            throw error
          }
        }

        console.log('Upload response:', response)

        if (response?.avatar && this.user) {
          this.user.avatar = response.avatar.startsWith('http')
            ? response.avatar
            : `${baseURL}${response.avatar}`
          this.saveToStorage()
          console.log('Avatar URL saved:', this.user.avatar)
        }

        return {
          success: true,
          message: response?.message || 'Avatar mis à jour avec succès',
          data: response
        }
      } catch (error: any) {
        console.error('Upload avatar error:', error)
        let errorMessage = 'Échec de l\'upload'

        if (error.message === 'SESSION_EXPIRED') {
          errorMessage = 'Session expirée. Veuillez vous reconnecter.'
        } else if (error.message === 'Fichier trop volumineux. Taille max : 10 Mo.') {
          errorMessage = error.message
        } else if (error.data) {
          if (error.data.detail) {
            errorMessage = error.data.detail
          } else if (typeof error.data === 'object') {
            const fieldErrors = Object.entries(error.data)
              .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
              .join('; ')
            if (fieldErrors) errorMessage = fieldErrors
          } else if (typeof error.data === 'string') {
            errorMessage = error.data
          }
        } else if (error.message) {
          errorMessage = error.message
        }

        this.error = errorMessage
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async deleteAccount(password?: string) {
      try {
        this.loading = true
        this.error = null

        const api = createApi()
        const response = await api('/api/users/delete_account/', {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${this.token}` },
          body: password ? { password } : undefined
        }) as any

        await this.logout()

        return {
          success: true,
          message: response?.message || 'Compte supprimé avec succès'
        }
      } catch (error: any) {
        console.error('Delete account error:', error)
        let errorMessage = 'Échec de la suppression du compte'

        if (error.data) {
          if (error.data.detail) {
            errorMessage = error.data.detail
          } else if (typeof error.data === 'object') {
            const fieldErrors = Object.entries(error.data)
              .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
              .join('; ')
            if (fieldErrors) errorMessage = fieldErrors
          } else if (typeof error.data === 'string') {
            errorMessage = error.data
          }
        } else if (error.message) {
          errorMessage = error.message
        }

        this.error = errorMessage
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // 2FA
    async enableTwoFactor() {
      try {
        this.loading = true
        this.error = null
        
        const api = createApi()
        const response = await api('/api/auth/enable-2fa/', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${this.token}` }
        }) as any
        
        return { success: true, qrCode: response.qr_code, secret: response.secret }
      } catch (error: any) {
        this.error = error.data?.detail || 'Échec de l\'activation 2FA'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async verifyTwoFactor(code: string) {
      try {
        this.loading = true
        this.error = null
        
        const api = createApi()
        const response = await api('/api/auth/verify-2fa/', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${this.token}` },
          body: { code }
        }) as any
        
        this.is2FAEnabled = true
        if (this.user) this.user.is_2fa_enabled = true
        this.saveToStorage()
        return { success: true, message: response.message }
      } catch (error: any) {
        this.error = error.data?.detail || 'Échec de la vérification 2FA'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async disableTwoFactor() {
      try {
        this.loading = true
        this.error = null
        
        const api = createApi()
        const response = await api('/api/auth/disable-2fa/', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${this.token}` }
        }) as any
        
        this.is2FAEnabled = false
        if (this.user) this.user.is_2fa_enabled = false
        this.saveToStorage()
        return { success: true, message: response.message }
      } catch (error: any) {
        this.error = error.data?.detail || 'Échec de la désactivation 2FA'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async check2FAStatus() {
      try {
        if (!this.token) return false
        const api = createApi()
        const response = await api('/api/auth/2fa-status/', {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${this.token}` }
        }) as any
        this.is2FAEnabled = response.is_enabled || false
        if (this.user) this.user.is_2fa_enabled = this.is2FAEnabled
        return this.is2FAEnabled
      } catch (error) {
        return false
      }
    },

    // ========== NOUVEAUX ENDPOINTS ==========
    // Vérification email
    async sendVerificationEmail(email: string) {
      try {
        this.loading = true
        this.error = null
        const api = createApi()
        const response = await api('/api/auth/send_verification_email/', {
          method: 'POST',
          body: { email }
        }) as any
        return { success: true, message: response.message }
      } catch (error: any) {
        this.error = error.data?.error || 'Erreur lors de l\'envoi du code'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async verifyEmail(email: string, code: string) {
      try {
        this.loading = true
        this.error = null
        const api = createApi()
        const response = await api('/api/auth/verify_email/', {
          method: 'POST',
          body: { email, code }
        }) as any
        // Mettre à jour l'utilisateur local si connecté
        if (this.user && this.user.email === email) {
          this.user.email_verified = true
          this.saveToStorage()
        }
        return { success: true, message: response.message }
      } catch (error: any) {
        this.error = error.data?.error || 'Code invalide ou expiré'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },


    async requestPasswordReset(email: string) {
      try {
        const config = useRuntimeConfig()
        const baseURL = config.public.apiBaseUrl || 'http://localhost'
        const response = await $fetch('/api/auth/password_reset_request/', {
          baseURL,
          method: 'POST',
          body: JSON.stringify({ email }),
          headers: { 'Content-Type': 'application/json' }
        })
        return { success: true, data: response }
      } catch (error: any) {
        return { success: false, error: error.data?.error || 'Erreur lors de l\'envoi du code' }
      }
    },

    async resetPassword(email: string, code: string, newPassword: string) {
      try {
        const config = useRuntimeConfig()
        const baseURL = config.public.apiBaseUrl || 'http://localhost'
        await $fetch('/api/auth/password_reset/', {
          baseURL,
          method: 'POST',
          body: JSON.stringify({
            email,
            code,
            new_password: newPassword,
            new_password_confirm: newPassword   // ← important !
          }),
          headers: { 'Content-Type': 'application/json' }
        })
        return { success: true }
      } catch (error: any) {
        console.error('Erreur resetPassword:', error)
        return { success: false, error: error.data?.error || 'Échec de la réinitialisation' }
      }
    },


    // Connexion Google
    async googleLogin(idToken: string) {
      try {
        this.loading = true
        this.error = null
        const api = createApi()
        const response = await api('/api/auth/google_login/', {
          method: 'POST',
          body: { id_token: idToken }
        }) as any
        this.token = response.access
        this.refreshToken = response.refresh
        this.sessionId = response.session_id
        this.user = {
          id: response.user.id,
          email: response.user.email,
          name: `${response.user.first_name || ''} ${response.user.last_name || ''}`.trim() || response.user.username,
          role: response.user.is_superuser ? 'admin' : 'user',
          first_name: response.user.first_name,
          last_name: response.user.last_name,
          is_superuser: response.user.is_superuser,
          is_2fa_enabled: response.user.is_2fa_enabled || false,
          email_verified: response.user.email_verified !== false  // Google garantit l'email vérifié
        }
        this.is2FAEnabled = response.user.is_2fa_enabled || false
        this.isAuthenticated = true
        this.saveToStorage()
        return { success: true, data: response }
      } catch (error: any) {
        this.error = error.data?.error || 'Erreur de connexion Google'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    saveToStorage() {
      if (process.client) {
        console.log('Saving token to localStorage:', this.token)
        if (this.token) {
          localStorage.setItem('token', this.token)
          if (this.refreshToken) localStorage.setItem('refreshToken', this.refreshToken)
          if (this.user) localStorage.setItem('user', JSON.stringify(this.user))
          if (this.sessionId) localStorage.setItem('sessionId', this.sessionId)
          localStorage.setItem('isAuthenticated', 'true')
          localStorage.setItem('is2FAEnabled', this.is2FAEnabled.toString())
          console.log('Saved. Now localStorage token:', localStorage.getItem('token'))
        } else {
          console.warn('No token to save')
        }
      }
    },

    loadFromStorage() {
      if (process.client && typeof window !== 'undefined') {
        const token = localStorage.getItem('token')
        const refreshToken = localStorage.getItem('refreshToken')
        const storedUser = localStorage.getItem('user')
        const sessionId = localStorage.getItem('sessionId')
        const stored2FA = localStorage.getItem('is2FAEnabled')

        if (token && storedUser) {
          this.token = token
          this.refreshToken = refreshToken
          this.user = JSON.parse(storedUser)
          this.isAuthenticated = true
          this.is2FAEnabled = stored2FA === 'true'
          this.sessionId = sessionId
          console.log('Store chargé avec succès', this.user)
        } else {
          console.warn('Token ou utilisateur manquant dans localStorage')
        }
      }
    },

    async refreshAuthToken() {
      if (!this.refreshToken) return false
      
      try {
        const api = createApi()
        const response = await api('/api/auth/refresh/', {
          method: 'POST',
          body: { refresh: this.refreshToken }
        }) as any
        
        this.token = response.access
        if (response.refresh) this.refreshToken = response.refresh
        this.saveToStorage()
        return true
      } catch (error) {
        console.error('Token refresh failed:', error)
        await this.logout()
        return false
      }
    }
  }
})