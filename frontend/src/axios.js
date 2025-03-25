import axios from 'axios'
import store from './store'

const instance = axios.create({
    baseURL: import.meta.env.VITE_BASE_URL,
    timeout: 60000,  // 增加超时时间到60秒
    withCredentials: true
})

instance.interceptors.request.use(
    config => {
        const token = store.state.auth.token
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

instance.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

export default instance