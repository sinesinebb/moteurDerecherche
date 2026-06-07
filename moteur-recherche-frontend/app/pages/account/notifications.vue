<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Notifications</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Configurez vos préférences de notification</p>
    </div>

    <div class="space-y-8">
      <!-- Notifications générales -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Notifications générales</h2>
        
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Notifications par email</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Recevoir des notifications par email</p>
            </div>
            <button
              @click="toggleSetting('emailNotifications')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.emailNotifications ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
              ]"
            >
              <span
                :class="settings.emailNotifications ? 'translate-x-6' : 'translate-x-1'"
                class="inline-block h-4 w-4 transform rounded-full bg-white transition"
              />
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Notifications push</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Recevoir des notifications sur le site</p>
            </div>
            <button
              @click="toggleSetting('pushNotifications')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.pushNotifications ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
              ]"
            >
              <span
                :class="settings.pushNotifications ? 'translate-x-6' : 'translate-x-1'"
                class="inline-block h-4 w-4 transform rounded-full bg-white transition"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Notifications de recherche -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Notifications de recherche</h2>
        
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Alertes de nouveaux résultats</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Être notifié de nouveaux résultats pour vos recherches sauvegardées</p>
            </div>
            <button
              @click="toggleSetting('newResultsAlerts')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.newResultsAlerts ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
              ]"
            >
              <span
                :class="settings.newResultsAlerts ? 'translate-x-6' : 'translate-x-1'"
                class="inline-block h-4 w-4 transform rounded-full bg-white transition"
              />
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Suggestions de recherche</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Recevoir des suggestions basées sur votre historique</p>
            </div>
            <button
              @click="toggleSetting('searchSuggestions')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.searchSuggestions ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
              ]"
            >
              <span
                :class="settings.searchSuggestions ? 'translate-x-6' : 'translate-x-1'"
                class="inline-block h-4 w-4 transform rounded-full bg-white transition"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Notifications système -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Notifications système</h2>
        
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Mises à jour système</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Être informé des mises à jour et maintenance</p>
            </div>
            <button
              @click="toggleSetting('systemUpdates')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.systemUpdates ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
              ]"
            >
              <span
                :class="settings.systemUpdates ? 'translate-x-6' : 'translate-x-1'"
                class="inline-block h-4 w-4 transform rounded-full bg-white transition"
              />
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Nouveautés</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Recevoir des informations sur les nouvelles fonctionnalités</p>
            </div>
            <button
              @click="toggleSetting('newFeatures')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.newFeatures ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
              ]"
            >
              <span
                :class="settings.newFeatures ? 'translate-x-6' : 'translate-x-1'"
                class="inline-block h-4 w-4 transform rounded-full bg-white transition"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Historique des notifications -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
          Historique des notifications
          <button
            @click="clearNotifications"
            class="ml-4 text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
          >
            Tout effacer
          </button>
        </h2>

        <div class="space-y-4">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            :class="[
              'p-4 rounded-lg border',
              notification.read ? 'bg-gray-50 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600' : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
            ]"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <div :class="[
                    'w-2 h-2 rounded-full mr-3',
                    notification.type === 'search' ? 'bg-blue-500' :
                    notification.type === 'system' ? 'bg-green-500' : 'bg-purple-500'
                  ]"></div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ notification.title }}</p>
                  <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">{{ formatDate(notification.date) }}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 ml-5">{{ notification.message }}</p>
              </div>
              <button
                @click="markAsRead(notification.id)"
                v-if="!notification.read"
                class="ml-4 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
              >
                Marquer comme lu
              </button>
            </div>
          </div>

          <div v-if="notifications.length === 0" class="text-center py-8">
            <svg class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <p class="mt-4 text-gray-500 dark:text-gray-400">Aucune notification</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-4">
        <button
          @click="resetSettings"
          class="px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium"
        >
          Réinitialiser
        </button>
        <button
          @click="saveSettings"
          :disabled="isSaving"
          class="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isSaving">Enregistrement...</span>
          <span v-else>Enregistrer les paramètres</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({
  layout: 'default',
  requiresAth: true  
})

interface Notification {
  id: string
  title: string
  message: string
  type: 'search' | 'system' | 'feature'
  date: string
  read: boolean
}

const settings = ref({
  emailNotifications: true,
  pushNotifications: true,
  newResultsAlerts: true,
  searchSuggestions: true,
  systemUpdates: true,
  newFeatures: false
})

const notifications = ref<Notification[]>([
  {
    id: '1',
    title: 'Nouveaux résultats disponibles',
    message: 'De nouveaux documents ont été trouvés pour votre recherche "microservices architecture"',
    type: 'search',
    date: new Date(Date.now() - 3600000).toISOString(),
    read: false
  },
  {
    id: '2',
    title: 'Maintenance planifiée',
    message: 'Une maintenance système est prévue le 15 février de 2h à 4h',
    type: 'system',
    date: new Date(Date.now() - 86400000).toISOString(),
    read: true
  },
  {
    id: '3',
    title: 'Nouvelle fonctionnalité',
    message: 'La recherche sémantique est maintenant disponible. Essayez-la !',
    type: 'feature',
    date: new Date(Date.now() - 172800000).toISOString(),
    read: true
  }
])

const isSaving = ref(false)

onMounted(() => {
  const savedSettings = localStorage.getItem('notificationSettings')
  if (savedSettings) {
    settings.value = JSON.parse(savedSettings)
  }
})

const toggleSetting = (key: keyof typeof settings.value) => {
  settings.value[key] = !settings.value[key]
}

const saveSettings = () => {
  isSaving.value = true
  try {
    localStorage.setItem('notificationSettings', JSON.stringify(settings.value))
    setTimeout(() => {
      alert('Paramètres sauvegardés avec succès !')
      isSaving.value = false
    }, 500)
  } catch (error) {
    alert('Erreur lors de la sauvegarde')
    isSaving.value = false
  }
}

const resetSettings = () => {
  if (confirm('Réinitialiser tous les paramètres de notification ?')) {
    settings.value = {
      emailNotifications: true,
      pushNotifications: true,
      newResultsAlerts: true,
      searchSuggestions: true,
      systemUpdates: true,
      newFeatures: false
    }
  }
}

const markAsRead = (id: string) => {
  const notification = notifications.value.find(n => n.id === id)
  if (notification) {
    notification.read = true
  }
}

const clearNotifications = () => {
  if (confirm('Effacer tout l\'historique des notifications ?')) {
    notifications.value = []
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'À l\'instant'
  if (diffMins < 60) return `Il y a ${diffMins} minute${diffMins > 1 ? 's' : ''}`
  if (diffHours < 24) return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`
  if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`
  
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}
</script>