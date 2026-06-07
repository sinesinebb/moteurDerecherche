// composables/useApi.ts
export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl || 'http://localhost'

  // Helper pour ajouter le token
  const getHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
    if (process.client) {
      const token = localStorage.getItem('token')
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }
    return headers
  }

  // Fonctions HTTP
  const get = async <T>(url: string, params?: any): Promise<T> => {
    const headers = getHeaders()
    return await $fetch<T>(url, { baseURL, method: 'GET', params, headers })
  }
  const post = async <T>(url: string, body?: any): Promise<T> => {
    const headers = getHeaders()
    return await $fetch<T>(url, { baseURL, method: 'POST', body, headers })
  }
  const put = async <T>(url: string, body?: any): Promise<T> => {
    const headers = getHeaders()
    return await $fetch<T>(url, { baseURL, method: 'PUT', body, headers })
  }
  const del = async <T>(url: string): Promise<T> => {
    const headers = getHeaders()
    return await $fetch<T>(url, { baseURL, method: 'DELETE', headers })
  }

  return { get, post, put, delete: del }
}