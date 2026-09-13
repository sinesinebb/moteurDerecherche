// stores/syne.store.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSyneStore = defineStore('syne', () => {
  const isChatOpen = ref(false) 

  function toggleChat() { isChatOpen.value = !isChatOpen.value }
  function openChat() { isChatOpen.value = true }
  function closeChat() { isChatOpen.value = false }

  return { isChatOpen, toggleChat, openChat, closeChat }
})