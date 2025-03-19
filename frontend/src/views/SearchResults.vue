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
            <SearchBar @search="handleSearch" :initial-value="$route.query.q" />
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <template v-if="!isLoading">
        <div class="mb-6">
          <h2 class="text-2xl font-bold">
            搜索结果: "{{ $route.query.q }}"
            <span class="text-gray-500 text-lg ml-2">(共 {{ searchMeta.total }} 个结果)</span>
          </h2>
        </div>

        <div v-if="searchResults.length > 0" class="space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <CourseCard v-for="course in searchResults" :key="course._id" :course="course" @select="selectCourse" />
          </div>

          <!-- 分页控件 -->
          <div class="flex justify-center mt-6" v-if="searchMeta.totalPages > 1">
            <nav class="flex items-center space-x-2">
              <button v-for="page in searchMeta.totalPages" :key="page" @click="handlePageChange(page)" :class="[
              'px-4 py-2 rounded-md',
              page === searchMeta.page
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            ]">
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
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import CourseCard from '@/components/CourseCard.vue'
import SearchBar from '@/components/SearchBar.vue'

export default {
  name: 'SearchResults',
  components: {
    CourseCard,
    SearchBar
  },
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const isLoading = ref(false)

    const searchResults = computed(() => store.state.courses.searchResults)
    const searchMeta = computed(() => store.state.courses.searchMeta)

    const performSearch = async (query, page = 1) => {
      if (!query?.trim()) return
      
      isLoading.value = true
      try {
        await store.dispatch('courses/searchCourses', { query, page })
      } catch (error) {
        console.error('搜索失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    const handlePageChange = async (page) => {
      await performSearch(route.query.q, page)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    onMounted(async () => {
      if (route.query.q) {
        await performSearch(route.query.q)
      }
    })

    const handleSearch = async (query) => {
      await router.push({
        path: '/search',
        query: { q: query }
      })
      await performSearch(query)
    }

    const selectCourse = async (courseId) => {
      try {
        await store.dispatch('courses/selectCourse', courseId)
        ElMessage.success('选课成功')
      } catch (error) {
        console.error('选课失败:', error)
        ElMessage.error(error.response?.data?.detail || '选课失败')
      }
    }

    return {
      isLoading,
      searchResults,
      searchMeta,         // 添加这一行
      handleSearch,
      selectCourse,
      handlePageChange
    }
  }
}
</script>