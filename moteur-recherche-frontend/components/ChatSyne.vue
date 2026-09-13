<template>
  <div>
    <!-- Bouton flottant d’ouverture (quand le chat n’est pas ouvert) -->
    <button
      v-if="!isChatOpen"
      class="syne-toggle"
      @click="syneStore.toggleChat()"
      title="Parler à Syne"
    >
      💬
    </button>

    <!-- Panneau de chat -->
    <div v-if="isChatOpen" class="syne-panel">
      <div class="syne-header">
        <span>Syne - Assistant</span>
        <button class="syne-close" @click="syneStore.closeChat()">✕</button>
      </div>

      <div class="syne-messages" ref="messagesContainer">
        <div
          v-for="msg in messages"
          :key="msg.role + msg.content"
          :class="['message', msg.role]"
        >
          <div class="message-content">
            <strong>{{ msg.role === 'user' ? 'Vous' : 'Syne' }} :</strong>
            <span v-html="formatContent(msg.content)"></span>
          </div>
        </div>

        <div v-if="syneChat.isLoading" class="message assistant">
          <em>Syne réfléchit…</em>
        </div>
      </div>

      <div class="syne-input-area">
        <input
          v-model="newMessage"
          @keyup.enter="send"
          placeholder="Posez une question…"
          :disabled="!!syneChat.isLoading"
        />
        <button @click="send" :disabled="!!syneChat.isLoading">Envoyer</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useSyneStore } from '../stores/syne.store'
import { useSyneChat } from '../composables/useSyneChat'
import type { Message } from '../composables/useSyneChat'

const syneStore = useSyneStore()
const { isChatOpen } = storeToRefs(syneStore) 

const syneChat = useSyneChat()
const newMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// Computed typée 
const messages = computed<Message[]>(() => syneChat.messages.value)

watch(() => syneChat.messages.value.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})

const send = () => {
  if (newMessage.value.trim()) {
    syneChat.sendMessage(newMessage.value)
    newMessage.value = ''
  }
}

function formatContent(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>

</style>