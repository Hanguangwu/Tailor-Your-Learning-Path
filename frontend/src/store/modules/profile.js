import axios from '@/axios'

const state = {
  selectedCourses: [],
  interests: [],
  userProfile: null
}

const mutations = {
  SET_SELECTED_COURSES(state, courses) {
    state.selectedCourses = courses
  },
  SET_USER_PROFILE(state, profile) {
    state.userProfile = profile
  }
}

const actions = {
  async fetchSelectedCourses({ commit }) {
    try {
      const response = await axios.get('/api/profile/selected-courses')
      commit('SET_SELECTED_COURSES', response.data.courses)
      return response.data
    } catch (error) {
      console.error('获取已选课程失败:', error)
      throw error
    }
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
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}