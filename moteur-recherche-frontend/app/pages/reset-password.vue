<template>
  <div class="max-w-md mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
    <h2 class="text-2xl font-bold mb-4">Réinitialisation du mot de passe</h2>
    
    <!-- Étape 1 : demande d'email -->
    <div v-if="!step">
      <p class="mb-4">Entrez votre email pour recevoir un code de vérification.</p>
      <form @submit.prevent="requestReset">
        <input
          v-model="email"
          type="email"
          placeholder="Votre email"
          required
          class="w-full p-2 border rounded mb-4 dark:bg-gray-700"
        />
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Envoi...' : 'Envoyer le code' }}
        </button>
      </form>
      <p v-if="errorMsg" class="text-red-500 text-sm mt-2">{{ errorMsg }}</p>
    </div>

    <!-- Étape 2 : code + nouveau mot de passe -->
    <div v-else>
      <p class="mb-4">Un code a été envoyé à <strong>{{ email }}</strong>.</p>
      <form @submit.prevent="performReset">
        <input
          v-model="code"
          type="text"
          placeholder="Code reçu"
          required
          class="w-full p-2 border rounded mb-2 dark:bg-gray-700"
        />
        <input
          v-model="newPassword"
          type="password"
          placeholder="Nouveau mot de passe"
          required
          class="w-full p-2 border rounded mb-2 dark:bg-gray-700"
        />
        <input
          v-model="confirmPassword"
          type="password"
          placeholder="Confirmer le mot de passe"
          required
          class="w-full p-2 border rounded mb-4 dark:bg-gray-700"
        />
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Réinitialisation...' : 'Réinitialiser' }}
        </button>
      </form>
      <p v-if="errorMsg" class="text-red-500 text-sm mt-2">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth.store'
import { useRouter } from '#app'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const step = ref(false)
const loading = ref(false)
const errorMsg = ref('')

const requestReset = async () => {
  loading.value = true
  errorMsg.value = ''
  const result = await authStore.requestPasswordReset(email.value)
  if (result.success) {
    step.value = true
  } else {
    errorMsg.value = result.error
  }
  loading.value = false
}

const performReset = async () => {
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Les mots de passe ne correspondent pas'
    return
  }
  if (newPassword.value.length < 6) {
    errorMsg.value = 'Le mot de passe doit contenir au moins 6 caractères'
    return
  }
  loading.value = true
  errorMsg.value = ''
  const result = await authStore.resetPassword(email.value, code.value, newPassword.value)
  if (result.success) {
    alert('Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.')
    router.push('/login')
  } else {
    errorMsg.value = result.error
  }
  loading.value = false
}
</script>