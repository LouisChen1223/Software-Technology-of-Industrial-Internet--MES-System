import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    token: '',
    user: { name: 'operator' },
    settings: { apiBase: '/api' }
  }),
  actions: {
    setToken(t: string) { this.token = t }
  }
})
