<template>
  <div class="relative min-h-screen flex items-center justify-center py-12 px-4">
    <!-- Image de fond futuriste -->
    <div class="fixed inset-0 z-0">
      <img 
        src="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=2034&auto=format&fit=crop" 
        alt="Information Technology Background"
        class="w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-gradient-to-br from-black/60 via-black/40 to-black/60"></div>
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(0,255,255,0.2)_1px,_transparent_1px)] bg-[length:32px_32px]"></div>
    </div>

    <div class="relative z-10 max-w-md w-full space-y-8">
      <div class="backdrop-blur-2xl bg-white/10 dark:bg-black/30 rounded-3xl shadow-2xl border border-white/30 dark:border-cyan-500/30 overflow-hidden transition-all duration-300 hover:shadow-cyan-500/20 hover:border-cyan-400/50">
        
        <!-- En-tête -->
        <div class="px-8 pt-8 pb-6 bg-gradient-to-r from-cyan-500/10 to-purple-600/10 dark:from-cyan-900/30 dark:to-purple-900/30">
          <div class="flex flex-col items-center">
            <div class="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 p-1.5 mb-5 shadow-lg shadow-cyan-500/30 animate-pulse-glow">
              <div class="w-full h-full bg-white/10 dark:bg-gray-900/40 rounded-full flex items-center justify-center backdrop-blur-sm">
                <svg class="w-12 h-12 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
            </div>
            <h2 class="text-4xl font-bold tracking-tight text-center">
              <span class="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">Search.dev</span>
            </h2>
            <p class="mt-2 text-center text-white/80 font-light">
              Créez votre compte en quelques secondes
            </p>
          </div>
        </div>

        <!-- Formulaire -->
        <form class="px-8 py-6 space-y-6" @submit.prevent="handleRegister">

          <!-- ===== BANDEAU D'ERREUR GLOBAL ===== -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-2 scale-95"
            enter-to-class="opacity-100 translate-y-0 scale-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0 scale-100"
            leave-to-class="opacity-0 -translate-y-2 scale-95"
          >
            <div
              v-if="errorMessage"
              class="flex items-start gap-3 px-4 py-3.5 rounded-xl border border-red-400/40 bg-red-500/15 backdrop-blur-sm"
              :class="{ 'animate-shake': shakeError }"
            >
              <div class="flex-shrink-0 mt-0.5">
                <div class="w-6 h-6 rounded-full bg-red-500/30 flex items-center justify-center">
                  <svg class="w-3.5 h-3.5 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-red-200 leading-tight">{{ errorTitle }}</p>
                <p class="text-xs text-red-300/80 mt-0.5 leading-relaxed">{{ errorMessage }}</p>
              </div>
              <button
                type="button"
                @click="clearError"
                class="flex-shrink-0 text-red-300/60 hover:text-red-200 transition-colors mt-0.5"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </Transition>

          <!-- ===== BANDEAU DE SUCCÈS ===== -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-2 scale-95"
            enter-to-class="opacity-100 translate-y-0 scale-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0 scale-100"
            leave-to-class="opacity-0 -translate-y-2 scale-95"
          >
            <div
              v-if="successMessage"
              class="flex items-start gap-3 px-4 py-3.5 rounded-xl border border-green-400/40 bg-green-500/15 backdrop-blur-sm"
            >
              <div class="flex-shrink-0 mt-0.5">
                <div class="w-6 h-6 rounded-full bg-green-500/30 flex items-center justify-center">
                  <svg class="w-3.5 h-3.5 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-green-200 leading-tight">Compte créé avec succès !</p>
                <p class="text-xs text-green-300/80 mt-0.5 leading-relaxed">{{ successMessage }}</p>
              </div>
            </div>
          </Transition>

          <div class="space-y-5">

            <!-- Nom complet -->
            <div>
              <label for="name" class="block text-sm font-medium text-white/80 mb-2 tracking-wide">
                Nom complet <span class="text-cyan-300">*</span>
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-cyan-300 group-focus-within:text-cyan-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  id="name"
                  v-model="form.name"
                  type="text"
                  required
                  :class="[
                    'pl-10 w-full px-4 py-3 bg-white/10 dark:bg-black/30 backdrop-blur-sm border rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200',
                    fieldError.name
                      ? 'border-red-400/60 focus:ring-red-400'
                      : 'border-white/30 focus:ring-cyan-400'
                  ]"
                  placeholder="John Doe"
                  :disabled="loading"
                  @input="clearFieldError('name')"
                />
                <div class="absolute inset-0 rounded-xl pointer-events-none group-focus-within:shadow-[0_0_12px_#06b6d4] transition-shadow duration-300"></div>
              </div>
              <p v-if="fieldError.name" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ fieldError.name }}
              </p>
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-white/80 mb-2 tracking-wide">
                Adresse email <span class="text-cyan-300">*</span>
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-cyan-300 group-focus-within:text-cyan-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  required
                  :class="[
                    'pl-10 w-full px-4 py-3 bg-white/10 dark:bg-black/30 backdrop-blur-sm border rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200',
                    fieldError.email
                      ? 'border-red-400/60 focus:ring-red-400'
                      : 'border-white/30 focus:ring-cyan-400'
                  ]"
                  placeholder="email@exemple.com"
                  :disabled="loading"
                  @input="clearFieldError('email')"
                />
                <div class="absolute inset-0 rounded-xl pointer-events-none group-focus-within:shadow-[0_0_12px_#06b6d4] transition-shadow duration-300"></div>
              </div>
              <p v-if="fieldError.email" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ fieldError.email }}
              </p>
            </div>

            <!-- Mot de passe -->
            <div>
              <label for="password" class="block text-sm font-medium text-white/80 mb-2 tracking-wide">
                Mot de passe <span class="text-cyan-300">*</span>
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-cyan-300 group-focus-within:text-cyan-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  minlength="6"
                  :class="[
                    'pl-10 pr-10 w-full px-4 py-3 bg-white/10 dark:bg-black/30 backdrop-blur-sm border rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200',
                    fieldError.password
                      ? 'border-red-400/60 focus:ring-red-400'
                      : 'border-white/30 focus:ring-cyan-400'
                  ]"
                  placeholder="••••••••"
                  :disabled="loading"
                  @input="clearFieldError('password')"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-white/60 hover:text-white transition-colors"
                >
                  <svg v-if="showPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.59 6.59m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <div class="absolute inset-0 rounded-xl pointer-events-none group-focus-within:shadow-[0_0_12px_#06b6d4] transition-shadow duration-300"></div>
              </div>
              <!-- Indicateur de force du mot de passe -->
              <div v-if="form.password" class="mt-2 space-y-1">
                <div class="flex gap-1">
                  <div
                    v-for="i in 4" :key="i"
                    :class="[
                      'h-1 flex-1 rounded-full transition-all duration-300',
                      i <= passwordStrength.score
                        ? passwordStrength.color
                        : 'bg-white/20'
                    ]"
                  ></div>
                </div>
                <p :class="['text-xs', passwordStrength.textColor]">
                  {{ passwordStrength.label }}
                </p>
              </div>
              <p v-if="fieldError.password" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ fieldError.password }}
              </p>
            </div>

            <!-- Confirmation mot de passe -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-white/80 mb-2 tracking-wide">
                Confirmer le mot de passe <span class="text-cyan-300">*</span>
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-cyan-300 group-focus-within:text-cyan-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <input
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  required
                  :class="[
                    'pl-10 pr-10 w-full px-4 py-3 bg-white/10 dark:bg-black/30 backdrop-blur-sm border rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200',
                    fieldError.confirmPassword
                      ? 'border-red-400/60 focus:ring-red-400'
                      : form.confirmPassword && passwordsMatch
                      ? 'border-green-400/60 focus:ring-green-400'
                      : 'border-white/30 focus:ring-cyan-400'
                  ]"
                  placeholder="••••••••"
                  :disabled="loading"
                  @input="clearFieldError('confirmPassword')"
                />
                <!-- Icône de validation en temps réel -->
                <div class="absolute inset-y-0 right-8 flex items-center pr-1 pointer-events-none">
                  <svg
                    v-if="form.confirmPassword && passwordsMatch"
                    class="w-4 h-4 text-green-400"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg
                    v-else-if="form.confirmPassword && !passwordsMatch"
                    class="w-4 h-4 text-red-400"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-white/60 hover:text-white transition-colors"
                >
                  <svg v-if="showConfirmPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.59 6.59m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <div class="absolute inset-0 rounded-xl pointer-events-none group-focus-within:shadow-[0_0_12px_#06b6d4] transition-shadow duration-300"></div>
              </div>
              <p v-if="fieldError.confirmPassword" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ fieldError.confirmPassword }}
              </p>
              <p v-else-if="form.confirmPassword && !passwordsMatch" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                Les mots de passe ne correspondent pas
              </p>
              <p v-else-if="form.confirmPassword && passwordsMatch" class="mt-1.5 text-xs text-green-400 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                </svg>
                Les mots de passe correspondent
              </p>
            </div>
          </div>

          <!-- Bouton d'inscription -->
          <div>
            <button
              type="submit"
              :disabled="loading || !passwordsMatch || !isFormValid"
              class="group relative w-full flex justify-center items-center py-3.5 px-4 border border-transparent text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transform hover:-translate-y-0.5"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Création du compte...
              </span>
              <span v-else class="flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                Créer mon compte
              </span>
            </button>
          </div>

          <!-- Lien vers connexion -->
          <div class="text-center">
            <p class="text-sm text-white/60">
              Déjà un compte ?
              <NuxtLink to="/login" class="font-medium text-cyan-300 hover:text-cyan-200 transition-colors">
                Se connecter
              </NuxtLink>
            </p>
          </div>
        </form>

        <!-- Pied de page -->
        <div class="px-8 py-4 bg-white/5 dark:bg-black/20 border-t border-white/10">
          <p class="text-xs text-white/50 text-center">
            En vous inscrivant, vous acceptez nos
            <a href="#" class="text-cyan-300 hover:underline">Conditions d'utilisation</a>
            et notre
            <a href="#" class="text-cyan-300 hover:underline">Politique de confidentialité</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from '#app'
import { useAuthStore } from '../../stores/auth.store'
import { useNotifications } from '../../composables/useNotifications'

const router = useRouter()
const authStore = useAuthStore()
const { error: notifyError } = useNotifications()

const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)

// ── Erreur globale ────────────────────────────────────────────────────────────
const errorMessage = ref('')
const errorTitle = ref('')
const shakeError = ref(false)
const successMessage = ref('')

// ── Erreurs par champ ─────────────────────────────────────────────────────────
const fieldError = ref<{
  name: string
  email: string
  password: string
  confirmPassword: string
}>({ name: '', email: '', password: '', confirmPassword: '' })

// ── Computed ──────────────────────────────────────────────────────────────────
const passwordsMatch = computed(() =>
  form.value.password === form.value.confirmPassword
)

const isFormValid = computed(() =>
  form.value.name.trim() !== '' &&
  form.value.email.trim() !== '' &&
  form.value.password.length >= 6 &&
  form.value.confirmPassword !== ''
)

// Indicateur de force du mot de passe
const passwordStrength = computed(() => {
  const p = form.value.password
  if (!p) return { score: 0, color: '', textColor: '', label: '' }

  let score = 0
  if (p.length >= 8) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++

  const levels = [
    { score: 1, color: 'bg-red-500',    textColor: 'text-red-300',    label: 'Très faible — ajoutez des chiffres et majuscules' },
    { score: 2, color: 'bg-orange-400', textColor: 'text-orange-300', label: 'Faible — essayez d\'ajouter un caractère spécial' },
    { score: 3, color: 'bg-yellow-400', textColor: 'text-yellow-300', label: 'Moyen — encore un effort !' },
    { score: 4, color: 'bg-green-400',  textColor: 'text-green-300',  label: 'Fort — excellent mot de passe ✓' },
  ]

  return { score, ...levels[Math.min(score, 4) - 1] }
})

// ── Utilitaires ───────────────────────────────────────────────────────────────
const clearError = () => {
  errorMessage.value = ''
  errorTitle.value = ''
}

const clearFieldError = (field: keyof typeof fieldError.value) => {
  fieldError.value[field] = ''
  if (Object.values(fieldError.value).every(v => !v)) clearError()
}

const triggerShake = () => {
  shakeError.value = true
  setTimeout(() => { shakeError.value = false }, 400)
}

// ── Traducteur d'erreurs API ──────────────────────────────────────────────────
const parseError = (error: any, resultError?: string) => {
  const raw = (resultError || error?.message || error?.detail || '').toLowerCase()

  // Email déjà utilisé
  if (
    raw.includes('already exists') || raw.includes('already registered') ||
    raw.includes('email already') || raw.includes('duplicate') ||
    raw.includes('unique') || raw.includes('already taken')
  ) {
    errorTitle.value = 'Adresse email déjà utilisée'
    errorMessage.value = 'Un compte existe déjà avec cette adresse email. Connectez-vous ou utilisez une autre adresse.'
    fieldError.value.email = 'Cette adresse email est déjà associée à un compte'
    return
  }

  // Nom d'utilisateur invalide
  if (raw.includes('username') && (raw.includes('invalid') || raw.includes('too short'))) {
    errorTitle.value = 'Nom invalide'
    errorMessage.value = 'Le nom saisi contient des caractères non autorisés ou est trop court. Utilisez uniquement des lettres et espaces.'
    fieldError.value.name = 'Nom invalide ou trop court'
    return
  }

  // Mot de passe trop faible / non conforme
  if (
    raw.includes('password') && (
      raw.includes('too short') || raw.includes('too common') ||
      raw.includes('entirely numeric') || raw.includes('similar') ||
      raw.includes('weak') || raw.includes('strength')
    )
  ) {
    errorTitle.value = 'Mot de passe insuffisant'
    errorMessage.value = 'Votre mot de passe est trop simple. Utilisez au moins 8 caractères avec des majuscules, chiffres et symboles.'
    fieldError.value.password = 'Choisissez un mot de passe plus sécurisé'
    return
  }

  // Email invalide
  if (raw.includes('valid email') || raw.includes('email invalid') || raw.includes('invalid email')) {
    errorTitle.value = 'Email invalide'
    errorMessage.value = 'Le format de l\'adresse email n\'est pas valide. Vérifiez qu\'elle contient un "@" et un domaine (ex: nom@exemple.com).'
    fieldError.value.email = 'Format d\'email invalide'
    return
  }

  // Trop de tentatives / rate limit
  if (raw.includes('too many') || raw.includes('rate limit') || raw.includes('throttle')) {
    errorTitle.value = 'Trop de tentatives'
    errorMessage.value = 'Vous avez effectué trop d\'inscriptions en peu de temps. Veuillez patienter quelques minutes avant de réessayer.'
    return
  }

  // Problème serveur / réseau
  if (
    raw.includes('network') || raw.includes('fetch') ||
    raw.includes('500') || raw.includes('503') || raw.includes('timeout')
  ) {
    errorTitle.value = 'Problème de connexion'
    errorMessage.value = 'Le serveur est temporairement indisponible. Vérifiez votre connexion internet et réessayez dans quelques instants.'
    return
  }

  // Erreur générique
  errorTitle.value = 'Inscription impossible'
  errorMessage.value = 'Une erreur inattendue s\'est produite. Veuillez réessayer ou contacter le support si le problème persiste.'
}

// ── Handler principal ─────────────────────────────────────────────────────────
const handleRegister = async () => {
  clearError()
  successMessage.value = ''
  fieldError.value = { name: '', email: '', password: '', confirmPassword: '' }

  // Validation côté client
  if (form.value.name.trim().length < 2) {
    fieldError.value.name = 'Le nom doit contenir au moins 2 caractères'
    errorTitle.value = 'Champ invalide'
    errorMessage.value = 'Veuillez saisir votre nom complet.'
    triggerShake()
    return
  }

  if (!form.value.email.includes('@')) {
    fieldError.value.email = 'Veuillez saisir une adresse email valide'
    errorTitle.value = 'Email invalide'
    errorMessage.value = 'L\'adresse email saisie ne semble pas valide.'
    triggerShake()
    return
  }

  if (form.value.password.length < 6) {
    fieldError.value.password = 'Le mot de passe doit contenir au moins 6 caractères'
    errorTitle.value = 'Mot de passe trop court'
    errorMessage.value = 'Votre mot de passe doit comporter au minimum 6 caractères.'
    triggerShake()
    return
  }

  if (!passwordsMatch.value) {
    fieldError.value.confirmPassword = 'Les mots de passe ne correspondent pas'
    errorTitle.value = 'Confirmation incorrecte'
    errorMessage.value = 'Les deux mots de passe saisis ne sont pas identiques. Veuillez les vérifier.'
    triggerShake()
    return
  }

  loading.value = true

  try {
    const result = await authStore.register({
      name: form.value.name,
      email: form.value.email,
      password: form.value.password
    })

    if (result.success) {
      successMessage.value = 'Bienvenue ! Vous allez être redirigé vers votre espace...'
      setTimeout(() => router.push('/'), 1500)
    } else {
      parseError(null, result.error)
      notifyError(errorMessage.value)
      triggerShake()
    }
  } catch (error: any) {
    parseError(error)
    notifyError(errorMessage.value)
    triggerShake()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px #06b6d4, 0 0 12px #3b82f6; }
  50%       { box-shadow: 0 0 20px #06b6d4, 0 0 30px #3b82f6; }
}
.animate-pulse-glow { animation: pulse-glow 2s infinite; }

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%       { transform: translateX(-5px); }
  40%       { transform: translateX(5px); }
  60%       { transform: translateX(-3px); }
  80%       { transform: translateX(3px); }
}
.animate-shake { animation: shake 0.4s ease-in-out; }
</style>