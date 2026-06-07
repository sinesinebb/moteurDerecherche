// types/nuxt.d.ts

// Types globaux pour Nuxt 4
import type { NuxtConfig } from 'nuxt/schema'

declare global {
  // Fonctions Nuxt globales
  export const defineNuxtConfig: (config: NuxtConfig) => NuxtConfig
  export const defineAppConfig: (config: any) => any
  export const definePageMeta: (meta: any) => void
  export const defineNuxtRouteMiddleware: (middleware: any) => any
  
  // Runtime config
  export const useRuntimeConfig: () => {
    public: {
      apiBaseUrl: string
      appName: string
      appVersion: string
    }
  }
  
  // $fetch global
  export const $fetch: {
    create: (options: any) => any
  }
}

// Déclaration pour Nitro
declare module 'nuxt/schema' {
  interface NuxtConfig {
    nitro?: {
      preset?: string
      serveStatic?: boolean
      timing?: boolean
      compressPublicAssets?: boolean
      [key: string]: any
    }
  }
}

// Pour que le fichier soit traité comme un module
export {}