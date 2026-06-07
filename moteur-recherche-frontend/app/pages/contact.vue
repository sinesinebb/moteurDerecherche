<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900/10']">
    <div class="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- En-tête -->
      <div class="text-center mb-12 animate-fade-in-down">
        <div class="inline-flex items-center justify-center space-x-4 mb-6">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 p-2">
            <div class="w-full h-full bg-white dark:bg-gray-900 rounded-xl flex items-center justify-center">
              <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div>
            <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Nous <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Contacter</span>
            </h1>
            <p class="text-gray-600 dark:text-gray-400 text-lg">
              Une question, un bug à signaler, ou une suggestion d'amélioration ?
            </p>
          </div>
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-8 mb-12">
        <!-- Formulaire de contact -->
        <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Envoyez-nous un message</h2>
          
          <form @submit.prevent="submitContactForm" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Prénom
                </label>
                <input
                  v-model="form.firstName"
                  type="text"
                  required
                  class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nom
                </label>
                <input
                  v-model="form.lastName"
                  type="text"
                  required
                  class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                >
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email
              </label>
              <input
                v-model="form.email"
                type="email"
                required
                class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sujet
              </label>
              <select
                v-model="form.subject"
                class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Sélectionnez un sujet</option>
                <option value="bug">Signaler un bug</option>
                <option value="feature">Suggestion de fonctionnalité</option>
                <option value="support">Support technique</option>
                <option value="partnership">Partenariat</option>
                <option value="other">Autre</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Message
              </label>
              <textarea
                v-model="form.message"
                rows="6"
                required
                class="w-full px-4 py-3 bg-white/50 dark:bg-gray-700/50 border border-gray-300/50 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="Décrivez votre requête en détail..."
              ></textarea>
            </div>
            
            <div class="flex items-center">
              <input
                v-model="form.consent"
                type="checkbox"
                required
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              >
              <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                J'accepte que mes données soient traitées conformément à la 
                <NuxtLink to="/privacy" class="text-blue-600 dark:text-blue-400 hover:underline">
                  politique de confidentialité
                </NuxtLink>
              </label>
            </div>
            
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl text-lg font-semibold transition-all duration-200 hover:scale-105 flex items-center justify-center"
            >
              <svg v-if="isSubmitting" class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              {{ isSubmitting ? 'Envoi en cours...' : 'Envoyer le message' }}
            </button>
          </form>
        </div>
        
        <!-- Informations de contact -->
        <div class="space-y-6">
          <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 backdrop-blur-xl rounded-2xl border border-blue-200/50 dark:border-blue-700/50 p-6">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Informations de contact</h3>
            
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Support technique</p>
                  <p class="text-gray-600 dark:text-gray-400">+242 06 937 30 53</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Email</p>
                  <p class="text-gray-600 dark:text-gray-400">support@search.dev</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">Bureau</p>
                  <p class="text-gray-600 dark:text-gray-400">Brazzaville, Congo</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Statut du support -->
          <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Statut du support</h3>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-gray-700 dark:text-gray-300">Temps de réponse moyen</span>
                <span class="font-semibold text-green-600 dark:text-green-400">2 heures</span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-gray-700 dark:text-gray-300">Support actif</span>
                <div class="flex items-center">
                  <div class="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></div>
                  <span class="font-semibold text-gray-900 dark:text-white">En ligne</span>
                </div>
              </div>
              
              <div class="pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Notre équipe de support est disponible du lundi au vendredi, de 9h à 18h (CET).
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

import { ref } from 'vue'
import { useThemeStore } from '../../stores/theme.store'

const themeStore = useThemeStore()

// États
const isSubmitting = ref(false)

// Formulaire
const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  subject: '',
  message: '',
  consent: false
})

// Méthodes
const submitContactForm = async () => {
  isSubmitting.value = true
  
  try {
    // Simulation d'envoi
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // En production, vous feriez un appel API ici
    // await $fetch('/api/contact', {
    //   method: 'POST',
    //   body: form.value
    // })
    
    alert('Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
    
    // Réinitialiser le formulaire
    form.value = {
      firstName: '',
      lastName: '',
      email: '',
      subject: '',
      message: '',
      consent: false
    }
  } catch (error) {
    console.error('Erreur lors de l\'envoi:', error)
    alert('Une erreur est survenue. Veuillez réessayer.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
@keyframes fade-in-down {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-down {
  animation: fade-in-down 0.6s ease-out;
}
</style>