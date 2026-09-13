<template>
  <div class="flex h-screen w-full font-sans overflow-hidden" :class="themeClasses">
    <!-- Sidebar Gauche -->
    <aside
      class="flex flex-col border-r shadow-xl z-10 transition-all duration-300 ease-in-out"
      :class="[
        sidebarCollapsed ? 'w-16' : 'w-64 px-4 py-6',
        isDark ? 'bg-[#18181b] border-white/5' : 'bg-white border-gray-200'
      ]"
    >
      <!-- Header Sidebar -->
      <div class="flex items-center mb-6" :class="sidebarCollapsed ? 'justify-center mt-2' : 'justify-between'">
        <h1 v-if="!sidebarCollapsed" class="text-lg font-bold tracking-tight" :class="isDark ? 'text-white' : 'text-gray-900'">Syne</h1>
        <button @click="toggleSidebar" class="text-sm" :class="isDark ? 'text-zinc-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'" :title="sidebarCollapsed ? 'Étendre le menu' : 'Réduire le menu'">
          <svg v-if="!sidebarCollapsed" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M15 3v18"/></svg>
        </button>
      </div>
      <!-- Navigation principale -->
      <nav class="space-y-1 mb-6" :class="sidebarCollapsed ? 'mt-4' : ''">
        <a href="#" @click.prevent="newConversation"
           class="flex items-center gap-3 rounded-lg px-2 py-2 text-sm font-medium hover:bg-white/5 transition-colors"
           :class="[sidebarCollapsed ? 'justify-center' : '', isDark ? 'text-white' : 'text-gray-900']"
           title="Nouvelle conversation">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 15h6"/><path d="M12 18v-6"/></svg>
          <span v-if="!sidebarCollapsed">Nouveau chat</span>
        </a>
        <a href="#" @click.prevent="focusInput"
           class="flex items-center gap-3 rounded-lg px-2 py-2 text-sm font-medium hover:bg-white/5 transition-colors"
           :class="[sidebarCollapsed ? 'justify-center' : '', isDark ? 'text-zinc-400 hover:text-white' : 'text-gray-600 hover:text-gray-900']"
           title="Rechercher">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <span v-if="!sidebarCollapsed">Rechercher</span>
        </a>
        <a href="#" @click.prevent="view = 'settings'"
           class="flex items-center gap-3 rounded-lg px-2 py-2 text-sm font-medium hover:bg-white/5 transition-colors"
           :class="[sidebarCollapsed ? 'justify-center' : '', view === 'settings' ? (isDark ? 'text-white bg-white/5' : 'text-gray-900 bg-gray-200') : (isDark ? 'text-zinc-400 hover:text-white' : 'text-gray-600 hover:text-gray-900')]"
           title="Paramètres">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
          <span v-if="!sidebarCollapsed">Paramètres</span>
        </a>
      </nav>
      <!-- Conversations Récentes -->
      <div v-if="!sidebarCollapsed" class="flex-1 overflow-y-auto custom-scrollbar">
        <h2 class="mb-3 px-2 text-xs font-semibold uppercase tracking-wider" :class="isDark ? 'text-zinc-500' : 'text-gray-500'">Conversations récentes</h2>
        <ul class="space-y-1">
          <li v-for="conv in conversations" :key="conv.id" class="group flex items-center gap-1">
            <!-- Lien de chargement de la conversation -->
            <a href="#" @click.prevent="loadConversation(conv.id)"
              class="flex-1 truncate rounded-lg px-2 py-2 text-sm hover:bg-white/5 transition-colors"
              :class="[
                isDark ? 'text-white' : 'text-gray-800',
                currentConversationId === conv.id ? (isDark ? 'bg-white/10' : 'bg-gray-200') : ''
              ]">
              {{ conv.title }}
            </a>

            <!-- Bouton supprimer (apparaît au survol) -->
            <button 
              @click.stop="deleteConversation(conv.id)"
              class="shrink-0 p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-all"
              title="Supprimer cette conversation"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 6h18"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
            </button>
          </li>

          <li v-if="conversations.length === 0">
            <span class="block truncate rounded-lg px-2 py-2 text-sm" :class="isDark ? 'text-zinc-500' : 'text-gray-500'">Aucune conversation</span>
          </li>
        </ul>
      </div>
    </aside>
    <!-- Contenu Principal -->
    <main class="flex-1 flex flex-col relative overflow-hidden min-h-0" :class="isDark ? 'bg-[#0a0a0a]' : 'bg-gray-100'">
      <!-- Zone centrale -->
      <div class="flex-1 flex flex-col overflow-hidden min-h-0" ref="chatMessages">
        <!-- Vue Settings (seulement le choix du theme) -->
        <ClientOnly>
          <div v-if="view === 'settings'" class="max-w-xl mx-auto space-y-6 p-6">
            <h2 class="text-2xl font-bold" :class="isDark ? 'text-white' : 'text-gray-900'">Paramètres</h2>
            <div>
              <h3 class="text-lg font-semibold mb-3" :class="isDark ? 'text-white' : 'text-gray-900'">Thème</h3>
              <div class="flex gap-4">
                <button @click="setTheme('system')" class="flex flex-col items-center gap-2 p-4 rounded-xl border transition-colors" :class="theme === 'system' ? (isDark ? 'border-blue-500 bg-blue-500/10 text-blue-400' : 'border-blue-600 bg-blue-50 text-blue-600') : (isDark ? 'border-white/10 hover:bg-white/5 text-zinc-400' : 'border-gray-200 hover:bg-gray-100 text-gray-600')">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2"/><path d="M12 2v20"/><path d="m4.93 4.93 14.14 14.14"/></svg>
                  <span class="text-xs font-medium">Système</span>
                </button>
                <button @click="setTheme('light')" class="flex flex-col items-center gap-2 p-4 rounded-xl border transition-colors" :class="theme === 'light' ? (isDark ? 'border-blue-500 bg-blue-500/10 text-blue-400' : 'border-blue-600 bg-blue-50 text-blue-600') : (isDark ? 'border-white/10 hover:bg-white/5 text-zinc-400' : 'border-gray-200 hover:bg-gray-100 text-gray-600')">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
                  <span class="text-xs font-medium">Clair</span>
                </button>
                <button @click="setTheme('dark')" class="flex flex-col items-center gap-2 p-4 rounded-xl border transition-colors" :class="theme === 'dark' ? (isDark ? 'border-blue-500 bg-blue-500/10 text-blue-400' : 'border-blue-600 bg-blue-50 text-blue-600') : (isDark ? 'border-white/10 hover:bg-white/5 text-zinc-400' : 'border-gray-200 hover:bg-gray-100 text-gray-600')">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
                  <span class="text-xs font-medium">Sombre</span>
                </button>
              </div>
            </div>
          </div>
        </ClientOnly>
        <!-- Vue Chat -->
        <template v-if="view === 'chat'">
          <!-- Écran d'accueil centré -->
          <div v-if="currentMessages.length === 0" class="flex-1 flex flex-col items-center justify-center p-4">
            <div class="text-center mb-8">
              <h1 class="text-4xl font-medium tracking-tight mb-2" :class="isDark ? 'text-white' : 'text-gray-900'">Bonjour</h1>
              <p class="font-light text-lg" :class="isDark ? 'text-zinc-500' : 'text-gray-500'">Tapez un message pour commencer</p>
            </div>
            <div class="w-full max-w-2xl">
              <div class="flex items-center gap-3 rounded-3xl px-4 py-3 shadow-sm ring-1 transition-shadow" :class="isDark ? 'bg-[#262626] ring-white/5 focus-within:ring-white/10' : 'bg-white ring-gray-200 focus-within:ring-gray-300'">
                <input ref="inputField" v-model="input" @keypress.enter="send" type="text" placeholder="Tapez un message..." :disabled="loading" class="flex-1 bg-transparent outline-none text-sm" :class="isDark ? 'text-white placeholder-zinc-500' : 'text-gray-900 placeholder-gray-400'" />
                <button @click="send" :disabled="loading || !input.trim()" class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed" :class="isDark ? 'bg-zinc-700 text-white hover:bg-zinc-600' : 'bg-gray-700 text-white hover:bg-gray-600'">
                  <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg>
                  <span v-else class="text-xs">...</span>
                </button>
              </div>
            </div>
          </div>
          <!-- Conversation active : messages + barre en bas -->
          <template v-else>
            <div class="flex-1 overflow-y-auto px-4 py-6">
              <div class="max-w-3xl mx-auto space-y-4">
                <div v-for="(msg, index) in currentMessages" :key="index" :class="['flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start']">
                  <div v-if="msg.role === 'assistant'" class="w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0" :class="isDark ? 'bg-[#18181b]' : 'bg-gray-200'">AI</div>
                  <div class="max-w-[75%]">
                    <div class="p-3 rounded-2xl text-sm leading-relaxed"
                      :class="msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-md' : (isDark ? 'bg-[#18181b] text-zinc-200' : 'bg-white border border-gray-200 text-gray-800') + ' rounded-bl-md'"
                    >
                      <div v-html="formatText(msg.content)"></div>
                    </div>
                    <div class="text-xs opacity-70 text-right mt-1">{{ formatTime(msg.timestamp) }}</div>
                  </div>
                  <div v-if="msg.role === 'user'" class="w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0" :class="isDark ? 'bg-[#18181b]' : 'bg-gray-200'">U</div>
                </div>
                <div v-if="loading" class="flex gap-3 justify-start">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm" :class="isDark ? 'bg-[#18181b]' : 'bg-gray-200'">AI</div>
                  <div class="rounded-2xl p-4 flex gap-1" :class="isDark ? 'bg-[#18181b]' : 'bg-white border-gray-200'">
                    <span class="w-2 h-2 rounded-full animate-bounce" :class="isDark ? 'bg-zinc-500' : 'bg-gray-400'"></span>
                    <span class="w-2 h-2 rounded-full animate-bounce delay-100" :class="isDark ? 'bg-zinc-500' : 'bg-gray-400'"></span>
                    <span class="w-2 h-2 rounded-full animate-bounce delay-200" :class="isDark ? 'bg-zinc-500' : 'bg-gray-400'"></span>
                  </div>
                </div>
              </div>
            </div>
            <!-- Barre de saisie basse -->
            <div class="p-4 border-t" :class="isDark ? 'border-white/5 bg-[#0a0a0a]' : 'border-gray-200 bg-gray-100'">
              <div class="flex items-center gap-3 max-w-3xl mx-auto rounded-3xl px-4 py-3 shadow-sm ring-1 transition-shadow" :class="isDark ? 'bg-[#262626] ring-white/5 focus-within:ring-white/10' : 'bg-white ring-gray-200 focus-within:ring-gray-300'">
                <input ref="inputField" v-model="input" @keypress.enter="send" type="text" placeholder="Tapez un message..." :disabled="loading" class="flex-1 bg-transparent outline-none text-sm" :class="isDark ? 'text-white placeholder-zinc-500' : 'text-gray-900 placeholder-gray-400'" />
                <button @click="send" :disabled="loading || !input.trim()" class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed" :class="isDark ? 'bg-zinc-700 text-white hover:bg-zinc-600' : 'bg-gray-700 text-white hover:bg-gray-600'">
                  <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg>
                  <span v-else class="text-xs">...</span>
                </button>
              </div>
            </div>
          </template>
        </template>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRuntimeConfig } from '#app'

// ===== THEME =====
const theme = ref('system')
const isDark = computed(() => {
  if (process.client) {
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    return theme.value === 'dark' || (theme.value === 'system' && systemDark)
  }
  return false
})
const themeClasses = computed(() => isDark.value ? 'theme-dark' : 'theme-light')

const setTheme = (newTheme) => {
  theme.value = newTheme
  localStorage.setItem('app-theme', newTheme)
}

if (process.client) {
  const savedTheme = localStorage.getItem('app-theme')
  if (savedTheme) theme.value = savedTheme
}

// ===== SIDEBAR =====
const sidebarCollapsed = ref(false)
const toggleSidebar = () => { sidebarCollapsed.value = !sidebarCollapsed.value }

// ===== VUES =====
const view = ref('chat')

// ===== HISTORIQUE =====
const conversations = ref([])
const currentConversationId = ref(null)
const currentMessages = ref([])

const loadConversations = () => {
  if (process.client) {
    const saved = localStorage.getItem('chatConversations')
    if (saved) conversations.value = JSON.parse(saved)
  }
}

const saveConversations = () => {
  localStorage.setItem('chatConversations', JSON.stringify(conversations.value))
}

const newConversation = () => {
  const id = Date.now().toString()
  currentConversationId.value = id
  currentMessages.value = []
  input.value = ''
  conversations.value.unshift({
    id,
    title: 'Nouvelle conversation',
    date: new Date().toLocaleDateString('fr-FR'),
    messages: []
  })
  saveConversations()
  view.value = 'chat'
}

const loadConversation = (id) => {
  const conv = conversations.value.find(c => c.id === id)
  if (conv) {
    currentConversationId.value = id
    currentMessages.value = conv.messages || []
    view.value = 'chat'
    scrollToBottom()
  }
}

const deleteConversation = (id) => {
  if (!id) return
  conversations.value = conversations.value.filter(c => c.id !== id)
  if (currentConversationId.value === id) {
    currentConversationId.value = null
    currentMessages.value = []
  }
  saveConversations()
}

const updateCurrentConversation = () => {
  if (!currentConversationId.value) {
    newConversation()
    return
  }
  const conv = conversations.value.find(c => c.id === currentConversationId.value)
  if (conv) {
    conv.messages = [...currentMessages.value]
    const firstUser = currentMessages.value.find(n => n.role === 'user')
    if (firstUser) {
      conv.title = firstUser.content.substring(0, 40) + (firstUser.content.length > 40 ? '...' : '')
    }
    conv.date = new Date().toLocaleDateString('fr-FR')
    saveConversations()
  }
}

// ===== UTILITAIRES =====
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

const formatText = (text) => {
  return text.replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

const focusInput = () => {
  view.value = 'chat'
  nextTick(() => inputField.value?.focus())
}

// ===== CHAT =====
const input = ref('')
const loading = ref(false)
const streamingContent = ref('')
const chatMessages = ref(null)
const inputField = ref(null)

const runtimeConfig = useRuntimeConfig()
const apiUrl = computed(() => runtimeConfig.public.chatbotUrl || '/api/ln/chat/completions')

const send = async () => {
  const question = input.value.trim()
  if (!question || loading.value) return

  currentMessages.value.push({ role: 'user', content: question, timestamp: Date.now() })
  input.value = ''
  loading.value = true
  streamingContent.value = ''
  scrollToBottom()

  if (!currentConversationId.value) newConversation()
  updateCurrentConversation()

  const assistantMsg = { role: 'assistant', content: '', timestamp: Date.now() }
  currentMessages.value.push(assistantMsg)

  try {
    const systemPrompt = 'Ton nom est Syne, tu as été créé par BAKOUETILA Mouhamed Yassine. Tu es un assistant. Réponds en français.'
    const response = await fetch(apiUrl.value, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'local',
        messages: [
          { role: 'system', content: systemPrompt },
          ...currentMessages.value
            .filter(m => m.role !== 'assistant' || m.content !== '')
            .map(m => ({ role: m.role, content: m.content }))
        ],
        temperature: 0.1,
        max_tokens: 2048,
        stream: true
      })
    })

    if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullContent = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      if (value) {
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '))
        for (const line of lines) {
          const jsonStr = line.replace('data: ', '')
          if (jsonStr === '[DONE]') break
          try {
            const json = JSON.parse(jsonStr)
            const content = json.choices?.[0]?.delta?.content
            if (content) {
              fullContent += content
              assistantMsg.content = fullContent
              streamingContent.value = fullContent
              scrollToBottom()
              await nextTick()
            }
          } catch (e) {}
        }
      }
    }

    assistantMsg.content = fullContent
    assistantMsg.timestamp = Date.now()
    streamingContent.value = ''
    updateCurrentConversation()
  } catch (err) {
    assistantMsg.content = `⚠️ Erreur : ${err.message}`
    updateCurrentConversation()
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  loadConversations()
  if (conversations.value.length > 0) {
    loadConversation(conversations.value[0].id)
  } else {
    newConversation()
  }
  inputField.value?.focus()
})
</script>

<style>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 9999px; }

html, body, #__nuxt {
  height: 100%;
  margin: 0;
  padding: 0;
}

.min-h-0 {
  min-height: 0;
}
</style>