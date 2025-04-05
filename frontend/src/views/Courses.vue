<template>
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
            <!-- 筛选条件 -->
            <div class="mb-6 bg-white p-4 rounded-lg shadow">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <!-- 平台筛选 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">平台</label>
                        <select v-model="filters.platform" @change="handleFilterChange"
                            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                            <option value="">全部平台</option>
                            <option value="coursera">Coursera</option>
                            <option value="mooc">中国大学MOOC</option>
                            <option value="edx">edX</option>
                            <option value="other">其他平台</option>
                        </select>
                    </div>

                    <!-- 分类筛选 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
                        <select v-model="filters.category" @change="handleFilterChange"
                            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                            <option value="">全部分类</option>
                            <option value="工学">工学</option>
                            <option value="管理学">管理学</option>
                            <option value="计算机科学">计算机科学</option>
                            <option value="教育教学">教育教学</option>
                            <option value="经济学">经济学</option>
                            <option value="理学">理学</option>
                            <option value="人工智能">人工智能</option>
                            <option value="社会科学">社会科学</option>
                            <option value="通识教育">通识教育</option>
                            <option value="外语">外语</option>
                            <option value="文学文化">文学文化</option>
                            <option value="医药卫生">医药卫生</option>
                            <option value="艺术学">艺术学</option>
                        </select>
                    </div>

                    <!-- 搜索框 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">关键词搜索</label>
                        <div class="mt-1 flex rounded-md shadow-sm">
                            <input type="text" v-model="filters.keyword" @keyup.enter="handleFilterChange"
                                class="focus:ring-indigo-500 focus:border-indigo-500 flex-1 block w-full rounded-md sm:text-sm border-gray-300"
                                placeholder="搜索课程名称">
                            <button @click="handleFilterChange"
                                class="ml-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                搜索
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 清除筛选按钮 -->
                <div class="mt-4 flex justify-end">
                    <button @click="clearFilters"
                        class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        清除筛选
                    </button>
                </div>
            </div>

            <!-- 课程列表 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <CourseCard v-for="course in courses" :key="course._id" :course="course" @select="handleCourseSelect" />
            </div>
            <div v-if="loading" class="flex justify-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>

            <div v-else-if="courses.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">未找到课程</h3>
                <p class="mt-1 text-sm text-gray-500">尝试调整筛选条件或清除筛选。</p>
            </div>

            <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <CourseCard v-for="course in courses" :key="course._id" :course="course" />
            </div>

            <!-- 分页控件 -->
            <div class="flex justify-center mt-6" v-if="totalPages > 1">
                <nav class="flex items-center space-x-2">
                    <!-- 第一页 -->
                    <button @click="handlePageChange(1)" :class="[
                            'px-4 py-2 rounded-md',
                            1 === currentPage
                                ? 'bg-indigo-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                        ]">
                        1
                    </button>

                    <!-- 左省略号 -->
                    <span v-if="showLeftEllipsis" class="px-4 py-2">...</span>

                    <!-- 中间页码 -->
                    <button v-for="page in visiblePages" :key="page" @click="handlePageChange(page)" :class="[
                            'px-4 py-2 rounded-md',
                            page === currentPage
                                ? 'bg-indigo-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                        ]">
                        {{ page }}
                    </button>

                    <!-- 右省略号 -->
                    <span v-if="showRightEllipsis" class="px-4 py-2">...</span>

                    <!-- 最后一页 -->
                    <button v-if="totalPages > 1" @click="handlePageChange(totalPages)" :class="[
                            'px-4 py-2 rounded-md',
                            totalPages === currentPage
                                ? 'bg-indigo-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                        ]">
                        {{ totalPages }}
                    </button>
                </nav>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/axios'
import CourseCard from '@/components/CourseCard.vue'

export default {
    name: 'Courses',
    components: {
        CourseCard
    },
    // 添加 props 配置
    props: {
        category: {
            type: String,
            default: ''
        },
        platform: {
            type: String,
            default: ''
        },
        page: {
            type: Number,
            default: 1
        }
    },
    setup(props) {
        const route = useRoute()
        const router = useRouter()

        const courses = ref([])
        const loading = ref(true)
        const currentPage = ref(1)
        const totalPages = ref(1)
        const categories = ref([])
        const platforms = ref([])

        // 筛选条件
        const filters = reactive({
            keyword: '',
            platform: '',
            category: ''
        })

        // 从URL查询参数初始化筛选条件
        const initFiltersFromQuery = () => {
            filters.category = route.query.category || ''
            filters.platform = route.query.platform || ''
            currentPage.value = parseInt(route.query.page) || 1
            filters.keyword = route.query.keyword || ''
        }

        // 更新URL查询参数
        const updateQueryParams = () => {
            const query = {}
            if (filters.keyword) query.keyword = filters.keyword
            if (filters.platform) query.platform = filters.platform
            if (filters.category) query.category = filters.category
            if (currentPage.value > 1) query.page = currentPage.value

            router.replace({ query })
        }

        // 获取所有类别
        const fetchCategories = async () => {
            try {
                const response = await axios.get('/api/courses/categories')
                categories.value = response.data.categories
            } catch (error) {
                console.error('获取课程类别失败:', error)
            }
        }

        // 获取所有平台
        const fetchPlatforms = async () => {
            try {
                const response = await axios.get('/api/courses/platforms')
                platforms.value = response.data.platforms
            } catch (error) {
                console.error('获取课程平台失败:', error)
            }
        }

        // 获取课程数据
        const fetchCourses = async () => {
            loading.value = true
            try {
                let params = {
                    page: currentPage.value,
                    page_size: 9
                }

                // 添加所有筛选条件
                if (filters.keyword) params.keyword = filters.keyword
                if (filters.platform) params.platform = filters.platform
                if (filters.category) params.category = filters.category

                const response = await axios.get('/api/courses/list/filter', { params })
                courses.value = response.data.courses
                totalPages.value = response.data.total_pages

                updateQueryParams()
            } catch (error) {
                console.error('获取课程失败:', error)
            } finally {
                loading.value = false
            }
        }

        // 搜索课程
        const searchCourses = () => {
            currentPage.value = 1
            fetchCourses()
        }

        // 添加筛选处理函数
        const handleFilterChange = () => {
            currentPage.value = 1
            fetchCourses()
        }

        // 修改 clearFilters 函数
        const clearFilters = () => {
            filters.keyword = ''
            filters.platform = ''
            filters.category = ''
            currentPage.value = 1
            fetchCourses()
        }

        // 添加选课处理函数
        const handleCourseSelect = async (courseId) => {
            try {
                await axios.post(`/api/courses/select/${courseId}`)
                // 更新课程列表中的选课状态
                const index = courses.value.findIndex(course => course._id === courseId)
                if (index !== -1) {
                    courses.value[index].is_selected = true
                    courses.value[index].enrollment_count += 1
                }
            } catch (error) {
                console.error('选课失败:', error)
                // 可以添加错误提示
                alert(error.response?.data?.detail || '选课失败')
            }
        }

        // 翻页
        const handlePageChange = async (page) => {
            try {
                currentPage.value = page
                await fetchCourses()
                // 平滑滚动到页面顶部
                window.scrollTo({ top: 0, behavior: 'smooth' })
            } catch (error) {
                console.error('加载课程失败:', error)
            }
        }
        // 添加分页逻辑计算属性
        const visiblePages = computed(() => {
            const delta = 2 // 当前页前后显示的页数
            let start = Math.max(2, currentPage.value - delta)
            let end = Math.min(totalPages.value - 1, currentPage.value + delta)

            // 调整start和end，确保显示足够的页码
            if (currentPage.value - delta > 2) {
                start = currentPage.value - delta
            }
            if (currentPage.value + delta < totalPages.value - 1) {
                end = currentPage.value + delta
            }

            // 生成页码数组
            const pages = []
            for (let i = start; i <= end; i++) {
                if (i !== 1 && i !== totalPages.value) { // 排除第一页和最后一页
                    pages.push(i)
                }
            }
            return pages
        })

        // 是否显示左省略号
        const showLeftEllipsis = computed(() => {
            return currentPage.value - 3 > 1
        })

        // 是否显示右省略号
        const showRightEllipsis = computed(() => {
            return currentPage.value + 3 < totalPages.value
        })
        const prevPage = () => {
            if (currentPage.value > 1) {
                currentPage.value--
                fetchCourses()
            }
        }

        const nextPage = () => {
            if (currentPage.value < totalPages.value) {
                currentPage.value++
                fetchCourses()
            }
        }

        // 平台名称显示转换
        const getPlatformDisplayName = (platform) => {
            const platformMap = {
                'coursera': 'Coursera',
                'mooc': '中国大学MOOC',
                'edx': 'edX',
                'other': '其他平台'
            }
            return platformMap[platform] || platform
        }

        // 监听路由变化
        // 确保在组件挂载和props变化时重新获取数据
        watch(() => route.query, (newQuery) => {
            initFiltersFromQuery()
            fetchCourses()
        }, { deep: true })

        onMounted(() => {
            initFiltersFromQuery()
            fetchCourses()
            fetchCategories()
            fetchPlatforms()
        })

        return {
            courses,
            loading,
            handlePageChange,
            currentPage,
            totalPages,
            categories,
            platforms,
            filters,
            fetchCourses,
            searchCourses,
            handleFilterChange,
            clearFilters,
            handleCourseSelect,
            prevPage,
            nextPage,
            getPlatformDisplayName,
            visiblePages,
            showLeftEllipsis,
            showRightEllipsis
        }
    }
}
</script>