// app.config.ts
import type { AppConfig } from '@nuxt/schema'

export default defineAppConfig({
  ui: {
    primary: 'blue',
    gray: 'slate'
  },
  
  // Votre configuration d'application
  appName: 'TechSearch',
  appVersion: '1.0.0'
} as AppConfig)