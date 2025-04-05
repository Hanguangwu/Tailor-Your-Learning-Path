import axios from '@/axios'
import { jwtDecode } from 'jwt-decode'

const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
  userProfile: null  // 存储完整的用户资料
}

const getters = {
  isLoggedIn: state => !!state.token,
  currentUser: state => state.user,
  userProfile: state => state.userProfile
}

const actions = {
  // 注册和登录方法保持不变
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
      formDataObj.append('username', formData.username)
      formDataObj.append('password', formData.password)

      console.log('发送登录请求:', formData.username)

      const response = await axios.post('/api/auth/login', formDataObj, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      console.log('登录响应:', response)

      // 检查响应格式
      if (!response.access_token || !response.user) {
        console.error('登录响应格式不正确:', response)
        throw new Error('登录响应格式不正确')
      }

      const { access_token, user } = response

      commit('SET_AUTH_DATA', { token: access_token, user })

      // 设置 token 过期检查
      try {
        const decodedToken = jwtDecode(access_token)
        const expirationTime = decodedToken.exp * 1000 - 60000
        setTimeout(() => {
          commit('CLEAR_AUTH_DATA')
          alert('您的会话已过期，请重新登录。')
          // 注意: 这里需要导入 router
          if (window.router) {
            window.router.push('/login')
          }
        }, expirationTime - Date.now())
      } catch (tokenError) {
        console.error('解析 token 失败:', tokenError)
      }

      return response
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  },

  logout({ commit }) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    commit('CLEAR_AUTH_DATA')
  },

  // 统一的获取用户资料方法
  async getUserProfile({ commit }) {
    try {
      const response = await axios.get('/api/users/profile')
      commit('SET_USER_PROFILE', response.data)
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  },

  // 统一的更新用户资料方法
  async updateUserProfile({ commit, state, dispatch }, profileData) {
    try {
      const response = await axios.post('/api/users/update-profile', profileData)

      // 如果更新了用户名，同时更新本地存储的基本用户信息
      if (profileData.username) {
        const updatedUser = {
          ...state.user,
          username: profileData.username
        }
        commit('SET_USER', updatedUser)
        commit('SET_AUTH_DATA', { token: state.token, user: updatedUser })
      }

      // 更新完整的用户资料
      await dispatch('getUserProfile')

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
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },

  CLEAR_AUTH_DATA(state) {
    state.token = null
    state.user = null
    state.userProfile = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  SET_USER(state, user) {
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
  },

  SET_USER_PROFILE(state, profile) {
    state.userProfile = profile
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}