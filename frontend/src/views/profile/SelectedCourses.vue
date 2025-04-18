<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div v-if="loading" class="text-center py-4">
      <el-loading :active="loading" />
    </div>

    <div v-else-if="error" class="text-center text-red-600 py-4">
      {{ error }}
    </div>

    <div v-else>
      <!-- 搜索和标题部分 -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">已选课程 ({{ courses.length }})</h2>
      </div>

      <!-- 课程列表 -->
      <div v-if="filteredCourses.length > 0" class="overflow-x-auto">
        <!-- 表格内容 -->
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">课程名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">课程简介</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">难度</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">平台</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="course in filteredCourses" :key="course._id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ course.course_name }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="ml-4">
                    <div class="text-sm text-gray-500 truncate" :title="course.description"
                      v-if="course.description.length > 12">
                      {{ course.description.slice(0, 12) }}<span v-if="course.description.length > 12">...</span>
                    </div>
                    <div v-else>
                      {{ course.description }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-indigo-100 text-indigo-800">
                  {{ course.category }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ course.difficulty }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ course.platform }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewCourseDetail(course._id)" class="text-indigo-600 hover:text-indigo-900 mr-3">
                  查看详情
                </button>
                <button @click="removeCourse(course._id)" class="text-red-600 hover:text-red-900">
                  退选
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 分页控件 -->
        <div class="mt-4 flex justify-center">
          <el-pagination v-model:current-page="currentPage" :page-size="10" :total="courses.length"
            layout="prev, pager, next" />
        </div>
      </div>

      <div v-else class="text-center py-8 text-gray-500">
        暂无已选课程
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'  // 添加这行导入
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'  // 添加路由导入

export default {
  name: 'SelectedCourses',
  setup() {
    const store = useStore()
    const router = useRouter()  // 添加路由实例
    const courses = ref([])
    const loading = ref(true)
    const error = ref(null)
    const searchQuery = ref('')
    const currentPage = ref(1)
    const pageSize = 10

    const fetchCourses = async () => {
      try {
        loading.value = true
        const response = await store.dispatch('profile/fetchSelectedCourses')
        courses.value = response.courses || []
        loading.value = false
      } catch (err) {
        error.value = '获取课程列表失败'
        ElMessage.error('获取课程列表失败')
        loading.value = false
      }
    }

    // 计算属性：过滤和分页后的课程列表
    const filteredCourses = computed(() => {
      let filtered = courses.value
      if (searchQuery.value) {
        filtered = filtered.filter(course =>
          course.course_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          course.description.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }
      const start = (currentPage.value - 1) * pageSize
      return filtered.slice(start, start + pageSize)
    })

    // 计算总页数
    const totalPages = computed(() =>
      Math.ceil(courses.value.length / pageSize)
    )

    // 添加退选课程方法
    const removeCourse = async (courseId) => {
      try {
        await ElMessageBox.confirm('确定要退选该课程吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        // 修改这里：使用 profile 模块的 action
        await store.dispatch('profile/unselectCourse', courseId)
        ElMessage.success('退选成功')
        await fetchCourses()  // 重新获取课程列表
      } catch (error) {
        if (error !== 'cancel') {  // 不是取消操作导致的错误
          ElMessage.error(error.response?.data?.detail || '退选失败')
          console.error('退选失败:', error)
        }
      }
    }

    // 添加查看课程详情方法
    const viewCourseDetail = (courseId) => {
      router.push(`/courses/${courseId}`)
    }

    onMounted(fetchCourses)

    return {
      courses,
      loading,
      error,
      searchQuery,
      currentPage,
      filteredCourses,
      totalPages,
      fetchCourses,
      removeCourse,     // 添加到返回对象
      viewCourseDetail  // 添加到返回对象
    }
  }
}
</script>