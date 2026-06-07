<template>
  <div class="max-w-md mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
    <h2 class="text-2xl font-bold mb-4">Vérification de l'email</h2>
    <p class="mb-4">Un code a été envoyé à {{ email }}. Saisissez-le ci-dessous.</p>
    <form @submit.prevent="handleVerify">
      <input v-model="code" type="text" placeholder="Code à 6 chiffres" class="w-full p-2 border rounded mb-4" />
      <button type="submit" class="w-full bg-blue-600 text-white p-2 rounded">Vérifier</button>
    </form>
    <button @click="resendCode" class="mt-4 text-sm text-blue-600">Renvoyer le code</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth.store'
import { useRouter, useRoute } from '#app'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const email = ref(route.query.email as string || '')
const code = ref('')

const handleVerify = async () => {
  const result = await authStore.verifyEmail(email.value, code.value)
  if (result.success) {
    alert('Email vérifié avec succès')
    router.push('/account')
  } else {
    alert(result.error)
  }
}

const resendCode = async () => {
  await authStore.sendVerificationEmail(email.value)
  alert('Nouveau code envoyé')
}
</script>