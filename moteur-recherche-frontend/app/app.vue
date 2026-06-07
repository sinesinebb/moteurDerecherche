<!-- <template>
  <div>
    <NuxtPage v-if="$route.path === '/'" />
    
    <NuxtLayout v-else>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template> -->

<!-- app.vue -->
<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup>
// Pas besoin d'importer onMounted et useAuthStore ici
// Les stores Pinia sont automatiquement disponibles avec @pinia/nuxt
</script>