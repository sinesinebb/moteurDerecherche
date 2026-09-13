<template>
  <div class="min-h-screen bg-[#0f1117]">
    <ChatSyneEmbedded />
  </div>
</template>

<script setup>

definePageMeta({
  layout: false
})

// import { layout } from 'echarts/types/src/layout/barGrid.js';
import ChatSyneEmbedded from '~~/components/ChatSyneEmbedded.vue'
import { useChatHistoryStore } from '~~/stores/chatHistory.store'
</script>

<style>
html, body, #__nuxt {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>