// composables/useNotifications.ts
import { ref } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number  // ms, défaut 5000
}

const notifications = ref<Notification[]>([])

export function useNotifications() {
  const add = (type: Notification['type'], message: string, duration = 5000) => {
    const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 7)
    notifications.value.push({ id, type, message, duration })
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
  }

  const remove = (id: string) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return {
    notifications,
    add,
    remove,
    success: (msg: string, dur?: number) => add('success', msg, dur),
    error: (msg: string, dur?: number) => add('error', msg, dur),
    warning: (msg: string, dur?: number) => add('warning', msg, dur),
    info: (msg: string, dur?: number) => add('info', msg, dur),
  }
}