import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',
    '@pinia/nuxt'
  ],

  // Pas de configuration Google

  plugins: [], // Supprimer le plugin Google s'il reste
  
  nitro: {
    preset: 'node-server',
    serveStatic: true,
    timing: true,
    compressPublicAssets: true,
    devProxy: {
      '/api': {
        target: 'http://localhost:80',
        //target: 'http://nginx-gateway',
        changeOrigin: true,  
        rewrite: (path) => path
      }
    }
  },
  
  sourcemap: false,
  // @ts-ignore
  pinia: {
    storesDirs: ['./stores/**'],
    disableHydrate: true,
  },
  
  colorMode: {
    preference: 'system',
    fallback: 'light',
    classSuffix: '',
    storageKey: 'techsearch-theme'
  },
  
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE || '',
      wsBaseUrl: process.env.NUXT_PUBLIC_WS_BASE || 'ws://localhost/ws',   // ← ajout
      appName: process.env.NUXT_PUBLIC_APP_NAME || 'TechSearch Engine',
      appVersion: process.env.NUXT_PUBLIC_APP_VERSION || '1.0.0'
    }
  },
  
  css: ['~/assets/css/main.css'],
  
  app: {
    head: {
      title: 'TechSearch - Moteur de Recherche Informatique',
      htmlAttrs: { lang: 'fr' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Moteur de recherche spécialisé en informatique avec architecture microservices' },
        { name: 'theme-color', content: '#3b82f6' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { 
          rel: 'stylesheet', 
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' 
        }
      ]
    },
    rootId: 'nuxt-app',
    buildAssetsDir: '/_nuxt/'
  },
  
  typescript: {
    strict: false,
    typeCheck: false,
    shim: false
  },
  
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },
  
  build: {
    transpile: ['@vue/runtime-dom']
  },
  
  imports: {
    dirs: [
      'composables/**',
      'utils/**'
    ]
  }
})