<template>
    <div class="flex-grow bg-gray-100">
        <!-- 顶部导航栏 -->
        <nav class="bg-white shadow">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <h1 class="text-xl font-bold">个人学习中心</h1>
                    </div>
                    <!-- <div class="flex items-center">
                        <span class="mr-4">{{ user.username }}</span>
                        <button @click="handleLogout" class="text-red-600 hover:text-red-800">
                            退出登录
                        </button>
                    </div> -->
                </div>
            </div>
        </nav>

        <!-- 主要内容区域 -->
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 mb-8">
            <!-- 搜索栏 -->
            <!--  -->

            <!-- 推荐课程 -->
            <div class="mb-8">
    <h2 class="text-2xl font-bold mb-4">为您推荐</h2>
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <CourseCard v-for="course in recommendedCourses" :key="course._id" :course="course"
            @select="selectCourse" />
    </div>
    
    <!-- 添加推荐课程的分页控件 -->
    <div class="flex justify-center mt-6" v-if="recommendedMeta.totalPages > 1">
        <nav class="flex items-center space-x-2">
            <button v-for="page in recommendedMeta.totalPages" :key="page"
                @click="handleRecommendedPageChange(page)" :class="[
                'px-4 py-2 rounded-md',
                page === recommendedMeta.page
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
            ]">
                {{ page }}
            </button>
        </nav>
    </div>
</div>

            <!-- 在精选课程部分添加分页控件 -->
            <div class="mb-8">
                <h2 class="text-2xl font-bold mb-4">精选课程</h2>
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    <CourseCard v-for="course in featuredCourses" :key="course._id" :course="course"
                        @select="selectCourse" />
                </div>

                <!-- 分页控件 -->
                <div class="flex justify-center mt-6" v-if="featuredMeta.totalPages > 1">
                    <nav class="flex items-center space-x-2">
                        <button v-for="page in featuredMeta.totalPages" :key="page"
                            @click="handleFeaturedPageChange(page)" :class="[
                            'px-4 py-2 rounded-md',
                            page === featuredMeta.page
                                ? 'bg-indigo-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                        ]">
                            {{ page }}
                        </button>
                    </nav>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CourseCard from '@/components/CourseCard.vue'
//import SearchBar from '@/components/SearchBar.vue'
export default {
    name: 'Dashboard',
    components: {
        CourseCard,
        //SearchBar
    },
    setup() {
        const store = useStore()
        const router = useRouter()

        const user = computed(() => store.state.auth.user)
        const featuredCourses = computed(() => store.state.courses.featuredCourses)
        const featuredMeta = computed(() => store.state.courses.featuredMeta)
        // 获取推荐课程状态
        const recommendedCourses = computed(() => store.state.courses.recommendedCourses)
        const recommendedMeta = computed(() => store.state.courses.recommendedMeta)

        onMounted(async () => {
            if (store.state.auth.token) {
                try {
                    await Promise.all([
                        store.dispatch('courses/fetchFeaturedCourses'),
                        await store.dispatch('courses/fetchRecommendedCourses', { page: 1 })
                    ])
                } catch (error) {
                    console.error('加载课程失败:', error)
                }
            }
        })

        const handleFeaturedPageChange = async (page) => {
            try {
                await store.dispatch('courses/fetchFeaturedCourses', { page })
                window.scrollTo({ top: 0, behavior: 'smooth' })
            } catch (error) {
                console.error('加载精选课程失败:', error)
            }
        }

        const handleRecommendedPageChange = async (page) => {
            try {
                await store.dispatch('courses/fetchRecommendedCourses', { page })
                window.scrollTo({ top: 0, behavior: 'smooth' })
            } catch (error) {
                console.error('加载推荐课程失败:', error)
            }
        }

        // const handleSearch = async (searchText) => {
        //     if (searchText.trim()) {
        //         await router.push({
        //             path: '/search',
        //             query: { q: searchText }
        //         })
        //     }
        // }

        const selectCourse = async (courseId) => {
            try {
                await store.dispatch('courses/selectCourse', courseId)
                ElMessage.success('选课成功')
            } catch (error) {
                console.error('选课失败:', error)
                ElMessage.error(error.response?.data?.detail || '选课失败')
            }
        }

        const handleLogout = () => {
            store.dispatch('auth/logout')
            router.push('/login')
        }

        return {
            user,
            featuredCourses,
            featuredMeta,
            recommendedCourses,  // 确保推荐课程数据被正确返回
            recommendedMeta,
            //handleSearch,
            selectCourse,
            handleLogout,
            handleFeaturedPageChange,
            handleRecommendedPageChange
        }
    }
}
</script>