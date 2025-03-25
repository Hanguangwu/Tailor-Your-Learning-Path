<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="grid grid-cols-12 gap-6">
      <!-- 左侧导航 -->
      <div class="col-span-3">
        <div class="bg-white shadow rounded-lg p-4">
          <nav class="space-y-2">
            <router-link 
              to="/profile/courses" 
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/courses' }"
            >
              已选课程
            </router-link>
            <router-link 
              to="/profile/interests" 
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/interests' }"
            >
              兴趣管理
            </router-link>
            <router-link 
              to="/profile/learning-path" 
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/learning-path' }"
            >
              学习路径
            </router-link>
            <router-link 
              to="/profile/settings" 
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/settings' }"
            >
              个人设置
            </router-link>
          </nav>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="col-span-9">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    const router = useRouter()
    const isLoading = ref(true)
    const selectedCourses = ref([])

    const user = computed(() => store.getters['auth/currentUser'])

    onMounted(async () => {
      try {
        await store.dispatch('auth/getUserProfile')
        // 这里应该有一个获取用户已选课程的API调用
        // 暂时使用空数组
        selectedCourses.value = []
        isLoading.value = false
      } catch (error) {
        console.error('Failed to load profile:', error)
        isLoading.value = false
      }
    })

    const viewCourse = (courseId) => {
      router.push(`/course/${courseId}`)
    }

    const logout = () => {
      store.dispatch('auth/logout')
      router.push('/login')
    }

    return {
      user,
      isLoading,
      selectedCourses,
      viewCourse,
      logout
    }
  }
}
</script>