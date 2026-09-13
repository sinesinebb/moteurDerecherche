import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth.store'
import { useFetch } from '#app'

// Interface pour la réponse de l'API llama.cpp (format chat completions)
interface OpenAiChoice {
  message: { content: string }
}
interface OpenAiResponse {
  choices: OpenAiChoice[]
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export const useSyneChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const authStore = useAuthStore()
  const userName = computed(() => authStore.user?.name || 'Utilisateur')

  const sendMessage = async (content: string) => {
    if (!content.trim()) return

    messages.value.push({ role: 'user', content })
    isLoading.value = true
    error.value = null

    try {
      // Typage explicite de la réponse 
      const { data, error: fetchError } = await useFetch<OpenAiResponse>('/api/syne/chat', {
        method: 'POST',
        body: { messages: [{ role: 'user', content }] }
      })

      const reply = data.value?.choices?.[0]?.message?.content
      if (reply) {
        messages.value.push({ role: 'assistant', content: reply })
      } else {
        throw new Error('Réponse vide')
      }
    } catch (e: any) {
      error.value = e.message
      messages.value.push({
        role: 'assistant',
        content: 'Désolé, une erreur est survenue.'
      })
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  return { messages, isLoading, error, sendMessage, clearMessages }
}