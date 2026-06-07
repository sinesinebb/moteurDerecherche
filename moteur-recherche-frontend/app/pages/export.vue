<template>
  <!-- Template inchangé -->
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Export des données</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Téléchargez vos données personnelles</p>
    </div>

    <div class="space-y-8">
      <!-- Types d'export -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Sélectionnez les données à exporter</h2>
        
        <div class="space-y-4">
          <div v-for="dataType in exportTypes" :key="dataType.id" class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div class="flex items-center">
              <input
                :id="dataType.id"
                v-model="selectedTypes"
                :value="dataType.id"
                type="checkbox"
                class="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label :for="dataType.id" class="ml-3">
                <span class="block font-medium text-gray-900 dark:text-white">{{ dataType.name }}</span>
                <span class="block text-sm text-gray-500 dark:text-gray-400">{{ dataType.description }}</span>
              </label>
            </div>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ dataType.size }}</span>
          </div>
        </div>

        <div class="mt-6 flex items-center">
          <input
            id="select-all"
            v-model="selectAll"
            type="checkbox"
            class="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="select-all" class="ml-2 text-sm font-medium text-gray-900 dark:text-white">
            Tout sélectionner
          </label>
        </div>
      </div>

      <!-- Format d'export -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Format d'export</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            v-for="format in exportFormats"
            :key="format.id"
            @click="selectedFormat = format.id"
            :class="[
              'p-4 border rounded-lg text-center transition-colors',
              selectedFormat === format.id
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600'
            ]"
          >
            <div class="text-2xl mb-2">{{ format.icon }}</div>
            <div class="font-medium text-gray-900 dark:text-white">{{ format.name }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ format.description }}</div>
          </button>
        </div>
      </div>

      <!-- Options d'export -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Options d'export</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Plage de dates
            </label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Du</label>
                <input
                  v-model="dateRange.start"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Au</label>
                <input
                  v-model="dateRange.end"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Compression
            </label>
            <div class="flex items-center space-x-4">
              <label class="flex items-center">
                <input
                  v-model="compression"
                  type="radio"
                  value="none"
                  class="text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Aucune</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="compression"
                  type="radio"
                  value="zip"
                  class="text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">ZIP</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Résumé et actions -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Résumé de l'export</h2>
        
        <div class="space-y-4">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Types de données sélectionnés :</span>
            <span class="font-medium text-gray-900 dark:text-white">{{ selectedTypes.length }} sur {{ exportTypes.length }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Format :</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {{ exportFormats.find(f => f.id === selectedFormat)?.name }}
            </span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Taille estimée :</span>
            <span class="font-medium text-gray-900 dark:text-white">{{ estimatedSize }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Temps estimé :</span>
            <span class="font-medium text-gray-900 dark:text-white">{{ estimatedTime }}</span>
          </div>
        </div>

        <div class="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div class="flex">
            <svg class="w-5 h-5 text-blue-500 dark:text-blue-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-blue-700 dark:text-blue-300">
              Une fois l'export lancé, vous recevrez un email avec un lien de téléchargement valable 7 jours. 
              Le traitement peut prendre plusieurs minutes en fonction de la quantité de données.
            </p>
          </div>
        </div>

        <div class="mt-8 flex justify-end">
          <button
            @click="requestExport"
            :disabled="selectedTypes.length === 0 || isExporting"
            class="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isExporting">Préparation en cours...</span>
            <span v-else>Lancer l'export</span>
          </button>
        </div>
      </div>

      <!-- Historique des exports -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Historique des exports</h2>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Types</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Format</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Statut</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="exportItem in exportHistory" :key="exportItem.id">
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                  {{ formatDate(exportItem.date) }}
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-1">
                    <span v-for="type in exportItem.types.slice(0, 2)" :key="type" class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                      {{ type }}
                    </span>
                    <span v-if="exportItem.types.length > 2" class="px-2 py-1 text-xs text-gray-500">
                      +{{ exportItem.types.length - 2 }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                  {{ exportItem.format }}
                </td>
                <td class="px-4 py-3">
                  <span :class="[
                    'px-2 py-1 text-xs rounded-full font-medium',
                    exportItem.status === 'completed' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' :
                    exportItem.status === 'processing' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
                    'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                  ]">
                    {{ getStatusText(exportItem.status) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <button
                    v-if="exportItem.status === 'completed'"
                    @click="downloadExport(exportItem.id)"
                    class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                  >
                    Télécharger
                  </button>
                  <span v-else class="text-sm text-gray-500 dark:text-gray-400">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="exportHistory.length === 0" class="text-center py-8">
          <svg class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-4 text-gray-500 dark:text-gray-400">Aucun export effectué</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import definePageMeta pour éviter l'erreur
import { definePageMeta } from '#imports'

definePageMeta({
  layout: 'default',
  requiresAuth: true
})

import { ref, computed, onMounted } from 'vue'

interface ExportType {
  id: string
  name: string
  description: string
  size: string
}

interface ExportFormat {
  id: string
  name: string
  description: string
  icon: string
}

interface ExportHistoryItem {
  id: string
  date: string
  types: string[]
  format: string
  status: 'processing' | 'completed' | 'failed'
  size: string
}

interface DateRange {
  start: string
  end: string
}

const exportTypes = ref<ExportType[]>([
  {
    id: 'profile',
    name: 'Profil',
    description: 'Informations personnelles et paramètres',
    size: '5 KB'
  },
  {
    id: 'history',
    name: 'Historique de recherche',
    description: 'Toutes vos recherches et résultats',
    size: '150 KB'
  },
  {
    id: 'saved',
    name: 'Recherches sauvegardées',
    description: 'Vos recherches favorites et collections',
    size: '50 KB'
  },
  {
    id: 'notifications',
    name: 'Notifications',
    description: 'Historique des notifications',
    size: '25 KB'
  },
  {
    id: 'preferences',
    name: 'Préférences',
    description: 'Paramètres et configurations personnelles',
    size: '10 KB'
  }
])

const exportFormats = ref<ExportFormat[]>([
  {
    id: 'json',
    name: 'JSON',
    description: 'Format structuré pour développeurs',
    icon: '{}'
  },
  {
    id: 'csv',
    name: 'CSV',
    description: 'Format tableur compatible Excel',
    icon: '📊'
  },
  {
    id: 'html',
    name: 'HTML',
    description: 'Format web consultable',
    icon: '🌐'
  }
])

const exportHistory = ref<ExportHistoryItem[]>([
  {
    id: '1',
    date: new Date(Date.now() - 86400000).toISOString(),
    types: ['profile', 'history'],
    format: 'JSON',
    status: 'completed',
    size: '155 KB'
  },
  {
    id: '2',
    date: new Date(Date.now() - 259200000).toISOString(),
    types: ['history'],
    format: 'CSV',
    status: 'completed',
    size: '150 KB'
  }
])

const selectedTypes = ref<string[]>(['profile', 'history'])
const selectedFormat = ref('json')
const dateRange = ref<DateRange>({
  start: '',
  end: ''
})
const compression = ref('zip')
const isExporting = ref(false)
const selectAll = ref(false)

const estimatedSize = computed(() => {
  const totalKB = exportTypes.value
    .filter(type => selectedTypes.value.includes(type.id))
    .reduce((sum, type) => {
      const size = parseInt(type.size)
      return sum + (isNaN(size) ? 0 : size)
    }, 0)
  
  if (totalKB < 1000) return `${totalKB} KB`
  return `${(totalKB / 1000).toFixed(2)} MB`
})

const estimatedTime = computed(() => {
  const count = selectedTypes.value.length
  if (count === 0) return '-'
  if (count <= 2) return '1-2 minutes'
  if (count <= 4) return '2-5 minutes'
  return '5-10 minutes'
})

onMounted(() => {
  const today = new Date()
  const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
  
  // Utiliser l'opérateur de coalescence nulle
  const todayStr = today.toISOString().split('T')[0] || ''
  const lastMonthStr = lastMonth.toISOString().split('T')[0] || ''
  
  dateRange.value = {
    start: lastMonthStr,
    end: todayStr
  }
})

const requestExport = async () => {
  if (selectedTypes.value.length === 0) {
    alert('Veuillez sélectionner au moins un type de données')
    return
  }

  isExporting.value = true
  
  try {
    // Simulation de traitement
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const newExport: ExportHistoryItem = {
      id: Date.now().toString(),
      date: new Date().toISOString(),
      types: selectedTypes.value,
      format: selectedFormat.value.toUpperCase(),
      status: 'processing',
      size: estimatedSize.value
    }
    
    exportHistory.value.unshift(newExport)
    
    // Simuler la progression
    setTimeout(() => {
      newExport.status = 'completed'
      alert('Votre export est prêt ! Vous recevrez un email avec le lien de téléchargement.')
    }, 3000)
    
  } finally {
    isExporting.value = false
  }
}

const downloadExport = (id: string) => {
  const exportItem = exportHistory.value.find(item => item.id === id)
  if (exportItem) {
    // Simulation de téléchargement
    const blob = new Blob(['Simulated export data'], { type: 'application/octet-stream' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `export-${exportItem.date.split('T')[0] || 'unknown'}.${exportItem.format.toLowerCase()}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'processing': 'En cours',
    'completed': 'Terminé',
    'failed': 'Échec'
  }
  return statusMap[status] || status
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Gestion de la sélection totale
// Utilisation simple sans watch
const handleSelectAll = () => {
  if (selectAll.value) {
    selectedTypes.value = exportTypes.value.map(type => type.id)
  } else {
    selectedTypes.value = []
  }
}
</script>