import axios from '@/axios'

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

      const response = await axios.post('/api/auth/login', formDataObj, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      const { access_token, user } = response.data
      
      commit('SET_AUTH_DATA', { token: access_token, user })
      return response.data
    } catch (error) {
      throw error
    }
  },

  logout({ commit }) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    commit('CLEAR_AUTH_DATA')
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
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}