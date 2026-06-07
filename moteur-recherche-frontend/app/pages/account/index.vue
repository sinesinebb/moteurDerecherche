<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900']">
    <!-- Grille de points subtile -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(59,130,246,0.08)_1px,_transparent_1px)] dark:bg-[radial-gradient(circle_at_center,_rgba(59,130,246,0.12)_1px,_transparent_1px)] bg-[length:24px_24px]"></div>
    </div>

    <div class="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 z-10">
      <!-- En-tête -->
      <div class="mb-10 animate-fade-in-up">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
          Mon compte
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Paramètres et préférences de votre profil</p>
      </div>

      <!-- Grille principale -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Colonne gauche (profil + sécurité) -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Carte Profil -->
          <div class="backdrop-blur-xl bg-white/70 dark:bg-gray-800/40 rounded-2xl shadow-xl border border-white/30 dark:border-gray-700/30 hover:shadow-2xl transition-all duration-300 p-6">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6">
              <span class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-3">
                <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              Informations personnelles
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Nom complet</label>
                <input
                  v-model="user.name"
                  type="text"
                  class="w-full px-4 py-3 bg-white/80 dark:bg-gray-900/80 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all dark:text-white"
                  placeholder="Votre nom"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Adresse email</label>
                <input
                  v-model="user.email"
                  type="email"
                  disabled
                  class="w-full px-4 py-3 bg-gray-100/80 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-500 dark:text-gray-400 cursor-not-allowed"
                />
              </div>
            </div>
          </div>

          <!-- Carte Sécurité -->
          <div class="backdrop-blur-xl bg-white/70 dark:bg-gray-800/40 rounded-2xl shadow-xl border border-white/30 dark:border-gray-700/30 hover:shadow-2xl transition-all duration-300 p-6">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6">
              <span class="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center mr-3">
                <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </span>
              Sécurité
            </h2>
            <div class="space-y-4">
              <div class="flex items-center justify-between py-3 border-b border-gray-200/50 dark:border-gray-700/50">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Mot de passe</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Modifiez votre mot de passe</p>
                </div>
                <NuxtLink
                  to="/account/security"
                  class="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                >
                  Changer →
                </NuxtLink>
              </div>
              <div class="flex items-center justify-between py-3">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Authentification à deux facteurs</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Renforcez la sécurité de votre compte</p>
                </div>
                <button
                  @click="toggleTwoFactor"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                  :class="twoFactorEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'"
                >
                  <span
                    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200"
                    :class="twoFactorEnabled ? 'translate-x-6' : 'translate-x-1'"
                  />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Colonne droite (préférences + avatar) -->
        <div class="space-y-8">
          <!-- Carte Préférences -->
          <div class="backdrop-blur-xl bg-white/70 dark:bg-gray-800/40 rounded-2xl shadow-xl border border-white/30 dark:border-gray-700/30 hover:shadow-2xl transition-all duration-300 p-6">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6">
              <span class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-3">
                <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </span>
              Préférences
            </h2>
            <div class="space-y-5">
              <!-- Thème -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Apparence</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Thème clair / sombre</p>
                </div>
                <button
                  @click="toggleDarkMode"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                  :class="themeStore.isDarkMode ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'"
                >
                  <span
                    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200"
                    :class="themeStore.isDarkMode ? 'translate-x-6' : 'translate-x-1'"
                  />
                </button>
              </div>
              <!-- Langue -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Langue</label>
                <select
                  v-model="selectedLanguage"
                  class="w-full px-4 py-2.5 bg-white/80 dark:bg-gray-900/80 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all dark:text-white"
                >
                  <option value="fr">Français</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                </select>
              </div>
              <!-- Résultats par page -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Résultats par page</label>
                <select
                  v-model="resultsPerPage"
                  class="w-full px-4 py-2.5 bg-white/80 dark:bg-gray-900/80 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all dark:text-white"
                >
                  <option value="10">10 résultats</option>
                  <option value="20">20 résultats</option>
                  <option value="50">50 résultats</option>
                </select>
              </div>
              <!-- Notifications -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Notifications</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Alertes par email</p>
                </div>
                <button
                  @click="toggleNotifications"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                  :class="notificationsEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'"
                >
                  <span
                    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200"
                    :class="notificationsEnabled ? 'translate-x-6' : 'translate-x-1'"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Carte Avatar -->
          <div class="backdrop-blur-xl bg-white/70 dark:bg-gray-800/40 rounded-2xl shadow-xl border border-white/30 dark:border-gray-700/30 hover:shadow-2xl transition-all duration-300 p-6 text-center">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6 justify-center">
              <span class="w-8 h-8 rounded-lg bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center mr-3">
                <svg class="w-4 h-4 text-pink-600 dark:text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </span>
              Photo de profil
            </h2>
            <div class="flex flex-col items-center space-y-4">
              <div class="relative group">
                <div class="w-28 h-28 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-3xl font-bold shadow-lg transition-transform group-hover:scale-105">
                  {{ userInitial }}
                </div>
                <div class="absolute inset-0 rounded-full bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 text-center">
                Gérez votre avatar et les options avancées
              </p>
              <NuxtLink
                to="/account/settings"
                class="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl text-sm font-medium text-center transition-all duration-300 shadow-md hover:shadow-lg"
              >
                Gérer l'avatar
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Boutons d'action -->
      <div class="mt-12 pt-6 border-t border-gray-200/50 dark:border-gray-700/50 flex justify-end gap-4">
        <button
          @click="cancel"
          class="px-6 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200"
        >
          Annuler
        </button>
        <button
          @click="saveSettings"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-medium shadow-md hover:shadow-lg transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Enregistrer
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from '#app'
import { useAuthStore } from '../../../stores/auth.store'
import { useThemeStore } from '../../../stores/theme.store'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Données utilisateur (sans bio)
const user = ref({
  name: '',
  email: ''
})

// Préférences
const selectedLanguage = ref('fr')
const resultsPerPage = ref('20')
const notificationsEnabled = ref(true)
const twoFactorEnabled = ref(false)

// Computed
const userInitial = computed(() => {
  return authStore.user?.name?.charAt(0).toUpperCase() || authStore.user?.email?.charAt(0).toUpperCase() || 'U'
})

// Initialisation
onMounted(() => {
  if (authStore.user) {
    user.value = {
      name: authStore.user.name || '',
      email: authStore.user.email || ''
    }
  }
  loadPreferences()
})

// Charger les préférences depuis localStorage
const loadPreferences = () => {
  if (typeof window !== 'undefined') {
    selectedLanguage.value = localStorage.getItem('user_language') || 'fr'
    resultsPerPage.value = localStorage.getItem('user_results_per_page') || '20'
    notificationsEnabled.value = localStorage.getItem('user_notifications') !== 'false'
    twoFactorEnabled.value = localStorage.getItem('user_two_factor') === 'true'
  }
}

// Sauvegarder les préférences
const savePreferences = () => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user_language', selectedLanguage.value)
    localStorage.setItem('user_results_per_page', resultsPerPage.value)
    localStorage.setItem('user_notifications', notificationsEnabled.value.toString())
    localStorage.setItem('user_two_factor', twoFactorEnabled.value.toString())
  }
}

// Actions
const toggleDarkMode = () => {
  themeStore.toggleTheme()
}

const toggleNotifications = () => {
  notificationsEnabled.value = !notificationsEnabled.value
}

const toggleTwoFactor = () => {
  twoFactorEnabled.value = !twoFactorEnabled.value
}

const saveSettings = () => {
  savePreferences()
  // Ici vous pourriez appeler une API pour mettre à jour le profil
  console.log('Sauvegarde des paramètres:', {
    user: user.value,
    preferences: {
      language: selectedLanguage.value,
      resultsPerPage: resultsPerPage.value,
      notifications: notificationsEnabled.value,
      twoFactor: twoFactorEnabled.value
    }
  })
  alert('Paramètres enregistrés avec succès !')
}

const cancel = () => {
  router.back()
}
</script>

<style scoped>
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in-up {
  animation: fade-in-up 0.5s ease-out;
}
</style>