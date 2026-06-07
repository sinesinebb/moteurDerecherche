import { ref, onUnmounted } from 'vue'

export function useWebSocket(url: string, options?: { onMessage?: (data: any) => void }) {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  let pingInterval: ReturnType<typeof setInterval> | null = null

  const scheduleReconnect = () => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    const baseDelay = 5000
    const delay = Math.min(baseDelay * Math.pow(1.5, reconnectAttempts), 30000)
    console.log(`[WS] Tentative de reconnexion dans ${delay}ms`)
    reconnectTimer = setTimeout(() => {
      reconnectAttempts++
      connect()
    }, delay)
  }

  const connect = () => {
    if (socket.value?.readyState === WebSocket.OPEN) return
    if (socket.value?.readyState === WebSocket.CONNECTING) return

    console.log('[WS] Connexion à', url)
    socket.value = new WebSocket(url)

    socket.value.onopen = () => {
      isConnected.value = true
      reconnectAttempts = 0
      console.log('[WS] Connecté')
      pingInterval = setInterval(() => {
        if (socket.value?.readyState === WebSocket.OPEN) {
          socket.value.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)
    }

    socket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        options?.onMessage?.(data)
      } catch (e) {
        console.error('[WS] Message invalide', e)
      }
    }

    socket.value.onclose = (event) => {
      isConnected.value = false
      socket.value = null
      if (pingInterval) clearInterval(pingInterval)
      if (event.code !== 1000) {
        console.warn(`[WS] Fermé anormalement (code ${event.code}).`)
        scheduleReconnect()
      } else {
        console.log('[WS] Fermeture normale.')
      }
    }

    socket.value.onerror = (error) => {
      console.error('[WS] Erreur', error)
      socket.value?.close()
    }
  }

  const disconnect = () => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (pingInterval) clearInterval(pingInterval)
    if (socket.value) {
      socket.value.close(1000)
      socket.value = null
    }
    isConnected.value = false
    reconnectAttempts = 0
  }

  onUnmounted(disconnect)

  return { connect, disconnect, isConnected }
}