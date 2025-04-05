<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="grid grid-cols-12 gap-6">
      <!-- 左侧导航 -->
      <div class="col-span-3">
        <div class="bg-white shadow rounded-lg p-4">
          <nav class="space-y-2">
            <router-link to="/profile/selected-courses"
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/selected-courses' }">
              已选课程
            </router-link>
            <router-link to="/profile/interests"
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/interests' }">
              兴趣管理
            </router-link>
            <router-link to="/profile/todo" class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/todo' }">
              待办事项
            </router-link>
            <router-link to="/profile/achievement-diary"
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/achievement-diary' }">
              成就日记
            </router-link>
            <router-link to="/profile/learning-pbl"
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/learning-pbl' }">
              成就排行榜
            </router-link>
            <router-link to="/profile/settings"
              class="block px-4 py-2 rounded-md hover:bg-indigo-50 hover:text-indigo-600"
              :class="{ 'bg-indigo-50 text-indigo-600': $route.path === '/profile/settings' }">
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

    // 使用统一的用户信息获取方法
    const user = computed(() => store.state.auth.user)
    const userProfile = computed(() => store.state.auth.userProfile)

    onMounted(async () => {
      try {
        // 使用统一的用户资料获取方法
        await store.dispatch('auth/getUserProfile')
        isLoading.value = false
      } catch (error) {
        console.error('加载个人资料失败:', error)
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
      userProfile,
      isLoading,
      viewCourse,
      logout
    }
  }
}
</script>