<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero Section -->
    <div class="text-center mb-16">
      <h1 class="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
        À propos de <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Search.dev</span>
      </h1>
      <p class="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
        Un moteur de recherche spécialisé en informatique, construit avec une architecture microservices moderne.
      </p>
    </div>

    <!-- Mission -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-12">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Notre Mission</h2>
      <div class="grid md:grid-cols-2 gap-8">
        <div class="space-y-4">
          <div class="flex items-start space-x-4">
            <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Rapidité</h3>
              <p class="text-gray-600 dark:text-gray-400">Recherche ultra-rapide grâce à l'indexation distribuée et au cache intelligent.</p>
            </div>
          </div>
          
          <div class="flex items-start space-x-4">
            <div class="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Confidentialité</h3>
              <p class="text-gray-600 dark:text-gray-400">Respect total de votre vie privée, pas de tracking publicitaire ni de vente de données.</p>
            </div>
          </div>
        </div>
        
        <div class="space-y-4">
          <div class="flex items-start space-x-4">
            <div class="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Précision</h3>
              <p class="text-gray-600 dark:text-gray-400">Algorithmes de pertinence avancés et traitement NLP pour des résultats précis.</p>
            </div>
          </div>
          
          <div class="flex items-start space-x-4">
            <div class="w-12 h-12 rounded-xl bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Personnalisation</h3>
              <p class="text-gray-600 dark:text-gray-400">Expérience adaptée à vos besoins avec historique, favoris et préférences.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Technologies -->
    <div class="mb-12">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-8 text-center">Technologies Utilisées</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Nuxt 4</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Frontend moderne</p>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900/20 dark:to-green-800/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Python</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Backend & NLP</p>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-yellow-100 to-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Elasticsearch</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Indexation</p>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Kafka</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Messagerie</p>
        </div>
      </div>
    </div>

    <!-- Architecture -->
    <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-xl p-8">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Architecture Microservices</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Notre système est construit sur une architecture microservices moderne avec 9 services spécialisés :
      </p>
      <div class="grid md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800/50 rounded-xl p-6">
          <h3 class="font-bold text-gray-900 dark:text-white mb-3">Recherche & Indexation</h3>
          <ul class="space-y-2">
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
              Service Crawler
            </li>
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
              Service Indexing
            </li>
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
              Service Search
            </li>
          </ul>
        </div>
        
        <div class="bg-white dark:bg-gray-800/50 rounded-xl p-6">
          <h3 class="font-bold text-gray-900 dark:text-white mb-3">Intelligence</h3>
          <ul class="space-y-2">
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
              Service NLP
            </li>
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
              Service PageRank
            </li>
          </ul>
        </div>
        
        <div class="bg-white dark:bg-gray-800/50 rounded-xl p-6">
          <h3 class="font-bold text-gray-900 dark:text-white mb-3">Infrastructure</h3>
          <ul class="space-y-2">
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-purple-500 mr-2"></div>
              Service User
            </li>
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-purple-500 mr-2"></div>
              Service Admin
            </li>
            <li class="flex items-center text-gray-600 dark:text-gray-400">
              <div class="w-2 h-2 rounded-full bg-purple-500 mr-2"></div>
              Gateway Nginx
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6">
      <div class="text-center">
        <div class="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">10M+</div>
        <div class="text-gray-600 dark:text-gray-400">Documents indexés</div>
      </div>
      <div class="text-center">
        <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">99.9%</div>
        <div class="text-gray-600 dark:text-gray-400">Disponibilité</div>
      </div>
      <div class="text-center">
        <div class="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">&lt;200ms</div>
        <div class="text-gray-600 dark:text-gray-400">Temps de réponse</div>
      </div>
      <div class="text-center">
        <div class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-2">24/7</div>
        <div class="text-gray-600 dark:text-gray-400">Monitoring</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})
</script>