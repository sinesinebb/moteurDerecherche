<!-- <template>
  <div>
    <NuxtPage v-if="$route.path === '/'" />
    
    <NuxtLayout v-else>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template> -->

<!-- app.vue -->
<!-- <template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template> -->



<template>
  <div>
    <!-- Si la route ne demande pas de layout, on n'utilise pas NuxtLayout -->
    <NuxtLayout v-if="route.meta.layout !== false">
      <NuxtPage />
    </NuxtLayout>
    <!-- Sinon, on rend la page directement sans layout -->
    <NuxtPage v-else />
  </div>
</template>

<script setup>
const route = useRoute()
</script>