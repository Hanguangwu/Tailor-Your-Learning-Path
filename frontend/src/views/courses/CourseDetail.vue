<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div v-if="loading" class="text-center py-4">
      <el-loading :active="loading" />
    </div>

    <div v-else-if="error" class="text-center text-red-600 py-4">
      {{ error }}
    </div>

    <div v-else class="space-y-6">
      <!-- 课程头部信息 -->
      <div class="flex items-start space-x-6">
        <div class="w-48 h-48 flex-shrink-0">
          <img :src="course.course_logo_url || 'src/assets/logo.png'" :alt="course.course_name"
            class="w-full h-full object-cover rounded-lg shadow">
        </div>

        <div class="flex-grow">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ course.course_name }}</h1>
          <div class="flex items-center space-x-4 mb-4">
            <span class="px-3 py-1 rounded-full text-sm font-semibold bg-indigo-100 text-indigo-800">
              {{ course.category }}
            </span>
            <span class="px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800">
              {{ course.difficulty }}
            </span>
          </div>
          <p class="text-gray-600 text-lg mb-4">{{ course.description }}</p>
        </div>
      </div>

      <!-- 课程详细信息 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div class="bg-gray-50 p-6 rounded-lg">
          <h3 class="text-lg font-semibold mb-4">课程信息</h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">选课人数</span>
              <span class="font-medium">{{ course.enrollment_count || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">课程评分</span>
              <span class="font-medium">{{ course.rating || '暂无评分' }}</span>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 p-6 rounded-lg">
          <h3 class="text-lg font-semibold mb-4">课程链接</h3>
          <a :href="course.course_url" target="_blank"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            访问课程
          </a>
        </div>
      </div>
    </div>
  </div>
  <!-- 添加评论组件 -->
  <CourseComments :courseId="courseId" />
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '@/axios'
import CourseComments from '@/components/CourseComments.vue'

export default {
  components: {
    CourseComments
  },
  name: 'CourseDetail',
  setup() {
    const route = useRoute()
    const course = ref({})
    const loading = ref(true)
    const error = ref(null)
    const courseId = ref(route.params.id)  // 添加这行

    const fetchCourseDetail = async () => {
      try {
        loading.value = true
        const response = await axios.get(`/api/courses/${courseId.value}`)
        course.value = response.data
      } catch (err) {
        error.value = '获取课程信息失败'
        ElMessage.error('获取课程信息失败')
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchCourseDetail)

    return {
      course,
      loading,
      error,
      courseId  // 添加这行
    }
  }
}
</script>