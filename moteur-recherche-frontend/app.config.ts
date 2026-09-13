// app.config.ts
import type { AppConfig } from '@nuxt/schema'

export default defineAppConfig({
  ui: {
    primary: 'blue',
    gray: 'slate'
  },
  
  // Votre configuration d'application
  appName: 'Luka',
  appVersion: '1.0.0'
} as AppConfig)