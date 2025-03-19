import axios from '@/axios'

const state = {
  featuredCourses: [],
  recommendedCourses: [],
  searchResults: [],
  featuredMeta: {    // 添加精选课程的元数据
    total: 0,
    page: 1,
    pageSize: 6,
    totalPages: 9
  },
  searchMeta: {
    total: 0,
    page: 1,
    pageSize: 9,
    totalPages: 0
  }
}

const mutations = {
  SET_FEATURED_COURSES(state, { courses, total, page, page_size, total_pages }) {
    state.featuredCourses = courses
    state.featuredMeta = {
      total,
      page,
      pageSize: page_size,
      totalPages: 9
      //totalPages: total_pages
    }
  },
  SET_RECOMMENDED_COURSES(state, courses) {
    state.recommendedCourses = courses
  },
  SET_SEARCH_RESULTS(state, { courses, total, page, page_size, total_pages }) {
    state.searchResults = courses
    state.searchMeta = {
      total,
      page,
      pageSize: page_size,
      totalPages: total_pages
    }
  },
  // 添加更新课程状态的 mutation
  UPDATE_COURSE_ENROLLMENT(state, courseId) {
    // 更新精选课程中的选课状态
    const featuredCourse = state.featuredCourses.find(c => c._id === courseId)
    if (featuredCourse) {
      featuredCourse.is_selected = true
      featuredCourse.enrollment_count = (featuredCourse.enrollment_count || 0) + 1
    }
    
    // 更新推荐课程中的选课状态
    const recommendedCourse = state.recommendedCourses.find(c => c._id === courseId)
    if (recommendedCourse) {
      recommendedCourse.is_selected = true
      recommendedCourse.enrollment_count = (recommendedCourse.enrollment_count || 0) + 1
    }
  },
  REMOVE_SELECTED_COURSE(state, courseId) {
    // 更新精选课程中的选课状态
    const featuredCourse = state.featuredCourses.find(c => c._id === courseId)
    if (featuredCourse) {
      featuredCourse.is_selected = false
      featuredCourse.enrollment_count = Math.max((featuredCourse.enrollment_count || 1) - 1, 0)
    }
    
    // 更新推荐课程中的选课状态
    const recommendedCourse = state.recommendedCourses.find(c => c._id === courseId)
    if (recommendedCourse) {
      recommendedCourse.is_selected = false
      recommendedCourse.enrollment_count = Math.max((recommendedCourse.enrollment_count || 1) - 1, 0)
    }
  }
}

const actions = {
  async fetchFeaturedCourses({ commit }, { page = 1 } = {}) {
    try {
      const response = await axios.get('/api/courses/featured', {
        params: { 
          page, 
          page_size: 6,
          total_pages: 9  // 添加总页数参数
        }
      })
      commit('SET_FEATURED_COURSES', {
        courses: response.data.courses,
        total: response.data.total,
        page: page,
        page_size: 6,
        total_pages: 9
      })
    } catch (error) {
      console.error('获取精选课程失败:', error)
      throw error
    }
  },
  
  async selectCourse({ commit }, courseId) {
    try {
      const response = await axios.post(`/api/courses/select/${courseId}`)
      // 选课成功后更新状态
      commit('UPDATE_COURSE_ENROLLMENT', courseId)
      return response.data
    } catch (error) {
      console.error('选课失败:', error)
      throw error
    }
  },

  async fetchRecommendedCourses({ commit }) {
    try {
      const response = await axios.get('/api/courses/recommended')
      commit('SET_RECOMMENDED_COURSES', response.data)
    } catch (error) {
      console.error('获取推荐课程失败:', error)
      throw error
    }
  },
  async searchCourses({ commit }, { query, page = 1 }) {
    try {
      const response = await axios.get('/api/courses/search', {
        params: {
          q: query,
          page,
          page_size: 9
        }
      })
      commit('SET_SEARCH_RESULTS', {
        courses: response.data.courses || [],
        total: response.data.total || 0,
        page: response.data.page || 1,
        page_size: response.data.page_size || 9,
        total_pages: response.data.total_pages || 0
      })
      return response.data
    } catch (error) {
      console.error('搜索课程失败:', error)
      // 搜索失败时返回空结果
      commit('SET_SEARCH_RESULTS', {
        courses: [],
        total: 0,
        page: 1,
        page_size: 9,
        total_pages: 0
      })
      throw error
    }
  },
  async unselectCourse({ commit }, courseId) {
    try {
      const response = await axios.delete(`/api/profile/courses/${courseId}`)
      // 退选成功后更新状态
      commit('REMOVE_SELECTED_COURSE', courseId)
      return response.data
    } catch (error) {
      console.error('退选课程失败:', error.response?.data || error.message)
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