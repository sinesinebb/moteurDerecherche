<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900/10']">
    <!-- Grille de points futuriste -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(59,130,246,0.12)_1px,_transparent_1px)] dark:bg-[radial-gradient(circle_at_center,_rgba(0,255,255,0.15)_1px,_transparent_1px)] bg-[length:24px_24px]"></div>
    </div>

    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 z-10">
      <!-- En-tête avec effet néon -->
      <div class="mb-10">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-4xl font-bold tracking-tight">
              <span class="text-gray-900 dark:text-white ml-2">Gestion des utilisateurs</span>
            </h1>
            <p class="text-gray-600 dark:text-gray-400 mt-2 flex items-center gap-2">
              <span class="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              Consultez les profils et statistiques
            </p>
            <!-- LOGO LUKA STYLÉ & PREMIUM (Version Dégradée & Calligraphique) -->
            <NuxtLink to="/" class="flex items-center space-x-2 group">
              <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 p-1 group-hover:scale-105 transition-transform duration-300">
                <div class="w-full h-full bg-white dark:bg-[#202124] rounded-full flex items-center justify-center">
                  <span class="text-xl">🔍</span>
                </div>
              </div>
              <div class="flex flex-col">
                <h1 
                  class="text-3xl md:text-4xl font-bold transition-all duration-300 hover:scale-105 cursor-default"
                  style="font-family: 'Great Vibes', 'Dancing Script', 'Pacifico', cursive; text-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                >
                  <!-- L en dégradé vert -->
                  <span style="background: linear-gradient(135deg, #009543 0%, #00d961 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 0 1px;">
                    L
                  </span>
                  <!-- u en dégradé jaune -->
                  <span style="background: linear-gradient(135deg, #FFD100 0%, #ffb700 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 0 1px;">
                    u
                  </span>
                  <!-- k en dégradé jaune doré -->
                  <span style="background: linear-gradient(135deg, #FFD100 0%, #ffb700 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 0 2px;">
                    k
                  </span>
                  <!-- a en dégradé rouge -->
                  <span style="background: linear-gradient(135deg, #CE1126 0%, #ff1a40 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 0 2px;">
                    a
                  </span>
                </h1>
              </div>
            </NuxtLink>
          </div>
          <!-- Barre de recherche (filtre) -->
          <div class="relative w-full md:w-80">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un utilisateur..."
              class="w-full pl-10 pr-4 py-3 bg-white/80 dark:bg-gray-800/60 backdrop-blur-md border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 transition-all shadow-sm"
            />
          </div>
        </div>
      </div>

      <!-- Tableau futuriste -->
      <div class="backdrop-blur-xl bg-white/80 dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200/50 dark:border-cyan-500/30 overflow-hidden transition-all duration-300 hover:shadow-cyan-500/10">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-white/10">
            <thead class="bg-gradient-to-r from-cyan-50/50 to-blue-50/50 dark:from-cyan-900/20 dark:to-blue-900/20">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">N°</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Utilisateur</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Email</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Rôle</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Statut</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-cyan-300 uppercase tracking-wider">Dernière connexion</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-white/5">
              <tr 
                v-for="(user, index) in filteredUsers" 
                :key="`user-${user.id}-${index}`"
                class="group transition-all duration-200 hover:bg-cyan-50/30 dark:hover:bg-cyan-900/10 hover:shadow-md"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono font-bold text-gray-700 dark:text-cyan-300">
                  {{ (index + 1).toString().padStart(2, '0') }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-semibold text-sm shadow-md">
                      {{ (user.name || 'U').charAt(0).toUpperCase() }}
                    </div>
                    <div class="flex flex-col">
                      <span class="text-sm font-medium text-gray-900 dark:text-white">{{ user.name || 'Utilisateur' }}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">ID: {{ user.id }}</span>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    {{ user.email }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'px-3 py-1 text-xs font-semibold rounded-full border inline-flex items-center gap-1',
                    user.role === 'admin'
                      ? 'bg-purple-100/80 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-500/50'
                      : 'bg-blue-100/80 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-500/50'
                  ]">
                    <svg v-if="user.role === 'admin'" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    {{ user.role === 'admin' ? 'Administrateur' : 'Utilisateur' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'px-3 py-1 text-xs font-semibold rounded-full border inline-flex items-center gap-1',
                    user.is_active
                      ? 'bg-green-100/80 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-300 dark:border-green-500/50'
                      : 'bg-red-100/80 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-300 dark:border-red-500/50'
                  ]">
                    <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
                    {{ user.is_active ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 font-mono">
                  {{ formatDate(user.last_login) }}
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0 && !isLoading">
                <td colspan="6" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                  <div class="flex flex-col items-center gap-3">
                    <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <span>Aucun utilisateur trouvé</span>
                  </div>
                </td>
              </tr>
              <tr v-if="isLoading">
                <td colspan="6" class="px-6 py-12 text-center">
                  <div class="flex justify-center items-center gap-2">
                    <div class="animate-spin h-5 w-5 border-2 border-cyan-500 border-t-transparent rounded-full"></div>
                    <span class="text-gray-500 dark:text-gray-400">Chargement...</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Pied de tableau avec stats -->
        <div class="px-6 py-3 bg-gray-50/50 dark:bg-gray-800/30 border-t border-gray-200 dark:border-white/10 text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
          <span>{{ filteredUsers.length }} utilisateur(s) affiché(s) sur {{ users.length }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ========== AJOUT IMPORTANT ==========
// Désactive le layout par défaut pour cette page d'administration
definePageMeta({ layout: false })

import { ref, computed, onMounted } from 'vue'
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
const searchQuery = ref('')
const isLoading = ref(false)

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value
  const query = searchQuery.value.toLowerCase().trim()
  return users.value.filter(
    user =>
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.id.toLowerCase().includes(query)
  )
})

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Jamais'
  return new Date(dateString).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const fetchUsers = async () => {
  isLoading.value = true
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
  } finally {
    isLoading.value = false
  }
}

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