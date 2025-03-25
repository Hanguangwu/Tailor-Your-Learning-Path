<template>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-2xl font-bold mb-6">个性化学习路径</h2>
      
      <!-- 学习进度概览 -->
      <div class="mb-8">
        <div class="bg-indigo-50 rounded-lg p-4">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="font-medium text-indigo-800">学习进度</h3>
              <p class="text-sm text-indigo-600">已完成 {{ completedCount }} / {{ totalCourses }} 门课程</p>
            </div>
            <div class="w-32 h-32">
              <div class="relative w-full h-full">
                <!-- 这里可以添加环形进度条组件 -->
                <div class="absolute inset-0 flex items-center justify-center">
                  {{ Math.round(completedCount / totalCourses * 100) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 学习路径时间线 -->
      <div class="relative">
        <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-indigo-100"></div>
        
        <div v-for="(phase, index) in learningPath" :key="index" 
             class="relative pl-10 pb-8">
          <div class="absolute left-2 -translate-x-1/2 w-6 h-6 rounded-full"
               :class="phase.completed ? 'bg-indigo-600' : 'bg-gray-200'">
          </div>
          
          <div class="bg-white rounded-lg border p-4">
            <h3 class="font-medium text-lg mb-2">{{ phase.title }}</h3>
            <p class="text-gray-600 mb-4">{{ phase.description }}</p>
            
            <!-- 阶段课程列表 -->
            <div class="space-y-3">
              <div v-for="course in phase.courses" :key="course._id"
                   class="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <h4 class="font-medium">{{ course.course_name }}</h4>
                  <p class="text-sm text-gray-500">{{ course.description }}</p>
                </div>
                <button v-if="!course.is_selected"
                        @click="selectCourse(course._id)"
                        class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
                  开始学习
                </button>
                <span v-else class="text-green-600">已选课</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue'
  import { useStore } from 'vuex'
  
  export default {
    name: 'LearningPath',
    setup() {
      const store = useStore()
      const learningPath = ref([])
      
      const completedCount = computed(() => {
        return learningPath.value.reduce((acc, phase) => {
          return acc + phase.courses.filter(course => course.is_selected).length
        }, 0)
      })
      
      const totalCourses = computed(() => {
        return learningPath.value.reduce((acc, phase) => {
          return acc + phase.courses.length
        }, 0)
      })
  
      const fetchLearningPath = async () => {
        try {
          const response = await store.dispatch('profile/fetchLearningPath')
          learningPath.value = response.path
        } catch (error) {
          console.error('获取学习路径失败:', error)
        }
      }
  
      const selectCourse = async (courseId) => {
        try {
          await store.dispatch('courses/selectCourse', courseId)
          await fetchLearningPath()
        } catch (error) {
          console.error('选课失败:', error)
        }
      }
  
      onMounted(fetchLearningPath)
  
      return {
        learningPath,
        completedCount,
        totalCourses,
        selectCourse
      }
    }
  }
  </script>