<template>
  <div class="flex-grow bg-gray-100">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/dashboard" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-arrow-left mr-2"></i>返回
            </router-link>
          </div>
          <div class="flex-1 max-w-2xl mx-4">
            <SearchBar @search="handleSearch" :initial-value="searchQuery" />
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div v-if="isLoading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <template v-else>
        <div class="mb-6">
          <h2 class="text-2xl font-bold">
            搜索结果: "{{ searchQuery }}"
            <span class="text-gray-500 text-lg ml-2">(共 {{ searchMeta.total }} 个结果)</span>
          </h2>
        </div>

        <div v-if="searchResults.length > 0" class="space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <CourseCard 
              v-for="course in searchResults" 
              :key="course._id" 
              :course="course" 
              @select="handleCourseSelect"
              @unselect="handleCourseUnselect"
            />
          </div>

          <div class="flex justify-center mt-6" v-if="searchMeta.totalPages > 1">
            <nav class="flex items-center space-x-2">
              <button 
                v-for="page in searchMeta.totalPages" 
                :key="page" 
                @click="handlePageChange(page)" 
                :class="[
                  'px-4 py-2 rounded-md',
                  page === currentPage
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
            </nav>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <div class="text-gray-500 text-lg">未找到相关课程，请尝试其他关键词</div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CourseCard from '@/components/CourseCard.vue'

export default {
  name: 'SearchResults',
  components: {
    CourseCard
  },
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const isLoading = ref(false)
    const currentPage = ref(1)

    const searchQuery = computed(() => route.query.keyword || '')
    const searchResults = computed(() => store.state.courses.searchResults)  // 确保从 courses 模块中获取
    const searchMeta = computed(() => store.state.courses.searchMeta)  // 确保从 courses 模块中获取

    const performSearch = async (keyword, page = 1) => {
      if (!keyword?.trim()) {
        router.push('/dashboard')
        return
      }
      
      isLoading.value = true
      try {
        await store.dispatch('courses/searchCourses', {  // 确保使用 courses 模块的 action
          keyword: keyword.trim(), 
          page 
        })
        currentPage.value = page
      } catch (error) {
        ElMessage.error('搜索失败，请稍后重试')
        console.error('搜索失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    const handlePageChange = (page) => {
      performSearch(searchQuery.value, page)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const handleCourseSelect = async (courseId) => {
      try {
        await store.dispatch('courses/selectCourse', courseId)
        ElMessage.success('选课成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '选课失败')
      }
    }

    const handleCourseUnselect = async (courseId) => {
      try {
        await store.dispatch('courses/unselectCourse', courseId)
        ElMessage.success('已取消选课')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '取消选课失败')
      }
    }

    watch(() => route.query.keyword, (newKeyword) => {
      if (newKeyword) {
        performSearch(newKeyword)
      }
    })

    onMounted(() => {
      if (searchQuery.value) {
        performSearch(searchQuery.value)
      }
    })

    return {
      isLoading,
      searchQuery,
      searchResults,
      searchMeta,
      currentPage,
      handlePageChange,
      handleCourseSelect,
      handleCourseUnselect
    }
  }
}
</script>