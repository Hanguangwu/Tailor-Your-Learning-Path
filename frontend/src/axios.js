import axios from 'axios'

// 创建axios实例
const instance = axios.create({
    // 在生产环境中，baseURL应该是相对路径，因为API请求会通过代理
    baseURL: import.meta.env.VITE_BACKEND_BASE_URL || '',
    timeout: 60000,  // 增加超时时间到60秒
    withCredentials: true
})

// 请求拦截器
instance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
instance.interceptors.response.use(
    response => {
        // 返回完整响应，保留原始结构
        return response
    },
    error => {
        // 统一处理错误
        const errorMsg = error.response?.data?.detail || error.message || '未知错误'
        console.error('API Error:', errorMsg)
        
        // 处理401错误（未授权）
        if (error.response?.status === 401) {
            console.warn('用户未授权，可能需要重新登录')
            // 可以在这里添加重定向到登录页面的逻辑
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
        }
        
        return Promise.reject(error)
    }
)

export default instance