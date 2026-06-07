<!-- moteur-recherche-frontend/components/search/SearchBox.vue -->
<template>
  <div class="relative w-full max-w-2xl">
    <div class="relative">
      <div 
        class="absolute -inset-4 bg-gradient-to-r from-blue-200/0 via-blue-200/20 to-blue-200/0 dark:from-blue-500/0 dark:via-blue-500/10 dark:to-blue-500/0 rounded-full blur-xl transition-opacity duration-500"
        :class="{ 'opacity-100': isFocused, 'opacity-0': !isFocused }"
      ></div>
      
      <div 
        class="relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border transition-all duration-500"
        :class="isFocused ? 'border-blue-400 dark:border-blue-500 scale-[1.02]' : 'border-transparent hover:border-blue-200 dark:hover:border-gray-700'"
      >
        <div class="flex items-center px-6 py-4">
          <svg 
            class="w-5 h-5 mr-4 transition-all duration-300" 
            :class="isFocused ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500'"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          
          <input
            ref="searchInput"
            :value="modelValue"
            @input="onInput"
            @keyup.enter="handleSearch"
            @focus="onFocus"
            @blur="onBlur"
            type="text"
            :placeholder="placeholder"
            class="flex-1 bg-transparent border-0 focus:ring-0 focus:outline-none text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 text-base font-light tracking-wide h-8"
            autocomplete="off"
          />
          
          <button 
            @click="handleSearch"
            class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center hover:shadow-lg hover:scale-105 transition-all duration-300 ml-4"
            :class="modelValue.trim() ? 'opacity-100' : 'opacity-50'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Rechercher...'
  }
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'search': [value: string]
}>()

const searchInput = ref<HTMLInputElement | null>(null)
const isFocused = ref(false)

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const onFocus = () => {
  isFocused.value = true
}

const onBlur = () => {
  setTimeout(() => {
    isFocused.value = false
  }, 100)
}

const handleSearch = () => {
  emit('search', props.modelValue)
}

defineExpose({
  focus: () => {
    searchInput.value?.focus()
  }
})
</script>