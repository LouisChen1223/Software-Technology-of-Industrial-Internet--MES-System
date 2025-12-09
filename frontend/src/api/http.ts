import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1',
  timeout: 15000
})

http.interceptors.request.use((config) => {
  // TODO: attach token if needed
  return config
})

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default http
