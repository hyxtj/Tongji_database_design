import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      // 确保token没有多余的引号
      const cleanToken = token.replace(/^"|"$/g, '')
      // console.log('Sending token:', cleanToken) // Debug token
      config.headers.Authorization = `Bearer ${cleanToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // 如果响应包含404错误，且在开发环境下，尝试使用模拟数据端点
    if (error.response?.status === 404 && !originalRequest._retryWithMock && import.meta.env.DEV) {
      console.warn(`❌ API端点 ${originalRequest.url} 不存在，尝试使用模拟数据...`)
      
      // 标记已尝试过模拟数据，避免无限循环
      originalRequest._retryWithMock = true
      
      try {
        // 尝试调用模拟数据端点
        const mockResponse = await axios.get(`/api/mock${originalRequest.url}`, originalRequest.params)
        console.log(`✅ 使用模拟数据成功: ${originalRequest.url}`)
        return mockResponse
      } catch (mockError) {
        console.warn(`⚠️ 模拟数据也失败: ${mockError.message}`)
        // 如果模拟数据也失败，继续处理原始错误
      }
    }
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期,请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 422:
          console.error('422 Error Details:', error.response.data)
          ElMessage.error(error.response.data?.error || '验证失败,请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          // 不显示404错误消息，因为已经尝试使用模拟数据
          if (!originalRequest._retryWithMock) {
            ElMessage.error('请求的资源不存在')
          }
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data?.error || '请求失败')
      }
    } else {
      ElMessage.error('网络错误,请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default api
