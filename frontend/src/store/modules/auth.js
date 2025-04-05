import axios from '@/axios'
import { jwtDecode } from 'jwt-decode'  // 添加 jwt-decode 库用于解析 token
const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null
}

const getters = {
  isLoggedIn: state => !!state.token
}

const actions = {
  async register({ commit }, userData) {
    try {
      const response = await axios.post('/api/auth/register', userData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async login({ commit }, formData) {
    try {
      // 创建 FormData 对象以匹配后端 OAuth2PasswordRequestForm 的格式
      const formDataObj = new FormData()
      formDataObj.append('username', formData.username)  // 后端使用 username 字段接收邮箱
      formDataObj.append('password', formData.password)
      console.log("执行到auth.js中的login1")
      const response = await axios.post('/api/auth/login', formDataObj, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const { access_token, user } = response.data
      console.log("执行到auth.js中的login2")
      commit('SET_AUTH_DATA', { token: access_token, user })

      // 设置 token 过期检查
      const decodedToken = jwtDecode(access_token)
      const expirationTime = decodedToken.exp * 1000 - 60000  // 提前一分钟检查过期
      setTimeout(() => {
        // 自动注销或刷新 token
        commit('CLEAR_AUTH_DATA')
        alert('您的会话已过期，请重新登录。')
        router.push('/login')
      }, expirationTime - Date.now())

      return response.data
    } catch (error) {
      throw error
    }
  },

  logout({ commit }) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    commit('CLEAR_AUTH_DATA')
  },

  async getUserProfile({ commit }) {
    try {
      const response = await axios.get('/api/profile')
      commit('SET_USER_PROFILE', response.data)
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  },
  async updateProfile({ commit }, profileData) {
    try {
      const response = await axios.post('/api/profile', profileData)
      commit('SET_USER_PROFILE', response.data)
      return response.data
    } catch (error) {
      console.error('更新个人信息失败:', error)
      throw error
    }
  }
}

const mutations = {
  SET_AUTH_DATA(state, { token, user }) {
    state.token = token
    state.user = user
    //console.log("SET_AUTH_DATA:", token)
    //console.log("SET_AUTH_DATA:", user)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },
  CLEAR_AUTH_DATA(state) {
    state.token = null
    state.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },
  SET_USER_PROFILE(state, profile) {
    state.userProfile = profile
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}