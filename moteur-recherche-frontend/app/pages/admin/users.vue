<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900/10']">
    <!-- Grille de points futuriste -->
    <!-- <div class="fixed top-20 left-4 z-50 bg-black/80 text-white p-4 rounded-lg text-xs">
      <p>🔍 DEBUG | users.length: {{ users.length }}</p>
      <ul>
        <li v-for="u in users" :key="u.id">
          {{ u.id }} - {{ u.name }}
        </li>
      </ul>
    </div> -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(59,130,246,0.12)_1px,_transparent_1px)] dark:bg-[radial-gradient(circle_at_center,_rgba(0,255,255,0.15)_1px,_transparent_1px)] bg-[length:24px_24px]"></div>
    </div>

    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 z-10">
      <!-- En-tête avec effet néon -->
      <div class="mb-10">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-4xl font-bold tracking-tight">
              <span class="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">Gestion</span>
              <span class="text-gray-900 dark:text-white ml-2">des utilisateurs</span>
            </h1>
            <p class="text-gray-600 dark:text-gray-400 mt-2 flex items-center gap-2">
              <span class="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              Gérez les comptes, rôles et permissions
            </p>
          </div>
          <button
            @click="showAddUserModal = true"
            class="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl text-sm font-medium transition-all duration-300 flex items-center gap-2 shadow-lg shadow-cyan-500/20"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Ajouter un utilisateur
          </button>
        </div>
      </div>

      <!-- Tableau futuriste -->
      <div class="backdrop-blur-xl bg-white/80 dark:bg-gray-800/40 rounded-2xl shadow-2xl border border-gray-200/50 dark:border-cyan-500/30 overflow-hidden transition-all duration-300 hover:shadow-cyan-500/10">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-white/10">
            <thead class="bg-gradient-to-r from-cyan-50/50 to-blue-50/50 dark:from-cyan-900/20 dark:to-blue-900/20">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">#</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Nom</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Email</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Rôle</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Statut</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Dernière connexion</th>
                <th class="px-6 py-4 text-right text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-white/5">
              <tr 
                v-for="(user, index) in users" 
                :key="`user-${user.id}-${index}`"
                class="group transition-all duration-200 hover:bg-cyan-50/30 dark:hover:bg-cyan-900/10 hover:shadow-md"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono font-bold text-gray-700 dark:text-cyan-300">
                  {{ (index + 1).toString().padStart(2, '0') }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-semibold text-sm shadow-md">
                      {{ (user.name || 'U').charAt(0).toUpperCase() }}
                    </div>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{{ user.name || 'Utilisateur' }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">{{ user.email }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'px-3 py-1 text-xs font-semibold rounded-full border',
                    user.role === 'admin'
                      ? 'bg-purple-100/80 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-500/50'
                      : 'bg-blue-100/80 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-500/50'
                  ]">
                    {{ user.role === 'admin' ? 'Administrateur' : 'Utilisateur' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'px-3 py-1 text-xs font-semibold rounded-full border',
                    user.is_active
                      ? 'bg-green-100/80 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-300 dark:border-green-500/50'
                      : 'bg-red-100/80 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-300 dark:border-red-500/50'
                  ]">
                    {{ user.is_active ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 font-mono">
                  {{ formatDate(user.last_login) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="editUser(user)" class="text-cyan-600 dark:text-cyan-400 hover:text-cyan-800 dark:hover:text-cyan-300 mr-4 transition-colors">
                    <svg class="w-5 h-5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="toggleUserStatus(user)" class="text-yellow-600 dark:text-yellow-400 hover:text-yellow-800 dark:hover:text-yellow-300 mr-4 transition-colors">
                    <svg class="w-5 h-5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                  </button>
                  <button 
                    @click="deleteUser(user)" 
                    :disabled="deletingIds.has(user.id)"
                    class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg class="w-5 h-5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="7" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                  Aucun utilisateur trouvé
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal pour ajout d'utilisateur -->
      <div v-if="showAddUserModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 transition-all">
        <div class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl rounded-2xl p-8 w-full max-w-md border border-cyan-500/30 shadow-2xl shadow-cyan-500/20">
          <h2 class="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-6">Ajouter un utilisateur</h2>
          <div class="space-y-5">
            <input 
              v-model="newUser.name" 
              type="text" 
              placeholder="Nom complet" 
              class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400"
            >
            <input 
              v-model="newUser.email" 
              type="email" 
              placeholder="Email" 
              class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400"
            >
            <input 
              v-model="newUser.password" 
              type="password" 
              placeholder="Mot de passe" 
              class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400"
            >
            <select 
              v-model="newUser.role" 
              class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all text-gray-900 dark:text-white"
            >
              <option value="user" class="text-gray-900 dark:text-white">Utilisateur</option>
              <option value="admin" class="text-gray-900 dark:text-white">Administrateur</option>
            </select>
          </div>
          <div class="flex justify-end gap-3 mt-8">
            <button @click="showAddUserModal = false" class="px-5 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white transition-colors">Annuler</button>
            <button @click="createUser" :disabled="isCreatingUser" class="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl transition-all shadow-md disabled:opacity-50">
              {{ isCreatingUser ? 'Création...' : 'Créer' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useThemeStore } from '../../../stores/theme.store'
import { useApi } from '../../../composables/useApi'

interface User {
  id: string
  name: string
  email: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
  last_login: string | null
}

const themeStore = useThemeStore()
const api = useApi()

const users = ref<User[]>([])
const showAddUserModal = ref(false)
const isCreatingUser = ref(false)
const deletingIds = ref<Set<string>>(new Set())

const newUser = ref({
  name: '',
  email: '',
  password: '',
  role: 'user' as 'user' | 'admin'
})

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Jamais'
  return new Date(dateString).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const fetchUsers = async () => {
  try {
    const data = await api.get<any>('/api/admin/users/')
    let raw: any[] = []
    if (Array.isArray(data)) {
      raw = data
    } else if (data && typeof data === 'object' && 'results' in data) {
      raw = (data as any).results
    }
    users.value = raw.map((u: any) => ({
      id: u.id || u.email || 'unknown',
      name: `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username || u.email || 'Utilisateur',
      email: u.email || '',
      role: u.is_superuser ? 'admin' : 'user',
      is_active: u.is_active ?? true,
      created_at: u.date_joined || '',
      last_login: u.last_login || null
    }))
  } catch (e) {
    console.error('Erreur fetchUsers:', e)
    users.value = []
  }
}

const createUser = async () => {
  if (!newUser.value.email || !newUser.value.password || !newUser.value.name) {
    alert('Veuillez remplir tous les champs')
    return
  }
  isCreatingUser.value = true
  try {
    const username = newUser.value.name.toLowerCase().replace(/\s+/g, '_')
    await api.post('/api/admin/users/', {
      email: newUser.value.email,
      password: newUser.value.password,
      first_name: newUser.value.name.trim().split(' ')[0],
      last_name: newUser.value.name.trim().split(' ').slice(1).join(' ') || '',
      username,
      is_superuser: newUser.value.role === 'admin'
    })
    showAddUserModal.value = false
    resetNewUser()
    await fetchUsers()
  } catch (e) {
    console.error('Erreur création:', e)
    alert('Échec de la création')
  } finally {
    isCreatingUser.value = false
  }
}

const editUser = async (user: User) => {
  const newName = prompt('Nouveau nom (Prénom Nom) :', user.name)
  const newRole = prompt('Rôle (user/admin) :', user.role)
  if (newName !== null && newRole !== null) {
    const [first, ...last] = newName.trim().split(' ')
    try {
      await api.put(`/api/admin/users/${user.id}/`, {
        first_name: first,
        last_name: last.join(' ') || '',
        is_superuser: newRole === 'admin'
      })
      await fetchUsers()
    } catch (e) {
      alert('Erreur modification')
    }
  }
}

const toggleUserStatus = async (user: User) => {
  try {
    await api.put(`/api/admin/users/${user.id}/`, { is_active: !user.is_active })
    await fetchUsers()
  } catch (e) {
    console.error(e)
  }
}

const deleteUser = async (user: User) => {
  if (!confirm(`Supprimer ${user.name} ?`)) return
  deletingIds.value.add(user.id)
  try {
    await api.delete(`/api/admin/users/${user.id}/`)
    users.value = users.value.filter(u => u.id !== user.id)
  } catch (e) {
    alert('Erreur suppression')
    await fetchUsers()
  } finally {
    deletingIds.value.delete(user.id)
  }
}

const resetNewUser = () => {
  newUser.value = { name: '', email: '', password: '', role: 'user' }
}

// Vérification admin locale
const checkAdmin = () => {
  if (!process.client) return
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  if (!token || !userStr) { window.location.href = '/login'; return }
  try {
    const user = JSON.parse(userStr)
    if (!user.is_superuser && user.role !== 'admin') {
      window.location.href = '/'
      return
    }
  } catch { window.location.href = '/login' }
}

onMounted(() => {
  checkAdmin()
  fetchUsers()
})
</script>