// moteur-recherche-frontend/utils/formatters.ts

// Formater la taille de fichier
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Formater la date relative
export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'À l\'instant'
  if (diffMins < 60) return `Il y a ${diffMins} minute${diffMins > 1 ? 's' : ''}`
  if (diffHours < 24) return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`
  if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`
  if (diffDays < 30) return `Il y a ${Math.floor(diffDays / 7)} semaine${Math.floor(diffDays / 7) > 1 ? 's' : ''}`
  if (diffDays < 365) return `Il y a ${Math.floor(diffDays / 30)} mois`
  
  return `Il y a ${Math.floor(diffDays / 365)} an${Math.floor(diffDays / 365) > 1 ? 's' : ''}`
}

// Formater la date complète
export function formatFullDate(dateString: string): string {
  const date = new Date(dateString)
  
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Formater les nombres (vues, likes, etc.)
export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
  }
  return num.toString()
}

// Tronquer le texte
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

// Formater l'URL pour l'affichage
export function formatUrlForDisplay(url: string): string {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace('www.', '')
  } catch {
    return url
  }
}

// Formater le score en pourcentage
export function formatScore(score: number): string {
  return Math.round(score * 100) + '%'
}

// Obtenir l'emoji pour le type de contenu
export function getContentTypeEmoji(type: string): string {
  const emojis: Record<string, string> = {
    'web': '🌐',
    'documentation': '📄',
    'tutorial': '📚',
    'video': '🎬',
    'image': '🖼️',
    'pdf': '📄',
    'docx': '📝',
    'md': '📓',
    'code': '💻',
    'forum': '💬',
    'blog': '📝'
  }
  
  return emojis[type] || '📎'
}

// Obtenir le nom du type de contenu
export function getContentTypeName(type: string): string {
  const names: Record<string, string> = {
    'web': 'Site Web',
    'documentation': 'Documentation',
    'tutorial': 'Tutoriel',
    'video': 'Vidéo',
    'image': 'Image',
    'pdf': 'PDF',
    'docx': 'Document Word',
    'md': 'Markdown',
    'code': 'Code Source',
    'forum': 'Forum',
    'blog': 'Article de Blog'
  }
  
  return names[type] || 'Document'
}