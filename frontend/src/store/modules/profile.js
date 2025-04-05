import axios from '@/axios'

const state = {
  selectedCourses: [],
  interests: []
  // 移除 userProfile，统一使用 auth.js 中的
}

const mutations = {
  SET_SELECTED_COURSES(state, courses) {
    state.selectedCourses = courses
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
  // 移除 SET_USER_PROFILE
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
  // 移除 getUserProfile 和 updateProfile 方法，统一使用 auth.js 中的

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
    } catch (error) {
      console.error('删除兴趣失败:', error)
    }
  },
  
  async unselectCourse({ commit }, courseId) {
    try {
      await axios.delete(`/api/courses/select/${courseId}`)
      return true
    } catch (error) {
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