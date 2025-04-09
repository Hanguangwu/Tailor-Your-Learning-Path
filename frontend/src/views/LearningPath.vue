<template>
  <div class="container mx-auto px-4 py-8 mt-16">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-2xl font-bold mb-6">个性化学习路径推荐</h1>
      
      <!-- 推荐设置 -->
      <div v-if="!recommendations.length" class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">设置推荐参数</h2>
        
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">推荐课程数量（最多9门）</label>
          <el-input-number v-model="recommendationCount" :min="1" :max="9" />
        </div>
        
        <el-button type="primary" @click="getRecommendations" :loading="loading">
          获取学习路径推荐
        </el-button>
      </div>
      
      <!-- 推荐结果 -->
      <div v-if="recommendations.length" class="mb-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">为您推荐的学习路径</h2>
          <el-button @click="resetRecommendations">重新推荐</el-button>
        </div>
        
        <div class="space-y-6">
          <div v-for="(course, index) in recommendations" :key="course.course_id" 
               class="bg-white rounded-lg shadow-md p-6 transition-all hover:shadow-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-indigo-100 text-indigo-800 font-bold rounded-full w-10 h-10 flex items-center justify-center mr-4">
                {{ index + 1 }}
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold mb-2">{{ course.title }}</h3>
                <p class="text-gray-600 mb-4">{{ course.description }}</p>
                
                <div class="mb-4">
                  <h4 class="font-medium text-gray-800 mb-2">推荐理由:</h4>
                  <p class="text-gray-700">{{ course.reason }}</p>
                </div>
                
                <div class="flex justify-end">
                  <router-link :to="`/courses/${course.course_id}`" class="text-indigo-600 hover:text-indigo-800">
                    查看课程详情 →
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'LearningPath',
  setup() {
    const recommendationCount = ref(5)
    const recommendations = ref([])
    const loading = ref(false)
    
    const getRecommendations = async () => {
      loading.value = true
      try {
        const response = await axios.post('/api/recommendations/learning-path', {
          count: recommendationCount.value
        })

        console.log('获取推荐成功:', response.data)
        
        recommendations.value = response.data
        
        if (recommendations.value.length === 0) {
          ElMessage.warning('未找到适合您的课程推荐，请完善您的个人资料')
        }
      } catch (error) {
        console.error('获取推荐失败:', error)
        ElMessage.error(error.response?.data?.detail || '获取推荐失败')
      } finally {
        loading.value = false
      }
    }
    
    const resetRecommendations = () => {
      recommendations.value = []
    }
    
    return {
      recommendationCount,
      recommendations,
      loading,
      getRecommendations,
      resetRecommendations
    }
  }
}
</script>