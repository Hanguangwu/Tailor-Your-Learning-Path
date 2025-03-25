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
  },
  SET_INTERESTS(state, interests) {
    state.interests = interests
  },
  ADD_INTEREST(state, interest) {
    state.interests.push(interest)
  },
  REMOVE_INTEREST(state, interest) {
    state.interests = state.interests.filter(i => i !== interest)
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
  },
  async fetchInterests({ commit }) {
    try {
      const response = await axios.get('/api/profile/interests')
      if (response.data && response.data.interests) {
        commit('SET_INTERESTS', response.data.interests)
        return response.data
      } else {
        console.error('获取兴趣失败: 数据格式不正确')
      }
    } catch (error) {
      console.error('获取兴趣失败:', error)
    }
  },
  async addInterest({ commit }, interest) {
    try {
      const response = await axios.post('/api/profile/interests', { interest: interest })
      commit('ADD_INTEREST', response.data.interest)
      return response.data
    } catch (error) {
      console.error('添加兴趣失败:', error)
    }
  },
  async removeInterest({ commit }, interest) {
    try {
      await axios.delete(`/api/profile/interests/${interest}`)
      commit('REMOVE_INTEREST', interest)
      // 删除操作通常不需要返回数据，因此移除对 response.data 的引用
    } catch (error) {
      console.error('删除兴趣失败:', error)
    }
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}