<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gray-50 dark:bg-[#202124]']">
    <header class="sticky top-0 z-50 bg-white/80 dark:bg-[#202124]/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo Search.dev -->
          <NuxtLink to="/" class="flex items-center space-x-2 group">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 p-1 group-hover:scale-105 transition-transform duration-300">
              <div class="w-full h-full bg-white dark:bg-[#202124] rounded-full flex items-center justify-center">
                <span class="text-xl">🔍</span>
              </div>
            </div>
            <div class="flex flex-col">
              <span class="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Search<span class="font-light">.dev</span>
              </span>
            </div>
          </NuxtLink>

          <!-- Barre de recherche style fond noir  -->
          <div class="flex-1 max-w-2xl mx-4">
            <div class="relative cinematic-search-wrapper">
              <div 
                class="relative bg-gradient-to-r from-[#303134] to-[#202124] dark:bg-[#303134] backdrop-blur-2xl rounded-full border transition-all duration-500 shadow-2xl overflow-hidden group"
                :class="isFocused || searchQuery.length > 0 
                  ? 'border-cyan-400/80 dark:border-cyan-500/80 scale-[1.01] shadow-cyan-500/30' 
                  : 'border-white/30 dark:border-gray-500/30 hover:border-cyan-300/50'"
              >
                <div class="relative flex items-center px-6 py-3">
                  <!-- Icône de recherche -->
                  <div class="mr-3">
                    <svg class="w-5 h-5 text-cyan-300 drop-shadow-md" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>

                  <!-- Champ de recherche -->
                  <input
                    ref="searchInput"
                    v-model="searchQuery"
                    @input="handleTyping"
                    @keyup.enter="handleSearch"
                    @focus="onFocus"
                    @blur="onBlur"
                    type="text"
                    placeholder="RECHERCHE"
                    class="flex-1 bg-transparent border-0 focus:ring-0 focus:outline-none text-white placeholder-white/70 text-base font-light tracking-wider h-8"
                    autocomplete="off"
                  />

                  <!-- Bouton effacer -->
                  <button 
                    v-if="searchQuery.length > 0"
                    @click="clearSearch"
                    class="mr-2 w-6 h-6 rounded-full bg-white/20 backdrop-blur text-white hover:bg-white/30 transition-all flex items-center justify-center"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>

                  <!-- Bouton de recherche -->
                  <button 
                    @click="handleSearch"
                    class="ml-2 w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 text-white flex items-center justify-center hover:shadow-lg hover:scale-105 transition-all duration-300 shadow-md"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </button>
                </div>

                <!-- Ligne de lumière au focus -->
                <div 
                  v-if="isFocused || searchQuery.length > 0"
                  class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-2/3 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent blur-sm"
                ></div>
              </div>

              <!-- DESSIN AU COIN -->
              <div class="absolute -bottom-3 -right-3 w-16 h-16 pointer-events-none">
                <div class="absolute inset-0 bg-gradient-to-tl from-cyan-400/60 to-transparent rounded-full blur-xl animate-pulse-slow"></div>
                <div class="absolute bottom-0 right-0 w-4 h-4 bg-cyan-300 rounded-full blur-sm"></div>
              </div>

              <!-- Suggestions -->
              <transition
                enter-active-class="transition duration-300 ease-out"
                enter-from-class="transform -translate-y-3 opacity-0"
                enter-to-class="transform translate-y-0 opacity-100"
                leave-active-class="transition duration-200 ease-in"
                leave-from-class="transform translate-y-0 opacity-100"
                leave-to-class="transform -translate-y-3 opacity-0"
              >
                <div 
                  v-if="showSuggestions && searchQuery.length > 0"
                  class="absolute top-full left-0 right-0 mt-3 bg-black/40 dark:bg-[#202124]/60 backdrop-blur-2xl rounded-2xl border border-white/20 shadow-2xl overflow-hidden z-40"
                >
                  <div class="max-h-56 overflow-y-auto custom-scrollbar">
                    <div v-if="autocompleteSuggestions.length > 0">
                      <div class="px-4 py-2 text-xs font-medium text-cyan-300 border-b border-white/10 bg-black/30">
                        Suggestions futuristes
                      </div>
                      <div 
                        v-for="suggestion in autocompleteSuggestions"
                        :key="suggestion"
                        @click="selectSuggestion(suggestion)"
                        class="px-4 py-2 hover:bg-cyan-500/20 cursor-pointer transition-colors flex items-center group/suggestion border-b border-white/5 last:border-0"
                      >
                        <svg class="w-4 h-4 mr-2 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <span class="text-sm text-white group-hover/suggestion:text-cyan-300">{{ suggestion }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>

          <!-- Right Side Controls -->
          <div class="flex items-center space-x-3">
            <div class="relative">
              <button
                @click="toggleUserMenu"
                ref="userMenuButton"
                class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
              >
                <div v-if="userPhoto" class="w-full h-full">
                  <img :src="userPhoto" alt="Photo de profil" class="w-full h-full object-cover rounded-full" />
                </div>
                <div v-else class="w-full h-full flex items-center justify-center">
                  {{ userInitial }}
                </div>
                <div v-if="hasNotifications" class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-white dark:border-[#202124] animate-pulse"></div>
              </button>

              <!-- Menu dropdown -->
              <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0"
              >
                <div 
                  v-if="isUserMenuOpen"
                  ref="userMenuDropdown"
                  class="absolute right-0 mt-3 w-72 bg-white/90 dark:bg-[#303134]/90 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
                >
                  <!-- Contenu du menu -->
                  <div class="p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-[#202124] dark:to-[#303134] border-b border-gray-200 dark:border-gray-700">
                    <div class="flex items-center space-x-3">
                      <div class="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl">
                        {{ userInitial }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="font-semibold text-gray-900 dark:text-white truncate">{{ displayName || 'Utilisateur' }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ userEmail || 'email@exemple.com' }}</p>
                      </div>
                    </div>
                  </div>
                  <div class="py-2">
                    <button v-if="isLoggedIn" @click="navigateToAccount" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
                      <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                        <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                      </div>
                      <div class="flex-1 text-left">
                        <p class="font-medium text-gray-900 dark:text-white">Gérer le compte</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Paramètres et préférences</p>
                      </div>
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                    </button>
                    <button v-if="isLoggedIn" @click="navigateToHistory" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
                      <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                        <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                      </div>
                      <div class="flex-1 text-left">
                        <p class="font-medium text-gray-900 dark:text-white">Historique</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Recherches récentes</p>
                      </div>
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                    </button>
                    <button v-if="user?.role === 'admin'" @click="navigateToAdmin" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
                      <div class="w-10 h-10 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
                        <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                      </div>
                      <div class="flex-1 text-left">
                        <p class="font-medium text-gray-900 dark:text-white">Administration</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Gestion du système</p>
                      </div>
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                    </button>
                    <button @click="toggleDarkMode" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
                      <div class="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                        <svg v-if="themeStore.isDarkMode" class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                        <svg v-else class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
                      </div>
                      <div class="flex-1 text-left">
                        <p class="font-medium text-gray-900 dark:text-white">Mode {{ themeStore.isDarkMode ? 'clair' : 'sombre' }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Apparence de l'interface</p>
                      </div>
                      <div class="relative w-12 h-6">
                        <div class="w-12 h-6 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                        <div :class="themeStore.isDarkMode ? 'translate-x-6' : 'translate-x-1'" class="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform duration-300"></div>
                      </div>
                    </button>
                    <div class="px-6 py-2"><div class="border-t border-gray-200 dark:border-gray-700"></div></div>
                    <template v-if="!isLoggedIn">
                      <button @click="navigateToSignUp" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
                        <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                          <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
                        </div>
                        <div class="flex-1 text-left"><p class="font-medium text-gray-900 dark:text-white">S'inscrire</p><p class="text-sm text-gray-500 dark:text-gray-400">Créer un nouveau compte</p></div>
                      </button>
                      <button @click="navigateToLogin" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
                        <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" /></svg>
                        </div>
                        <div class="flex-1 text-left"><p class="font-medium text-gray-900 dark:text-white">Se connecter</p><p class="text-sm text-gray-500 dark:text-gray-400">Accéder à votre compte</p></div>
                      </button>
                    </template>
                    <template v-else>
                      <button @click="handleLogout" class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors group">
                        <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" /></svg>
                        </div>
                        <div class="flex-1 text-left"><p class="font-medium text-gray-900 dark:text-white">Se déconnecter</p><p class="text-sm text-gray-500 dark:text-gray-400">Fermer la session</p></div>
                      </button>
                    </template>
                  </div>
                  <div class="px-6 py-4 bg-gray-50 dark:bg-[#202124] border-t border-gray-200 dark:border-gray-700">
                    <p class="text-xs text-gray-500 dark:text-gray-400 text-center">Version 1.0.0 • © 2024 Search.dev</p>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>

        <!-- Navigation Links -->
        <div class="flex items-center justify-center space-x-8 mt-4">
          <NuxtLink to="/search" class="text-gray-700 dark:text-[#e8eaed] hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-lg text-sm font-medium transition-colors" :class="{ 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400': $route.path === '/search' || $route.path === '/' }">Tous</NuxtLink>
          <NuxtLink to="/images" class="text-gray-700 dark:text-[#e8eaed] hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-lg text-sm font-medium transition-colors" :class="{ 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400': $route.path === '/images' }">Images</NuxtLink>
          <NuxtLink to="/videos" class="text-gray-700 dark:text-[#e8eaed] hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-lg text-sm font-medium transition-colors" :class="{ 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400': $route.path === '/videos' }">Vidéos</NuxtLink>
          <NuxtLink to="/docs" class="text-gray-700 dark:text-[#e8eaed] hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-lg text-sm font-medium transition-colors" :class="{ 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400': $route.path === '/docs' }">Documents</NuxtLink>
          <NuxtLink to="/advanced-search" class="text-gray-700 dark:text-[#e8eaed] hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-lg text-sm font-medium transition-colors" :class="{ 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400': $route.path === '/advanced-search' }">Recherche avancée</NuxtLink>
          <NuxtLink v-if="user?.role === 'admin'" to="/admin" class="text-gray-700 dark:text-[#e8eaed] hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-lg text-sm font-medium transition-colors" :class="{ 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400': $route.path.startsWith('/admin') }">Administration</NuxtLink>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>

    <!-- Footer  -->
    <footer class="bg-white dark:bg-[#202124] border-t border-gray-200 dark:border-gray-700 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div class="space-y-4">
            <div class="flex items-center space-x-2">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 p-0.5"><div class="w-full h-full bg-white dark:bg-[#202124] rounded-full flex items-center justify-center"><span class="text-sm">🔍</span></div></div>
              <div><span class="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Search.dev</span><p class="text-xs text-gray-500 dark:text-gray-400">Recherche intelligente</p></div>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Moteur de recherche spécialisé en informatique avec architecture microservices. Indexation en temps réel de contenus techniques et scientifiques.</p>
          </div>
          <div><h4 class="font-semibold text-gray-900 dark:text-white mb-4 text-lg">À propos</h4><ul class="space-y-3"><li><NuxtLink to="/about" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>Notre mission</NuxtLink></li><li><NuxtLink to="/team" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>L'équipe</NuxtLink></li><li><NuxtLink to="/blog" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>Blog</NuxtLink></li></ul></div>
          <div><h4 class="font-semibold text-gray-900 dark:text-white mb-4 text-lg">Aide</h4><ul class="space-y-3"><li><NuxtLink to="/help" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>Centre d'aide</NuxtLink></li><li><NuxtLink to="/faq" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>FAQ</NuxtLink></li><li><NuxtLink to="/contact" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>Contact</NuxtLink></li></ul></div>
          <div><h4 class="font-semibold text-gray-900 dark:text-white mb-4 text-lg">Développeurs</h4><ul class="space-y-3"><li><NuxtLink to="/api" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" /></svg>API</NuxtLink></li><li><NuxtLink to="/docs/api" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>Documentation</NuxtLink></li><li><a href="https://github.com" target="_blank" class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>GitHub</a></li></ul></div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="text-gray-500 dark:text-gray-400 text-sm"><p>&copy; 2024 Search.dev. Tous droits réservés.</p><p class="mt-1">Respect de votre vie privée • Pas de tracking publicitaire</p></div>
            <div class="flex items-center space-x-6 text-sm"><NuxtLink to="/privacy" class="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Confidentialité</NuxtLink><NuxtLink to="/terms" class="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Conditions</NuxtLink><NuxtLink to="/cookies" class="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Cookies</NuxtLink></div>
          </div>
          <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700"><div class="flex flex-wrap items-center justify-center gap-6 text-xs text-gray-500 dark:text-gray-400"><div class="flex items-center space-x-2"><div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div><span>Système opérationnel</span></div><div class="flex items-center space-x-2"><div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse delay-150"></div><span>Index temps réel</span></div><div class="flex items-center space-x-2"><div class="w-2 h-2 rounded-full bg-purple-500 animate-pulse delay-300"></div><span>9 microservices</span></div><div class="flex items-center space-x-2"><div class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse delay-500"></div><span>&lt;100ms de réponse</span></div></div></div>
        </div>
      </div>
    </footer>
    <NotificationsContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from '#app'
import { useThemeStore } from '../../stores/theme.store'
import { useAuthStore } from '../../stores/auth.store'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const searchInput = ref<HTMLInputElement | null>(null)
const userMenuButton = ref<HTMLElement | null>(null)
const userMenuDropdown = ref<HTMLElement | null>(null)

const searchQuery = ref('')
const isFocused = ref(false)
const showSuggestions = ref(false)
let typingTimer: NodeJS.Timeout | null = null
let suggestionsTimer: NodeJS.Timeout | null = null

const isUserMenuOpen = ref(false)
const hasNotifications = ref(true)

const autocompleteData = [
  'Python programmation', 'Python Django framework', 'Python Flask tutoriel',
  'JavaScript ES6', 'JavaScript React hooks', 'JavaScript Vue 3 composition API',
  'TypeScript interface', 'Docker containerisation', 'Kubernetes orchestration',
  'AWS cloud computing', 'Machine learning algorithmes', 'AI deep learning',
  'Base de données SQL', 'NoSQL MongoDB', 'GraphQL API', 'REST API design',
  'DevOps CI/CD', 'Git version control', 'Linux administration', 'Cybersecurity basics',
  'Web development', 'Mobile app development', 'Data science Python', 'Big data Hadoop',
  'Cloud architecture', 'Microservices design', 'Agile methodology', 'Scrum framework',
  'Base de donnée', 'Modele de machine learning', 'Java', 'C++', 'Programmation réseaux',
  'Architecture micro service', 'Framwork'
]

const isLoggedIn = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const displayName = computed(() => authStore.displayName)
const userEmail = computed(() => authStore.userEmail)
const userInitial = computed(() => authStore.userInitial)
const userPhoto = computed(() => authStore.userPhoto)

const autocompleteSuggestions = computed(() => {
  if (!searchQuery.value.trim()) return []
  const query = searchQuery.value.toLowerCase()
  return autocompleteData.filter(s => s.toLowerCase().includes(query)).slice(0, 5)
})

const handleClickOutside = (event: MouseEvent) => {
  if (isUserMenuOpen.value && userMenuButton.value && !userMenuButton.value.contains(event.target as Node) && userMenuDropdown.value && !userMenuDropdown.value.contains(event.target as Node)) {
    isUserMenuOpen.value = false
  }
  if (showSuggestions.value && searchInput.value && !searchInput.value.contains(event.target as Node)) {
    setTimeout(() => { showSuggestions.value = false }, 100)
  }
}

const toggleUserMenu = () => { isUserMenuOpen.value = !isUserMenuOpen.value }
const toggleDarkMode = () => { themeStore.toggleTheme() }
const navigateToAccount = () => { isUserMenuOpen.value = false; router.push('/account') }
const navigateToSignUp = () => { isUserMenuOpen.value = false; router.push('/register') }
const navigateToLogin = () => { isUserMenuOpen.value = false; router.push('/login') }
const navigateToHistory = () => { isUserMenuOpen.value = false; router.push('/history') }
const navigateToAdmin = () => { isUserMenuOpen.value = false; router.push('/admin') }
const handleLogout = async () => { await authStore.logout(); isUserMenuOpen.value = false; router.push('/') }

const onFocus = () => { isFocused.value = true; showSuggestions.value = true }
const onBlur = () => { setTimeout(() => { isFocused.value = false }, 100) }
const handleTyping = () => {
  if (typingTimer) clearTimeout(typingTimer)
  if (suggestionsTimer) clearTimeout(suggestionsTimer)
  suggestionsTimer = setTimeout(() => { showSuggestions.value = searchQuery.value.length > 0 }, 300)
  typingTimer = setTimeout(() => {}, 500)
}
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    showSuggestions.value = false
    let targetRoute = '/search'
    if (route.path.startsWith('/images')) targetRoute = '/images'
    else if (route.path.startsWith('/videos')) targetRoute = '/videos'
    else if (route.path.startsWith('/docs')) targetRoute = '/docs'
    router.push({ path: targetRoute, query: { q: searchQuery.value } })
  }
}
const selectSuggestion = (suggestion: string) => { searchQuery.value = suggestion; handleSearch() }
const clearSearch = () => { searchQuery.value = ''; searchInput.value?.focus() }

onMounted(() => {
  themeStore.initializeTheme()
  authStore.loadFromStorage()
  if (route.query.q) searchQuery.value = route.query.q as string
  setTimeout(() => searchInput.value?.focus(), 100)
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { showSuggestions.value = false; isUserMenuOpen.value = false } })
})
onUnmounted(() => { document.removeEventListener('click', handleClickOutside) })
</script>

<style scoped>
@keyframes ping { 75%, 100% { transform: scale(1.5); opacity: 0; } }
.animate-pulse { animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite; }
.animate-pulse-slow { animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.4; transform: scale(1); } 50% { opacity: 0.8; transform: scale(1.1); } }
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.03); border-radius: 8px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: linear-gradient(to bottom, #3b82f6, #8b5cf6); border-radius: 8px; }
.dark .custom-scrollbar::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.03); }
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: linear-gradient(to bottom, #60a5fa, #a78bfa); }
</style>

