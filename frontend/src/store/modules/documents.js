import axios from '@/axios'

const state = {
  documents: [],
  loading: false,
  error: null
}

const mutations = {
  SET_DOCUMENTS(state, documents) {
    state.documents = documents
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  ADD_DOCUMENT(state, document) {
    state.documents.unshift(document)
  },
  REMOVE_DOCUMENT(state, documentId) {
    state.documents = state.documents.filter(doc => doc.id !== documentId)
  }
}

const actions = {
  async fetchDocuments({ commit }) {
    commit('SET_LOADING', true)
    try {
      // 修正API路径
      const response = await axios.get('/api/documents/history')
      commit('SET_DOCUMENTS', response.data)
      commit('SET_ERROR', null)
      return response.data
    } catch (error) {
      console.error('获取文档失败:', error)
      commit('SET_ERROR', '获取文档失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async saveDocument({ commit }, documentData) {
    //console.log('保存文档数据:', documentData)
    //console.log("执行到saveDocument了")
    commit('SET_LOADING', true)
    try {
      // 修正API路径
      const response = await axios.post('/api/documents/save', documentData)
      console.log('保存文档响应:', response.data)
      commit('ADD_DOCUMENT', response.data)
      commit('SET_ERROR', null)
      return response.data
    } catch (error) {
      console.error('保存文档失败:', error)
      commit('SET_ERROR', '保存文档失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async deleteDocument({ commit }, documentId) {
    commit('SET_LOADING', true)
    try {
      // 修正API路径
      await axios.delete(`/api/documents/${documentId}`)
      commit('REMOVE_DOCUMENT', documentId)
      commit('SET_ERROR', null)
      return { success: true }
    } catch (error) {
      console.error('删除文档失败:', error)
      commit('SET_ERROR', '删除文档失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  allDocuments: state => state.documents,
  isLoading: state => state.loading,
  hasError: state => state.error !== null,
  errorMessage: state => state.error
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}