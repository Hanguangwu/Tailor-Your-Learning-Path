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

          <!-- 桌面端导航菜单 -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link to="/courses" class="text-gray-700 hover:text-indigo-600">
              全部课程
            </router-link>

            <router-link to="/websites" class="text-gray-700 hover:text-indigo-600">
              资源网站
            </router-link>

            <router-link to="/chat" class="text-gray-700 hover:text-indigo-600">
              AI聊天
            </router-link>

            <!-- 新增记忆工具按钮 -->
            <router-link to="/memory-tool" class="text-gray-700 hover:text-indigo-600">
              记忆工具
            </router-link>

            <!-- 新增自测功能按钮 -->
            <router-link to="/self-test" class="text-gray-700 hover:text-indigo-600">
              自测练习
            </router-link>
          </div>
        </div>

        <!-- 中间搜索框 - 仅桌面端显示 -->
        <div class="flex-1 max-w-2xl px-4 hidden md:flex items-center justify-center">
          <SearchBar @search="handleSearch" />
        </div>
        
        <!-- 移动端汉堡菜单按钮 -->
        <div class="md:hidden flex items-center">
          <button @click="toggleMobileMenu" class="text-gray-700 hover:text-indigo-600 focus:outline-none">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 右侧用户区域 - 仅桌面端显示 -->
        <div class="hidden md:flex items-center">
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
          <template v-else>
            <div class="relative" @mouseenter="showDropdown = true" @mouseleave="hideDropdown">
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
                <router-link to="/profile/personal-info" class="block px-4 py-2 text-gray-700 hover:bg-indigo-50"
                  @click="showDropdown = false">
                  个人中心
                </router-link>
                <router-link to="/personal-trait" class="block px-4 py-2 text-gray-700 hover:bg-indigo-50"
                  @click="showDropdown = false">
                  学习偏好设置
                </router-link>
                <router-link to="/learning-path" class="block px-4 py-2 text-gray-700 hover:text-indigo-600">
                  学习路径
                </router-link>
                <button @click="handleLogout" class="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50">
                  退出登录
                </button>
              </div>
              <!-- <div v-show="showDropdown"
                class="absolute right-0 w-48 bg-white shadow-lg rounded-md mt-2 py-2 transition-all duration-200"
                @mouseenter="clearHideTimer" @mouseleave="hideDropdown">
                <router-link to="/profile/courses" class="block px-4 py-2 text-gray-700 hover:bg-indigo-50"
                  @click="showDropdown = false">
                  个人中心
                </router-link>
                <button @click="handleLogout" class="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50">
                  退出登录
                </button>
              </div> -->
            </div>
          </template>
        </div>
      </div>
    </div>
    
    <!-- 移动端菜单 -->
    <div class="md:hidden bg-white shadow-lg mobile-menu" :class="{ 'menu-open': mobileMenuOpen }">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <router-link to="/courses" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
          全部课程
        </router-link>
        <router-link to="/websites" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
          资源网站
        </router-link>
        <router-link to="/chat" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
          AI聊天
        </router-link>
        <router-link to="/memory-tool" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
          记忆工具
        </router-link>
        <router-link to="/self-test" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
          自测练习
        </router-link>
        
        <!-- 移动端搜索框 -->
        <div class="px-3 py-2">
          <SearchBar @search="handleSearch" />
        </div>
        
        <!-- 移动端用户区域 -->
        <div class="px-3 py-2">
          <!-- 未登录状态 -->
          <template v-if="!isLoggedIn">
            <div class="flex flex-col space-y-2">
              <router-link to="/login" class="block w-full text-center px-3 py-2 rounded-md text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
                登录
              </router-link>
              <router-link to="/register" class="block w-full text-center px-3 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700">
                注册
              </router-link>
            </div>
          </template>
          
          <!-- 已登录状态 -->
          <template v-else>
            <div class="border-t border-gray-200 pt-2">
              <div class="px-3 py-2 text-gray-700 font-medium">{{ username }}</div>
              <router-link to="/profile/personal-info" class="block px-3 py-2 rounded-md text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
                个人中心
              </router-link>
              <router-link to="/personal-trait" class="block px-3 py-2 rounded-md text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
                学习偏好设置
              </router-link>
              <router-link to="/learning-path" class="block px-3 py-2 rounded-md text-gray-700 hover:text-indigo-600 hover:bg-indigo-50">
                学习路径
              </router-link>
              <button @click="handleLogout" class="block w-full text-left px-3 py-2 rounded-md text-red-600 hover:bg-red-50">
                退出登录
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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
    const mobileMenuOpen = ref(false)

    const isLoggedIn = computed(() => store.state.auth.token !== null)
    const username = computed(() => isLoggedIn.value ? store.state.auth.user?.username || '' : '')  // 确保未登录时不显示用户名
    
    // 切换移动端菜单显示状态
    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
    }
  
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

    const handleSearch = (keyword) => {
      if (keyword.trim()) {
        router.push({
          path: '/search',
          query: { keyword: keyword.trim() }
        })
      }
    }

    const handleLogout = async () => {
      showDropdown.value = false
      await store.dispatch('auth/logout')
      router.push('/login')
    }

    // 移除窗口关闭事件监听器，因为它会在页面刷新时导致用户退出登录
    // const handleWindowClose = () => {
    //   store.dispatch('auth/logout')
    // }

    // window.addEventListener('beforeunload', handleWindowClose)

    // onBeforeUnmount(() => {
    //   window.removeEventListener('beforeunload', handleWindowClose)
    // })

    // 使用sessionStorage区分页面刷新和浏览器关闭
    const handleWindowClose = () => {
      // 在页面即将卸载时设置一个标记
      sessionStorage.setItem('isReloading', 'true')
      
      // 设置一个延迟，如果是真正的关闭浏览器，这个延迟不会执行
      setTimeout(() => {
        sessionStorage.removeItem('isReloading')
      }, 0)
    }

    window.addEventListener('beforeunload', handleWindowClose)

    // 在组件挂载时检查是否是刷新页面
    onMounted(() => {
      const isReloading = sessionStorage.getItem('isReloading')
      if (isReloading) {
        // 是刷新页面，移除标记
        sessionStorage.removeItem('isReloading')
      } else {
        // 是新打开的页面，不做任何操作
      }
    })

    // 在组件卸载前移除事件监听
    onBeforeUnmount(() => {
      window.removeEventListener('beforeunload', handleWindowClose)
    })
    
    // 监听路由变化，关闭移动端菜单
    router.afterEach(() => {
      if (mobileMenuOpen.value) {
        mobileMenuOpen.value = false
      }
    })

    return {
      isLoggedIn: computed(() => store.getters['auth/isLoggedIn']),
      username,
      showDropdown,
      mobileMenuOpen,
      toggleMobileMenu,
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

/* 添加额外的样式来改善下拉菜单的交互体验 */
.group:hover .group-hover\:visible {
  visibility: visible;
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

.group\/platform:hover .group-hover\/platform\:visible {
  visibility: visible;
}

.group\/platform:hover .group-hover\/platform\:opacity-100 {
  opacity: 1;
}

.group\/category:hover .group-hover\/category\:visible {
  visibility: visible;
}

.group\/category:hover .group-hover\/category\:opacity-100 {
  opacity: 1;
}

/* 移动端菜单过渡动画 */
.mobile-menu {
  transition: all 0.3s ease-in-out;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
}

.mobile-menu.menu-open {
  max-height: 1000px;
  overflow: visible;
  opacity: 1;
}
</style>
