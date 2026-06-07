<template>
  <div class="relative min-h-screen flex items-center justify-center py-12 px-4">
    <!-- Image de fond futuriste -->
    <div class="fixed inset-0 z-0">
      <img 
        src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop" 
        alt="Background"
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </div>
            <h2 class="text-4xl font-bold tracking-tight text-center">
              <span class="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">Search.dev</span>
            </h2>
            <p class="mt-2 text-center text-white/80 font-light">
              Connectez-vous à votre espace
            </p>
          </div>
        </div>

        <!-- Formulaire -->
        <form class="px-8 py-6 space-y-6" @submit.prevent="handleLogin">

          <!-- ===== BLOC MESSAGE D'ERREUR ===== -->
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
              <!-- Icône -->
              <div class="flex-shrink-0 mt-0.5">
                <div class="w-6 h-6 rounded-full bg-red-500/30 flex items-center justify-center">
                  <svg class="w-3.5 h-3.5 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                </div>
              </div>
              <!-- Texte -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-red-200 leading-tight">{{ errorTitle }}</p>
                <p class="text-xs text-red-300/80 mt-0.5 leading-relaxed">{{ errorMessage }}</p>
              </div>
              <!-- Fermer -->
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

          <div class="space-y-5">
            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-white/80 mb-2 tracking-wide">
                Adresse email
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
              <!-- Erreur champ email -->
              <p v-if="fieldError.email" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ fieldError.email }}
              </p>
            </div>

            <!-- Mot de passe -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label for="password" class="block text-sm font-medium text-white/80 tracking-wide">
                  Mot de passe
                </label>
                <NuxtLink to="/reset-password" class="text-sm text-cyan-300 hover:text-cyan-200 transition-colors">
                  Mot de passe oublié ?
                </NuxtLink>
              </div>
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
              <!-- Erreur champ password -->
              <p v-if="fieldError.password" class="mt-1.5 text-xs text-red-300 flex items-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                {{ fieldError.password }}
              </p>
            </div>

            <!-- Remember me -->
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="form.rememberMe"
                type="checkbox"
                class="h-4 w-4 rounded border-white/30 bg-white/10 text-cyan-500 focus:ring-cyan-400 focus:ring-2 focus:ring-offset-0"
              />
              <label for="remember-me" class="ml-2 block text-sm text-white/70">
                Se souvenir de moi
              </label>
            </div>
          </div>

          <!-- Bouton de connexion -->
          <div>
            <button
              type="submit"
              :disabled="loading || !isFormValid"
              class="group relative w-full flex justify-center items-center py-3.5 px-4 border border-transparent text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transform hover:-translate-y-0.5"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Connexion en cours...
              </span>
              <span v-else class="flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                Se connecter
              </span>
            </button>
          </div>

          <!-- Lien vers inscription -->
          <div class="text-center">
            <p class="text-sm text-white/60">
              Pas encore de compte ?
              <NuxtLink to="/register" class="font-medium text-cyan-300 hover:text-cyan-200 transition-colors">
                S'inscrire
              </NuxtLink>
            </p>
          </div>
        </form>

        <!-- Pied de page -->
        <div class="px-8 py-4 bg-white/5 dark:bg-black/20 border-t border-white/10">
          <p class="text-xs text-white/50 text-center">
            En vous connectant, vous acceptez nos
            <a href="#" class="text-cyan-300 hover:underline">Conditions d'utilisation</a>
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
  email: '',
  password: '',
  rememberMe: false
})

const showPassword = ref(false)
const loading = ref(false)

// ── Erreur globale (bandeau) ──────────────────────────────────────────────────
const errorMessage = ref('')
const errorTitle = ref('')
const shakeError = ref(false)

// ── Erreurs par champ (bordure rouge + message sous le champ) ─────────────────
const fieldError = ref<{ email: string; password: string }>({
  email: '',
  password: ''
})

const isFormValid = computed(() =>
  form.value.email.trim() !== '' && form.value.password.trim() !== ''
)

// ── Utilitaires ───────────────────────────────────────────────────────────────
const clearError = () => {
  errorMessage.value = ''
  errorTitle.value = ''
}

const clearFieldError = (field: 'email' | 'password') => {
  fieldError.value[field] = ''
  // Si plus d'erreur de champ, on efface aussi le bandeau global
  if (!fieldError.value.email && !fieldError.value.password) {
    clearError()
  }
}

const triggerShake = () => {
  shakeError.value = true
  setTimeout(() => { shakeError.value = false }, 400)
}

// ── Traduction des erreurs API en messages lisibles ───────────────────────────
const parseError = (error: any, resultError?: string) => {
  const raw = (resultError || error?.message || error?.detail || '').toLowerCase()

  // Identifiants incorrects
  if (
    raw.includes('invalid') || raw.includes('incorrect') ||
    raw.includes('no active account') || raw.includes('wrong') ||
    raw.includes('bad credentials') || raw.includes('unauthorized')
  ) {
    errorTitle.value = 'Identifiants incorrects'
    errorMessage.value = 'L\'adresse email ou le mot de passe que vous avez saisi est incorrect. Veuillez réessayer.'
    fieldError.value.email = 'Vérifiez votre adresse email'
    fieldError.value.password = 'Vérifiez votre mot de passe'
    return
  }

  // Compte inexistant
  if (raw.includes('not found') || raw.includes('does not exist') || raw.includes('user not found')) {
    errorTitle.value = 'Compte introuvable'
    errorMessage.value = 'Aucun compte n\'est associé à cette adresse email. Vérifiez l\'adresse ou créez un nouveau compte.'
    fieldError.value.email = 'Aucun compte trouvé avec cet email'
    return
  }

  // Compte désactivé / bloqué
  if (
    raw.includes('disabled') || raw.includes('blocked') ||
    raw.includes('suspended') || raw.includes('banned') || raw.includes('inactive')
  ) {
    errorTitle.value = 'Compte désactivé'
    errorMessage.value = 'Votre compte a été désactivé. Contactez l\'administrateur pour plus d\'informations.'
    return
  }

  // Trop de tentatives
  if (raw.includes('too many') || raw.includes('rate limit') || raw.includes('throttle') || raw.includes('locked')) {
    errorTitle.value = 'Trop de tentatives'
    errorMessage.value = 'Vous avez effectué trop de tentatives de connexion. Veuillez patienter quelques minutes avant de réessayer.'
    return
  }

  // Email non vérifié
  if (raw.includes('verify') || raw.includes('confirmed') || raw.includes('activation')) {
    errorTitle.value = 'Email non vérifié'
    errorMessage.value = 'Votre adresse email n\'a pas encore été vérifiée. Consultez votre boîte mail et cliquez sur le lien de confirmation.'
    return
  }

  // Problème réseau / serveur
  if (
    raw.includes('network') || raw.includes('fetch') ||
    raw.includes('500') || raw.includes('503') || raw.includes('timeout')
  ) {
    errorTitle.value = 'Problème de connexion'
    errorMessage.value = 'Le serveur est temporairement indisponible. Vérifiez votre connexion internet et réessayez dans quelques instants.'
    return
  }

  // Mot de passe expiré
  if (raw.includes('expired') || raw.includes('password reset required')) {
    errorTitle.value = 'Mot de passe expiré'
    errorMessage.value = 'Votre mot de passe a expiré. Cliquez sur « Mot de passe oublié » pour en définir un nouveau.'
    return
  }

  // Erreur générique (fallback)
  errorTitle.value = 'Connexion impossible'
  errorMessage.value = 'Une erreur inattendue s\'est produite. Veuillez réessayer ou contacter le support si le problème persiste.'
}

// ── Handler principal ─────────────────────────────────────────────────────────
const handleLogin = async () => {
  loading.value = true
  clearError()
  fieldError.value = { email: '', password: '' }

  // Validation côté client avant envoi
  if (!form.value.email.includes('@')) {
    fieldError.value.email = 'Veuillez saisir une adresse email valide'
    errorTitle.value = 'Champ invalide'
    errorMessage.value = 'L\'adresse email saisie ne semble pas valide.'
    triggerShake()
    loading.value = false
    return
  }

  if (form.value.password.length < 1) {
    fieldError.value.password = 'Le mot de passe ne peut pas être vide'
    loading.value = false
    return
  }

  try {
    const result = await authStore.login({
      email: form.value.email,
      password: form.value.password
    })

    if (result.success) {
      const redirectTo = router.currentRoute.value.query.redirect as string || '/'
      await router.push(redirectTo)
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