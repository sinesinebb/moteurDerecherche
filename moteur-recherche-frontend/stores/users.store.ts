import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
  password: string
  createdAt: string
  lastLogin?: string
  isActive: boolean
  avatar?: string
}

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [] as User[],
    loading: false,
    initialized: false
  }),

  getters: {
    getAllUsers: (state) => state.users,
    getActiveUsers: (state) => state.users.filter(user => user.isActive),
    getAdmins: (state) => state.users.filter(user => user.role === 'admin'),
    getUserCount: (state) => state.users.length,
    getUserById: (state) => (id: string) => state.users.find(user => user.id === id),
    getUserByEmail: (state) => (email: string) => state.users.find(user => user.email === email)
  },

  actions: {
    initializeUsers() {
      if (this.initialized) return
      
      const storedUsers = localStorage.getItem('techsearch_users')
      if (storedUsers) {
        try {
          this.users = JSON.parse(storedUsers)
        } catch (error) {
          console.error('Error parsing stored users:', error)
          this.users = []
        }
      } else {
        const defaultAdmin: User = {
          id: this.generateId(),
          email: 'admin@search.dev',
          name: 'Administrateur',
          role: 'admin',
          password: 'admin123',
          createdAt: new Date().toISOString(),
          isActive: true
        }
        this.users = [defaultAdmin]
        this.saveToStorage()
      }
      
      this.initialized = true
    },

    generateId(): string {
      return Date.now().toString(36) + Math.random().toString(36).substr(2)
    },

    async createUser(userData: Omit<User, 'id' | 'createdAt' | 'isActive'>): Promise<{ success: boolean; user: User; error?: string }> {
      this.loading = true
      
      try {
        // Vérifier si l'email existe déjà
        if (this.getUserByEmail(userData.email)) {
          throw new Error('Un utilisateur avec cet email existe déjà')
        }

        const newUser: User = {
          id: this.generateId(),
          ...userData,
          createdAt: new Date().toISOString(),
          isActive: true
        }

        this.users.push(newUser)
        this.saveToStorage()
        
        return { success: true, user: newUser }
      } catch (error: any) {
        return { 
          success: false, 
          user: {} as User,
          error: error.message || "Erreur lors de la création de l'utilisateur" 
        }
      } finally {
        this.loading = false
      }
    },

    async updateUser(id: string, updates: Partial<User>): Promise<{ success: boolean; user?: User; error?: string }> {
      try {
        const userIndex = this.users.findIndex(user => user.id === id)
        if (userIndex === -1) {
          throw new Error('Utilisateur non trouvé')
        }

        // Vérifier si l'email est déjà utilisé par un autre utilisateur
        if (updates.email && updates.email !== this.users[userIndex].email) {
          const existingUser = this.getUserByEmail(updates.email)
          if (existingUser && existingUser.id !== id) {
            throw new Error('Cet email est déjà utilisé par un autre utilisateur')
          }
        }

        // Mettre à jour l'utilisateur sans mutation directe
        const updatedUser = { ...this.users[userIndex], ...updates }
        this.users = [
          ...this.users.slice(0, userIndex),
          updatedUser,
          ...this.users.slice(userIndex + 1)
        ]
        
        this.saveToStorage()
        
        return { success: true, user: updatedUser }
      } catch (error: any) {
        return { 
          success: false, 
          error: error.message || "Erreur lors de la mise à jour de l'utilisateur" 
        }
      }
    },

    async deleteUser(id: string): Promise<{ success: boolean; error?: string }> {
      try {
        const userIndex = this.users.findIndex(user => user.id === id)
        if (userIndex === -1) {
          throw new Error('Utilisateur non trouvé')
        }

        // Désactiver plutôt que supprimer
        const updatedUser = { ...this.users[userIndex], isActive: false }
        this.users = [
          ...this.users.slice(0, userIndex),
          updatedUser,
          ...this.users.slice(userIndex + 1)
        ]
        
        this.saveToStorage()
        
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          error: error.message || "Erreur lors de la suppression de l'utilisateur" 
        }
      }
    },

    async restoreUser(id: string): Promise<{ success: boolean; error?: string }> {
      try {
        const userIndex = this.users.findIndex(user => user.id === id)
        if (userIndex === -1) {
          throw new Error('Utilisateur non trouvé')
        }

        const updatedUser = { ...this.users[userIndex], isActive: true }
        this.users = [
          ...this.users.slice(0, userIndex),
          updatedUser,
          ...this.users.slice(userIndex + 1)
        ]
        
        this.saveToStorage()
        
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          error: error.message || "Erreur lors de la restauration de l'utilisateur" 
        }
      }
    },

    async changeUserRole(id: string, role: 'user' | 'admin'): Promise<{ success: boolean; error?: string }> {
      try {
        const userIndex = this.users.findIndex(user => user.id === id)
        if (userIndex === -1) {
          throw new Error('Utilisateur non trouvé')
        }

        const updatedUser = { ...this.users[userIndex], role }
        this.users = [
          ...this.users.slice(0, userIndex),
          updatedUser,
          ...this.users.slice(userIndex + 1)
        ]
        
        this.saveToStorage()
        
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          error: error.message || "Erreur lors du changement de rôle" 
        }
      }
    },

    async updateLastLogin(email: string): Promise<void> {
      try {
        const user = this.getUserByEmail(email)
        if (user) {
          const userIndex = this.users.findIndex(u => u.id === user.id)
          if (userIndex !== -1) {
            const updatedUser = { ...this.users[userIndex], lastLogin: new Date().toISOString() }
            this.users = [
              ...this.users.slice(0, userIndex),
              updatedUser,
              ...this.users.slice(userIndex + 1)
            ]
            this.saveToStorage()
          }
        }
      } catch (error) {
        console.error('Error updating last login:', error)
      }
    },

    saveToStorage() {
      try {
        localStorage.setItem('techsearch_users', JSON.stringify(this.users))
      } catch (error) {
        console.error('Error saving users to storage:', error)
      }
    },

    clearAll() {
      this.users = []
      localStorage.removeItem('techsearch_users')
      this.initialized = false
    }
  }
})