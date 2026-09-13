import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface Conversation {
  id: string
  title: string
  createdAt: number
  messages: ChatMessage[]
}

export const useChatHistoryStore = defineStore('chatHistory', () => {
  const conversations = ref<Conversation[]>([])
  const activeConversationId = ref<string | null>(null)

  // Charger depuis le localStorage (côté client uniquement)
  function loadFromStorage() {
    if (process.client) {
      const saved = localStorage.getItem('syne-conversations')
      if (saved) {
        conversations.value = JSON.parse(saved)
      }
      const activeId = localStorage.getItem('syne-active-conversation')
      if (activeId) activeConversationId.value = activeId
    }
  }

  // Sauvegarder automatiquement à chaque modification
  watch(conversations, (val) => {
    if (process.client) localStorage.setItem('syne-conversations', JSON.stringify(val))
  }, { deep: true })

  watch(activeConversationId, (val) => {
    if (process.client) localStorage.setItem('syne-active-conversation', val || '')
  })

  function createConversation(): string {
    const id = Date.now().toString(36) + Math.random().toString(36).substring(2, 8)
    const newConv: Conversation = {
      id,
      title: 'Nouvelle conversation',
      createdAt: Date.now(),
      messages: []
    }
    conversations.value.unshift(newConv)
    activeConversationId.value = id
    return id
  }

  function deleteConversation(id: string) {
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (activeConversationId.value === id) {
      activeConversationId.value = conversations.value[0]?.id || null
    }
  }

  function setActiveConversation(id: string) {
    activeConversationId.value = id
  }

  function updateConversationMessages(id: string, messages: ChatMessage[]) {
    const conv = conversations.value.find(c => c.id === id)
    if (conv) {
      conv.messages = messages
      // Mettre à jour le titre avec le premier message utilisateur
      if (messages.length > 0 && conv.title === 'Nouvelle conversation') {
        const firstUserMsg = messages.find(m => m.role === 'user')
        if (firstUserMsg) {
          conv.title = firstUserMsg.content.slice(0, 50) + (firstUserMsg.content.length > 50 ? '…' : '')
        }
      }
    }
  }

  const activeConversation = computed(() =>
    conversations.value.find(c => c.id === activeConversationId.value) || null
  )

  return {
    conversations,
    activeConversationId,
    activeConversation,
    loadFromStorage,
    createConversation,
    deleteConversation,
    setActiveConversation,
    updateConversationMessages
  }
})