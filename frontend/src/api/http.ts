import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    // 避免浏览器/代理缓存导致列表不刷新
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache'
  }
})

http.interceptors.request.use((config) => {
  // TODO: attach token if needed
  // 为 GET 请求添加时间戳参数，避免返回缓存数据
  if ((config.method || 'get').toLowerCase() === 'get') {
    const url = new URL((config.url || ''), 'http://dummy')
    url.searchParams.set('_ts', String(Date.now()))
    // axios 接受相对路径，保留 pathname+search
    config.url = `${url.pathname}${url.search}`
    // 同时设置 no-cache 头以强化不缓存策略（兼容 AxiosHeaders 类型）
    const h: any = config.headers || {}
    h['Cache-Control'] = 'no-cache'
    h['Pragma'] = 'no-cache'
    config.headers = h
  }
  return config
})

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const resp = error.response
    if (resp) {
      const status = resp.status
      let msg = ''
      const detail = resp.data?.detail
      if (typeof detail === 'string') {
        msg = detail
      } else if (Array.isArray(detail) && detail[0]?.msg) {
        msg = detail[0].msg
      } else if (status >= 400 && status < 500) {
        msg = `请求错误（${status}）`
      } else {
        msg = '服务器异常，请稍后重试'
      }
      ElMessage.error(msg)
    } else {
      ElMessage.error('网络异常，请检查连接')
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default http
