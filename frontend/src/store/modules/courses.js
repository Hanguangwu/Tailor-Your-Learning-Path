import axios from '@/axios'

const state = {
  featuredCourses: [],
  featuredMeta: {    // 添加精选课程的元数据
    total: 0,
    page: 1,
    pageSize: 6,
    totalPages: 9
  },
  recommendedCourses: [],
  searchResults: [],
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

  async searchCourses({ commit }, { keyword, page = 1 }) {
    try {
      const response = await axios.get('/api/courses/search', {
        params: {
          keyword,
          page,
          page_size: 9
        }
      })
      commit('SET_SEARCH_RESULTS', response.data)
      return response.data
    } catch (error) {
      console.error('搜索课程失败:', error)
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
      if (response.data && response.data.length > 0) {
        commit('SET_RECOMMENDED_COURSES', response.data)
      } else {
        console.warn('没有推荐课程')
      }
      return response.data
    } catch (error) {
      console.error('获取推荐课程失败:', error)
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