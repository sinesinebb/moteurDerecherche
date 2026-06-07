<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-3xl font-bold mb-8 text-gray-900 dark:text-white">
      Paramètres du compte
    </h1>

    <div v-if="message" :class="['mb-4 p-4 rounded-lg', messageType === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
      {{ message }}
    </div>

    <!-- Section Avatar -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
        Photo de profil
      </h2>
      <div class="flex items-center space-x-6">
        <div class="relative w-24 h-24 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
          <img
            v-if="avatarPreview || authStore.user?.avatar"
            :src="avatarPreview || authStore.user?.avatar"
            alt="Avatar"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-3xl text-gray-400">
            {{ authStore.userInitial }}
          </div>
        </div>

        <div>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,image/gif"
            @change="onFileSelected"
            class="hidden"
          />
          <button
            @click="fileInput?.click()"
            class="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
          >
            Choisir une image
          </button>
          <button
            v-if="selectedFile"
            @click="uploadAvatar"
            :disabled="authStore.loading"
            class="ml-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ authStore.loading ? 'Upload...' : 'Enregistrer' }}
          </button>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Formats acceptés : JPEG, PNG, GIF (max 5 Mo)
          </p>
        </div>
      </div>
    </div>

    <!-- Zone dangereuse : Suppression de compte -->
    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl shadow-md p-6">
      <h2 class="text-xl font-semibold mb-2 text-red-700 dark:text-red-400">
        Zone dangereuse
      </h2>
      <p class="text-gray-700 dark:text-gray-300 mb-4">
        La suppression du compte est irréversible. Toutes vos données seront effacées.
      </p>

      <div v-if="!showDeleteConfirm">
        <button
          @click="showDeleteConfirm = true"
          class="bg-red-600 hover:bg-red-700 text-white font-medium px-6 py-2 rounded-lg transition-colors"
        >
          Supprimer mon compte
        </button>
      </div>
      <div v-else>
        <p class="mb-2 font-semibold text-gray-900 dark:text-white">
          Confirmez la suppression en saisissant votre mot de passe :
        </p>
        <input
          v-model="deletePassword"
          type="password"
          placeholder="Mot de passe"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4"
        />
        <div class="flex space-x-3">
          <button
            @click="deleteAccount"
            :disabled="authStore.loading"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ authStore.loading ? 'Suppression...' : 'Confirmer la suppression' }}
          </button>
          <button
            @click="showDeleteConfirm = false; deletePassword = ''"
            class="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
          >
            Annuler
          </button>
        </div>
      </div>
    </div>

    <NuxtLink
      to="/account"
      class="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline mt-8"
    >
      ← Retour au compte
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../../stores/auth.store'
import { useRouter } from '#app'

const authStore = useAuthStore()
const router = useRouter()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const avatarPreview = ref<string | null>(null)

const showDeleteConfirm = ref(false)
const deletePassword = ref('')

const message = ref('')
const messageType = ref<'success' | 'error'>('success')

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    avatarPreview.value = URL.createObjectURL(target.files[0])
  }
}

async function uploadAvatar() {
  if (!selectedFile.value) return
  message.value = ''
  const result = await authStore.uploadAvatar(selectedFile.value)
  if (result.success) {
    message.value = result.message
    messageType.value = 'success'
  } else {
    if (result.error === 'Session expirée. Veuillez vous reconnecter.') {
      await router.push('/login')
    } else {
      message.value = result.error
      messageType.value = 'error'
    }
  }
}

async function deleteAccount() {
  if (!deletePassword.value) {
    message.value = 'Veuillez saisir votre mot de passe'
    messageType.value = 'error'
    return
  }
  message.value = ''
  const result = await authStore.deleteAccount(deletePassword.value)
  if (result.success) {
    await router.push('/')
  } else {
    message.value = result.error || 'Erreur lors de la suppression'
    messageType.value = 'error'
    deletePassword.value = ''
  }
}
</script>