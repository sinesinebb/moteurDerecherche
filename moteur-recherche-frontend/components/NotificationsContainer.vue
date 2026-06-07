<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80 max-w-[90vw]">
    <TransitionGroup name="toast">
      <div
        v-for="notif in notifications"
        :key="notif.id"
        :class="[
          'rounded-lg px-4 py-3 shadow-lg text-sm flex items-start gap-3',
          notif.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800 dark:bg-green-900/30 dark:border-green-800 dark:text-green-200' :
          notif.type === 'error' ? 'bg-red-50 border border-red-200 text-red-800 dark:bg-red-900/30 dark:border-red-800 dark:text-red-200' :
          notif.type === 'warning' ? 'bg-yellow-50 border border-yellow-200 text-yellow-800 dark:bg-yellow-900/30 dark:border-yellow-800 dark:text-yellow-200' :
          'bg-blue-50 border border-blue-200 text-blue-800 dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-200'
        ]"
      >
        <!-- Icône -->
        <span class="flex-shrink-0 mt-0.5">
          <span v-if="notif.type === 'success'">✅</span>
          <span v-else-if="notif.type === 'error'">❌</span>
          <span v-else-if="notif.type === 'warning'">⚠️</span>
          <span v-else>ℹ️</span>
        </span>
        <!-- Message -->
        <span class="flex-1">{{ notif.message }}</span>
        <!-- Bouton fermer -->
        <button @click="remove(notif.id)" class="flex-shrink-0 text-current opacity-60 hover:opacity-100">✕</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useNotifications } from '../composables/useNotifications'

const { notifications, remove } = useNotifications()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>