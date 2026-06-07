<template>
  <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ title }}</h3>
      <div class="flex items-center space-x-2">
        <span v-if="isLoading" class="text-sm text-gray-500">
          <svg class="w-4 h-4 animate-spin inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Mise à jour...
        </span>
        <span v-else class="text-xs text-gray-500">Dernière mise à jour : {{ lastUpdate }}</span>
      </div>
    </div>
    <div class="h-64" ref="chartRef"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { useAuthStore } from '../../stores/auth.store'

const props = defineProps<{
  title: string
  query: string
  unit?: string
  refreshInterval?: number
}>()

const authStore = useAuthStore()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
const isLoading = ref(false)
const lastUpdate = ref('')
let interval: number | null = null

const fetchData = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const response = await $fetch('http://localhost/api/admin/metrics/query', {
      params: {
        query: props.query,
        start: 'now-1h',
        end: 'now',
        step: '15s'
      },
      headers
    })
    console.log(`[${props.title}] Données reçues`, response)
    updateChart(response)
    lastUpdate.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error(`[${props.title}] Erreur:`, error)
  } finally {
    isLoading.value = false
  }
}

const updateChart = (data: any) => {
  if (!chart) return
  if (!data.data || !data.data.result || data.data.result.length === 0) {
    chart.setOption({
      title: { show: true, text: 'Aucune donnée', left: 'center', top: 'center' }
    })
    return
  }
  const series = data.data.result.map((result: any) => {
    const name = result.metric.status || result.metric.__name__ || 'valeur'
    const values = result.values.map(([timestamp, value]: [number, string]) => [timestamp * 1000, parseFloat(value)])
    return {
      name,
      type: 'line',
      data: values,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2 }
    }
  })
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value: number) => value + (props.unit ? ` ${props.unit}` : '')
    },
    xAxis: { type: 'time', axisLabel: { fontSize: 10, rotate: 0 } },
    yAxis: { type: 'value', name: props.unit, nameTextStyle: { fontSize: 10 } },
    series,
    grid: { left: '5%', right: '5%', bottom: '10%', top: '10%', containLabel: true },
    legend: { show: series.length > 1, bottom: 0, icon: 'circle', itemWidth: 8 }
  })
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    fetchData()
    if (props.refreshInterval && props.refreshInterval > 0) {
      interval = window.setInterval(fetchData, props.refreshInterval * 1000)
    }
  }
})

onBeforeUnmount(() => {
  if (interval) clearInterval(interval)
  if (chart) chart.dispose()
})

watch(() => props.query, () => fetchData())
</script>