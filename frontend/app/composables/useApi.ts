export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase

  async function get<T = any>(url: string, params?: Record<string, any>): Promise<T> {
    try {
      return await $fetch<T>(url, { baseURL, params })
    } catch (e: any) {
      console.error("API error:", e)
      throw e
    }
  }

  async function post<T = any>(url: string, body?: any): Promise<T> {
    try {
      return await $fetch<T>(url, { baseURL, method: "POST", body })
    } catch (e: any) {
      console.error("API error:", e)
      throw e
    }
  }

  return { get, post }
}