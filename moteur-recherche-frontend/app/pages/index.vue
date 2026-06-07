<template>
  <div :class="[themeStore.isDarkMode ? 'dark' : '', 'min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 overflow-hidden']">
    <!-- Fond avec particules animées subtiles -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]">
        <div class="absolute inset-0" style="
          background-image: radial-gradient(circle at 25% 25%, #3b82f6 2px, transparent 0),
                            radial-gradient(circle at 75% 75%, #8b5cf6 1px, transparent 0);
          background-size: 60px 60px;
        "></div>
      </div>
    </div>
    <!-- Menu utilisateur en haut à droite -->
    <div class="fixed top-6 right-6 z-50">
      <div class="relative">
        <!-- Bouton avatar -->
        <button
          @click="toggleUserMenu"
          ref="userMenuButton"
          class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-300 relative overflow-hidden group"
        >
          <div v-if="userPhoto" class="w-full h-full">
            <img 
              :src="userPhoto" 
              alt="Photo de profil" 
              class="w-full h-full object-cover"
            />
          </div>
          <div v-else class="w-full h-full flex items-center justify-center">
            {{ userInitial }}
          </div>
          
          <div v-if="hasNotifications" class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-white dark:border-gray-900 animate-pulse"></div>
          
          <div class="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
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
            class="absolute right-0 mt-3 w-72 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden z-50"
          >
            <!-- En-tête du menu -->
            <div class="p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 border-b border-gray-200/50 dark:border-gray-700/50">
              <div class="flex items-center space-x-3">
                <div class="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
                  {{ userInitial }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-gray-900 dark:text-white truncate">{{ displayName || 'Utilisateur' }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ userEmail || 'email@exemple.com' }}</p>
                </div>
              </div>
            </div>

            <!-- Options du menu -->
            <div class="py-2">
              <!-- Gérer le compte (visible seulement si connecté) -->
              <button 
                v-if="isLoggedIn"
                @click="navigateTo('/account')"
                class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100/50 dark:hover:bg-gray-700/30 transition-colors duration-200 group"
              >
                <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div class="flex-1 text-left">
                  <p class="font-medium text-gray-900 dark:text-white">Gérer le compte</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Paramètres et préférences</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- Historique (visible seulement si connecté) -->
              <button 
                v-if="isLoggedIn"
                @click="navigateTo('/history')"
                class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100/50 dark:hover:bg-gray-700/30 transition-colors duration-200 group"
              >
                <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                  <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div class="flex-1 text-left">
                  <p class="font-medium text-gray-900 dark:text-white">Historique</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Recherches récentes</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- Administration (visible seulement pour les admins) -->
              <button 
                v-if="user?.role === 'admin'"
                @click="navigateTo('/admin')"
                class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100/50 dark:hover:bg-gray-700/30 transition-colors duration-200 group"
              >
                <div class="w-10 h-10 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                  <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div class="flex-1 text-left">
                  <p class="font-medium text-gray-900 dark:text-white">Administration</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Gérer le système de recherche</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-yellow-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- Mode sombre/clair -->
              <button 
                @click="toggleDarkMode"
                class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100/50 dark:hover:bg-gray-700/30 transition-colors duration-200 group"
              >
                <div class="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                  <svg v-if="themeStore.isDarkMode" class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  <svg v-else class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
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

              <!-- Séparateur -->
              <div class="px-6 py-2">
                <div class="border-t border-gray-200/50 dark:border-gray-700/50"></div>
              </div>

              <!-- S'inscrire/Se connecter ou Se déconnecter -->
              <template v-if="!isLoggedIn">
                <button 
                  @click="navigateTo('/register')"
                  class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100/50 dark:hover:bg-gray-700/30 transition-colors duration-200 group"
                >
                  <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                  </div>
                  <div class="flex-1 text-left">
                    <p class="font-medium text-gray-900 dark:text-white">S'inscrire</p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Créer un nouveau compte</p>
                  </div>
                </button>

                <button 
                  @click="navigateTo('/login')"
                  class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-gray-100/50 dark:hover:bg-gray-700/30 transition-colors duration-200 group"
                >
                  <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                  </div>
                  <div class="flex-1 text-left">
                    <p class="font-medium text-gray-900 dark:text-white">Se connecter</p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Accéder à votre compte</p>
                  </div>
                </button>
              </template>

              <template v-else>
                <button 
                  @click="handleLogout"
                  class="w-full px-6 py-4 flex items-center space-x-3 hover:bg-red-50/50 dark:hover:bg-red-900/20 transition-colors duration-200 group"
                >
                  <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                  </div>
                  <div class="flex-1 text-left">
                    <p class="font-medium text-gray-900 dark:text-white">Se déconnecter</p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Fermer la session</p>
                  </div>
                </button>
              </template>
            </div>

            <!-- Pied du menu -->
            <div class="px-6 py-4 bg-gray-50/50 dark:bg-gray-900/30 border-t border-gray-200/50 dark:border-gray-700/50">
              <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
                Version 1.0.0 • © 2026 Search.dev
              </p>
            </div>
          </div>
        </transition>
      </div>
    </div>


    <!-- Contenu principal centré -->
    <div class="relative min-h-screen flex flex-col items-center justify-center px-4 pt-12 pb-8">
      <!-- Logo élégant au-dessus de la barre de recherche -->
      <div class="mb-10 animate-fade-in-down">
        <!-- Logo avec effet 3D -->
        <div class="relative mb-6">
          <div class="w-32 h-32 mx-auto">
            <!-- Effet d'ombre portée -->
            <div class="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full blur-xl opacity-30 animate-pulse-slow"></div>
            
            <!-- Logo principal -->
            <div class="relative w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 via-blue-600 to-purple-600 p-2 shadow-2xl animate-float">
              <div class="w-full h-full bg-white/10 dark:bg-gray-900/20 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/20 dark:border-gray-700/30">
                <div class="w-24 h-24 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 p-2 shadow-inner">
                  <div class="w-full h-full bg-white/90 dark:bg-gray-900/90 rounded-full flex items-center justify-center shadow-lg">
                    <div class="relative">
                      <span class="text-4xl">🔍</span>
                      <!-- Effet de lueur interne -->
                      <div class="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-500/20 rounded-full blur-md"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Nom du site avec effet gradient animé -->
        <div class="text-center">
          <h1 class="text-5xl md:text-6xl font-bold mb-2">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-gradient bg-[length:200%_auto]">
              Search<span class="font-light">.dev</span>
            </span>
          </h1>
          
          <!-- Tagline élégante -->
          <div class="mt-4 flex items-center justify-center space-x-3">
            <div class="flex items-center space-x-1">
              <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
              <span class="text-xs text-gray-600 dark:text-gray-400">Index temps réel</span>
            </div>
            <div class="flex items-center space-x-1">
              <div class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse delay-150"></div>
              <span class="text-xs text-gray-600 dark:text-gray-400">Résultats intelligents</span>
            </div>
            <div class="flex items-center space-x-1">
              <div class="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse delay-300"></div>
              <span class="text-xs text-gray-600 dark:text-gray-400">Confidentialité</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Barre de recherche élégante au centre (très fine et arrondie) -->
      <div class="w-full max-w-2xl mb-10">
        <!-- Effet de lumière autour de la barre de recherche -->
        <div 
          class="absolute -inset-6 bg-gradient-to-r from-blue-400/0 via-blue-400/20 to-blue-400/0 dark:from-blue-500/0 dark:via-blue-500/15 dark:to-blue-500/0 rounded-full blur-2xl transition-all duration-1000"
          :class="{ 
            'opacity-100 scale-105': isFocused || searchQuery.length > 0,
            'opacity-0 scale-100': !isFocused && searchQuery.length === 0 
          }"
        ></div>
        
        <div class="relative">
          <!-- Barre de recherche avec effet glassmorphism (très fine et arrondie) -->
          <div 
            class="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl rounded-full border transition-all duration-500 shadow-lg overflow-hidden group"
            :class="isFocused || searchQuery.length > 0 
              ? 'border-blue-400 dark:border-blue-500 scale-[1.02] shadow-xl' 
              : 'border-transparent hover:border-blue-200 dark:hover:border-gray-700'"
          >
            <!-- Effet de brillance interne -->
            <div class="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            
            <!-- Conteneur de la barre de recherche (très fine) -->
            <div class="relative flex items-center px-4 py-2">
              <!-- Icône de recherche -->
              <div class="mr-2">
                <svg 
                  class="w-4 h-4 transition-all duration-300" 
                  :class="isFocused || searchQuery.length > 0 
                    ? 'text-blue-500 dark:text-blue-400 scale-110' 
                    : 'text-gray-400 dark:text-gray-500'"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              
              <!-- Champ de recherche (très fin) -->
              <input
                ref="searchInput"
                v-model="searchQuery"
                @input="handleTyping"
                @keyup.enter="handleSearch"
                @focus="onFocus"
                @blur="onBlur"
                type="text"
                placeholder="Rechercher des concepts techniques, tutoriels, documentation..."
                class="flex-1 bg-transparent border-0 focus:ring-0 focus:outline-none text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 text-sm font-light tracking-wide h-6"
                autocomplete="off"
              />
              
              <!-- Bouton de recherche avec effet hover (petit) -->
              <button 
                @click="handleSearch"
                class="ml-2 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center hover:shadow-lg hover:scale-110 transition-all duration-300 shadow-md relative overflow-hidden group/search-btn"
                :class="searchQuery.trim() 
                  ? 'opacity-100 from-blue-500 to-purple-600' 
                  : 'opacity-70 from-gray-400 to-gray-500 dark:from-gray-600 dark:to-gray-700'"
              >
                <!-- Effet de brillance sur le bouton -->
                <div class="absolute inset-0 bg-white/20 opacity-0 group-hover/search-btn:opacity-100 transition-opacity duration-300"></div>
                
                <svg class="w-3.5 h-3.5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
            
            <!-- Effet de lumière bas (seulement quand focus) -->
            <div 
              v-if="isFocused || searchQuery.length > 0"
              class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-3/4 h-0.5 bg-gradient-to-r from-transparent via-blue-400 to-transparent blur-sm"
            ></div>
          </div>

          <!-- Suggestions de recherche élégantes -->
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
              class="absolute top-full left-0 right-0 mt-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 overflow-hidden z-40"
            >
              <div class="max-h-48 overflow-y-auto custom-scrollbar">
                <!-- Suggestions d'autocomplétion -->
                <div v-if="autocompleteSuggestions.length > 0">
                  <div class="px-3 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 border-b border-gray-100/50 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-900/30">
                    Suggestions de recherche
                  </div>
                  <div 
                    v-for="suggestion in autocompleteSuggestions"
                    :key="suggestion"
                    @click="selectSuggestion(suggestion)"
                    class="px-3 py-2 hover:bg-blue-50/50 dark:hover:bg-gray-700/30 cursor-pointer transition-colors duration-200 flex items-center group/suggestion border-b border-gray-100/30 dark:border-gray-700/30 last:border-0"
                  >
                    <svg class="w-3.5 h-3.5 mr-2 text-gray-400 group-hover/suggestion:text-blue-500 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <div class="flex-1">
                      <span class="text-xs text-gray-700 dark:text-gray-300 group-hover/suggestion:text-blue-600 dark:group-hover/suggestion:text-blue-400 transition-colors duration-200">{{ suggestion }}</span>
                    </div>
                    <svg class="w-3 h-3 text-gray-300 dark:text-gray-600 group-hover/suggestion:text-blue-500 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Boutons des sites informatiques importants -->
      <div class="w-full max-w-5xl mb-8">
        <div class="text-center mb-4">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Ressources Informatiques
            </span>
          </h2>
          <p class="text-xs text-gray-600 dark:text-gray-400 max-w-xl mx-auto">
            Accédez rapidement aux meilleures ressources informatiques et à notre partenaire académique
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 px-2">
          <!-- GitHub -->
          <a 
            href="https://github.com" 
            target="_blank"
            class="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl p-3 border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-300 dark:hover:border-blue-700 hover:shadow-lg hover:scale-105 transition-all duration-300 transform cursor-pointer"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                GitHub
              </h3>
              <p class="text-xs text-gray-600 dark:text-gray-400 leading-tight">
                Développement collaboratif
              </p>
            </div>
          </a>

          <!-- Stack Overflow -->
          <a 
            href="https://stackoverflow.com" 
            target="_blank"
            class="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl p-3 border border-gray-200/50 dark:border-gray-700/50 hover:border-orange-300 dark:hover:border-orange-700 hover:shadow-lg hover:scale-105 transition-all duration-300 transform cursor-pointer"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.986 21.865v-6.404h2.134V24H1.844v-8.539h2.13v6.404h15.012zM6.111 19.731H16.85v-2.137H6.111v2.137zm.259-4.852l10.48 2.189.451-2.07-10.478-2.187-.453 2.068zm1.359-5.056l9.705 4.53.903-1.95-9.706-4.53-.902 1.95zm2.715-4.785l8.217 6.855 1.359-1.62-8.216-6.853-1.36 1.618zM15.751 0l-1.746 1.294 6.405 8.604 1.746-1.294L15.751 0z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                Stack Overflow
              </h3>
              <p class="text-xs text-gray-600 dark:text-gray-400 leading-tight">
                Questions & réponses techniques
              </p>
            </div>
          </a>

          <!-- MDN Web Docs -->
          <a 
            href="https://developer.mozilla.org" 
            target="_blank"
            class="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl p-3 border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-300 dark:hover:border-blue-700 hover:shadow-lg hover:scale-105 transition-all duration-300 transform cursor-pointer"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M0 0v24h24V0H0zm21.6 21.6H2.4V2.4h19.2v19.2zM8.4 16.8l2.4-4.2-2.4-4.2h4.8l2.4 4.2-2.4 4.2H8.4z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                MDN Web Docs
              </h3>
              <p class="text-xs text-gray-600 dark:text-gray-400 leading-tight">
                Documentation web complète
              </p>
            </div>
          </a>

          <!-- W3Schools -->
          <a 
            href="https://www.w3schools.com" 
            target="_blank"
            class="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl p-3 border border-gray-200/50 dark:border-gray-700/50 hover:border-green-300 dark:hover:border-green-700 hover:shadow-lg hover:scale-105 transition-all duration-300 transform cursor-pointer"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M0 0v24h24V0H0zm21.6 21.6H2.4V2.4h19.2v19.2zM12 6l-6 6 6 6 6-6-6-6z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                W3Schools
              </h3>
              <p class="text-xs text-gray-600 dark:text-gray-400 leading-tight">
                Tutoriels développement web
              </p>
            </div>
          </a>

          <!-- CFI-CIRAS Université -->
          <a 
            href="https://cfi-ciras.cg" 
            target="_blank"
            class="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl p-3 border border-gray-200/50 dark:border-gray-700/50 hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-lg hover:scale-105 transition-all duration-300 transform cursor-pointer"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v6l9-5" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v6l-9-5" />
                </svg>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                CFI-CIRAS
              </h3>
              <p class="text-xs text-gray-600 dark:text-gray-400 leading-tight">
                Centre de Formation en informatique
              </p>
            </div>
          </a>
        </div>
      </div>

      <!-- Informations supplémentaires (visible en bas) -->
      <div class="absolute bottom-4 left-0 right-0">
        <div class="text-center">
          <div class="inline-flex items-center space-x-6 text-gray-400 dark:text-gray-500 text-xs">
            <!-- Statistiques -->
            <div class="flex items-center space-x-2">
              <div class="text-right">
                <div class="font-bold text-gray-700 dark:text-gray-300 text-sm">9</div>
                <div class="text-xs">Microservices</div>
              </div>
              <div class="w-6 h-px bg-gradient-to-r from-gray-300 to-transparent dark:from-gray-600"></div>
            </div>
            
            <div class="flex items-center space-x-2">
              <div class="text-right">
                <div class="font-bold text-gray-700 dark:text-gray-300 text-sm">12K+</div>
                <div class="text-xs">Documents indexés</div>
              </div>
              <div class="w-6 h-px bg-gradient-to-r from-gray-300 to-transparent dark:from-gray-600"></div>
            </div>
            
            <div class="flex items-center space-x-2">
              <div class="text-right">
                <div class="font-bold text-gray-700 dark:text-gray-300 text-sm">&lt;100ms</div>
                <div class="text-xs">Temps de réponse</div>
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
  layout: false,
});

import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from '#app'
import { useThemeStore } from '../../stores/theme.store'
import { useAuthStore } from '../../stores/auth.store'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

// Références DOM
const searchInput = ref<HTMLInputElement | null>(null)
const userMenuButton = ref<HTMLElement | null>(null)
const userMenuDropdown = ref<HTMLElement | null>(null)

// États de recherche
const searchQuery = ref('')
const isFocused = ref(false)
const showSuggestions = ref(false)
let typingTimer: NodeJS.Timeout | null = null
let suggestionsTimer: NodeJS.Timeout | null = null

// États du menu utilisateur
const isUserMenuOpen = ref(false)
const hasNotifications = ref(true)

// Utiliser les stores
const isLoggedIn = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const displayName = computed(() => authStore.displayName)
const userEmail = computed(() => authStore.userEmail)
const userInitial = computed(() => authStore.userInitial)
const userPhoto = computed(() => authStore.userPhoto)

// Données d'autocomplétion simulées
const autocompleteData = [
  'Python programmation avancée',
  'Python Django framework REST API',
  'Python Flask tutoriel pour débutants',
  'JavaScript ES6+ nouvelles fonctionnalités',
  'JavaScript React hooks avancés',
  'JavaScript Vue 3 composition API guide',
  'TypeScript interfaces et types',
  'Docker containerisation pour développeurs',
  'Kubernetes orchestration de conteneurs',
  'AWS cloud computing services',
  'Machine learning algorithmes implémentation',
  'AI deep learning modèles neuronaux',
  'Base de données SQL optimisation',
  'NoSQL MongoDB schéma design',
  'GraphQL API design patterns',
  'REST API best practices',
  'DevOps CI/CD pipelines',
  'Git version control avancé',
  'Linux administration système',
  'Cybersecurity basics pour développeurs',
  'Web development modern stack',
  'Mobile app development React Native',
  'Data science avec Python pandas',
  'Big data Hadoop ecosystem',
  'Cloud architecture design patterns',
  'Microservices design principles',
  'Agile methodology Scrum framework',
  'Architecture micro service patterns',
  'PHP Laravel framework moderne',
  'C++ programmation système'
]

// Suggestions filtrées
const autocompleteSuggestions = computed(() => {
  if (!searchQuery.value.trim()) return []
  
  const query = searchQuery.value.toLowerCase()
  return autocompleteData
    .filter(suggestion => suggestion.toLowerCase().includes(query))
    .slice(0, 4)
})

// Fonction de navigation générique
const navigateTo = (path: string) => {
  isUserMenuOpen.value = false
  router.push(path)
}

// Gestion du clic en dehors du menu
const handleClickOutside = (event: MouseEvent) => {
  if (isUserMenuOpen.value && 
      userMenuButton.value && 
      !userMenuButton.value.contains(event.target as Node) &&
      userMenuDropdown.value && 
      !userMenuDropdown.value.contains(event.target as Node)) {
    isUserMenuOpen.value = false
  }
  
  // Fermer les suggestions si on clique en dehors
  if (showSuggestions.value && 
      searchInput.value && 
      !searchInput.value.contains(event.target as Node) &&
      !document.querySelector('.custom-scrollbar')?.contains(event.target as Node)) {
    setTimeout(() => {
      showSuggestions.value = false
    }, 150)
  }
}

// Toggle du menu utilisateur
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

// Toggle du mode sombre
const toggleDarkMode = () => {
  themeStore.toggleTheme()
}

// Déconnexion
const handleLogout = async () => {
  try {
    await authStore.logout()
    isUserMenuOpen.value = false
    router.push('/')
  } catch (error) {
    console.error('Erreur lors de la déconnexion:', error)
  }
}

// Gestion de la recherche
const onFocus = () => {
  isFocused.value = true
  showSuggestions.value = true
}

const onBlur = () => {
  setTimeout(() => {
    isFocused.value = false
  }, 200)
}

const handleTyping = () => {
  if (typingTimer) clearTimeout(typingTimer)
  if (suggestionsTimer) clearTimeout(suggestionsTimer)
  
  // Afficher les suggestions après un délai
  suggestionsTimer = setTimeout(() => {
    showSuggestions.value = searchQuery.value.length > 0
  }, 200)
  
  typingTimer = setTimeout(() => {
    // Logique de recherche après arrêt de frappe (si nécessaire)
  }, 500)
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    showSuggestions.value = false
    router.push({
      path: '/search',
      query: { q: searchQuery.value }
    })
  }
}

const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  handleSearch()
}

// Empêcher le défilement avec la roulette de la souris
const preventScroll = (e: WheelEvent) => {
  e.preventDefault()
  e.stopPropagation()
  return false
}

// Initialisation
onMounted(() => {
  // Initialiser le thème
  themeStore.initializeTheme()
  
  // Charger l'utilisateur
  authStore.loadFromStorage()
  
  // Focus sur la barre de recherche
  setTimeout(() => {
    searchInput.value?.focus()
  }, 800)

  // Écouter les clics en dehors du menu
  document.addEventListener('click', handleClickOutside)

  // Écouter les touches du clavier
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      showSuggestions.value = false
      isUserMenuOpen.value = false
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault()
      searchInput.value?.focus()
    }
  })

  // Empêcher le défilement avec la roulette
  document.addEventListener('wheel', preventScroll, { passive: false })
})

onUnmounted(() => {
  // Nettoyer les écouteurs d'événements
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('wheel', preventScroll)
})
</script>

<style scoped>
/* Empêcher le défilement */
html, body {
  overflow: hidden;
  height: 100%;
}

/* Animations personnalisées */
@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-8px) rotate(0.5deg);
  }
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-gradient {
  animation: gradient 3s ease infinite;
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.delay-150 {
  animation-delay: 150ms;
}

.delay-300 {
  animation-delay: 300ms;
}

/* Scrollbar personnalisée */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
  border-radius: 8px;
}

.dark .custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.03);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #60a5fa, #a78bfa);
}

/* Effets de transition pour les inputs */
input {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Effet de brillance pour la barre de recherche focus */
.group:focus-within .search-glow {
  opacity: 1;
  transform: scale(1.02);
}

/* Amélioration des bordures gradients */
.border-gradient {
  border-image: linear-gradient(to right, #3b82f6, #8b5cf6) 1;
}

/* Empêcher la sélection de texte */
* {
  user-select: none;
}

/* Permettre la sélection seulement dans les inputs */
input {
  user-select: text;
}
</style>