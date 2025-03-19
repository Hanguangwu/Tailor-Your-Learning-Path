<template>
  <nav class="fixed top-0 w-full bg-white shadow z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- 左侧导航项 -->
        <div class="flex items-center space-x-8">
          <!-- Logo -->
          <router-link to="/" class="text-xl font-bold text-indigo-600">
            量身学程
          </router-link>

          <!-- 导航链接 -->
          <div class="hidden md:flex items-center space-x-8">
            <!-- 课程下拉菜单 -->
            <div class="relative group">
              <button class="flex items-center text-gray-700 hover:text-indigo-600">
                所有课程
                <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <!-- 下拉内容 -->
              <div class="absolute hidden group-hover:block w-48 bg-white shadow-lg rounded-md mt-2">
                <div class="py-2">
                  <router-link to="/courses?category=platform" class="block px-4 py-2 text-gray-700 hover:bg-indigo-50">
                    平台课程
                  </router-link>
                  <router-link to="/courses?category=category" class="block px-4 py-2 text-gray-700 hover:bg-indigo-50">
                    分类课程
                  </router-link>
                </div>
              </div>
            </div>

            <router-link to="/chat" class="text-gray-700 hover:text-indigo-600">
              AI聊天
            </router-link>
          </div>
        </div>

        <!-- 中间搜索框 -->
        <div class="flex-1 max-w-2xl px-4 hidden md:flex items-center justify-center">
          <SearchBar @search="handleSearch" />
        </div>

        <!-- 右侧用户区域 -->
        <div class="flex items-center">
          <!-- 未登录状态 -->
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="text-gray-700 hover:text-indigo-600 px-3 py-2">
              登录
            </router-link>
            <router-link to="/register" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
              注册
            </router-link>
          </template>

          <!-- 已登录状态 -->
          <div v-else class="relative" @mouseenter="showDropdown = true" @mouseleave="hideDropdown">
            <button class="flex items-center text-gray-700 hover:text-indigo-600">
              {{ username }}
              <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <!-- 用户下拉菜单 - 修改显示逻辑 -->
            <div v-show="showDropdown"
              class="absolute right-0 w-48 bg-white shadow-lg rounded-md mt-2 py-2 transition-all duration-200"
              @mouseenter="clearHideTimer" @mouseleave="hideDropdown">
              <router-link to="/profile/courses" class="block px-4 py-2 text-gray-700 hover:bg-indigo-50"
                @click="showDropdown = false">
                个人中心
              </router-link>
              <button @click="handleLogout" class="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50">
                退出登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref } from 'vue'
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import SearchBar from './SearchBar.vue'

export default {
  name: 'Navbar',
  components: {
    SearchBar
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const showDropdown = ref(false)
    const hideTimer = ref(null)

    const isLoggedIn = computed(() => store.state.auth.token !== null)
    const username = computed(() => store.state.auth.user?.username || '')

    const hideDropdown = () => {
      hideTimer.value = setTimeout(() => {
        showDropdown.value = false
      }, 200)
    }

    const clearHideTimer = () => {
      if (hideTimer.value) {
        clearTimeout(hideTimer.value)
        hideTimer.value = null
      }
    }

    const handleSearch = async (searchText) => {
      if (searchText.trim()) {
        await router.push({
          path: '/search',
          query: { q: searchText }
        })
      }
    }

    const handleLogout = async () => {
      showDropdown.value = false
      await store.dispatch('auth/logout')
      router.push('/login')
    }

    return {
      isLoggedIn,
      username,
      showDropdown,
      handleSearch,
      handleLogout,
      hideDropdown,
      clearHideTimer
    }
  }
}
</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>