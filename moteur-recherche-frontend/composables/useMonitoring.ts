// moteur-recherche-frontend/composables/useMonitoring.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { adminService } from '../utils/api'

export interface ServiceStatus {
  name: string
  status: 'running' | 'stopped' | 'error'
  cpu: number
  memory: number
  uptime: number
  requests: number
  errors: number
}

export interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: number
  activeUsers: number
  requestsPerMinute: number
}

export const useMonitoring = () => {
  const services = ref<ServiceStatus[]>([])
  const metrics = ref<SystemMetrics>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    activeUsers: 0,
    requestsPerMinute: 0
  })
  const isLoading = ref(false)
  const autoRefresh = ref(true)
  let refreshInterval: NodeJS.Timeout | null = null

  const fetchServicesStatus = async () => {
    try {
      const response = await adminService.getServiceStatus()
      services.value = response.services
    } catch (error) {
      console.error('Error fetching service status:', error)
    }
  }

  const fetchSystemMetrics = async () => {
    try {
      const response = await adminService.getSystemStats()
      metrics.value = response.metrics
    } catch (error) {
      console.error('Error fetching system metrics:', error)
    }
  }

  const restartService = async (serviceName: string) => {
    try {
      isLoading.value = true
      await adminService.restartService(serviceName)
      await fetchServicesStatus()
    } catch (error) {
      console.error('Error restarting service:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const startAutoRefresh = () => {
    if (refreshInterval) clearInterval(refreshInterval)
    
    refreshInterval = setInterval(async () => {
      await Promise.all([
        fetchServicesStatus(),
        fetchSystemMetrics()
      ])
    }, 5000) // Rafraîchir toutes les 5 secondes
  }

  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  onMounted(async () => {
    await Promise.all([
      fetchServicesStatus(),
      fetchSystemMetrics()
    ])
    
    if (autoRefresh.value) {
      startAutoRefresh()
    }
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    services,
    metrics,
    isLoading,
    autoRefresh,
    fetchServicesStatus,
    fetchSystemMetrics,
    restartService,
    startAutoRefresh,
    stopAutoRefresh
  }
}