// 添加一个 action 用于检查和更新成就
actions: {
  async checkAndUpdateAchievements({ commit }) {
    try {
      await axios.post('/api/profile/check-achievements');
      const response = await axios.get('/api/profile/achievements');
      commit('SET_USER_ACHIEVEMENTS', response.data);
      return response.data;
    } catch (error) {
      console.error('更新成就失败:', error);
      throw error;
    }
  }
}