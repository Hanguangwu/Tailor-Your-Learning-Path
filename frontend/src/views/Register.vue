<template>
  <div class="min-h-screen flex items-center justify-center relative">
    <!-- 背景图 -->
    <div class="absolute inset-0 z-0">
      <img src="@/assets/wallhaven-register.jpg" alt="注册背景" class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-br from-blue-900/50 to-purple-900/50 backdrop-blur-[2px]"></div>
    </div>

    <!-- 注册表单卡片 -->
    <div class="relative z-10 w-full max-w-md mx-auto p-8 bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">创建账号</h1>
        <p class="text-gray-600 mt-2">已有账号？
          <router-link to="/login" class="text-blue-600 hover:text-blue-700 font-medium">
            立即登录
          </router-link>
        </p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5">
        <!-- 表单内容保持不变 -->
        <div class="relative">
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input v-model="form.username" type="text" required class="form-input"
            :class="{ 'border-red-500': errors.username }" />
          <p v-if="errors.username" class="error-message">{{ errors.username }}</p>
        </div>

        <!-- 其他输入框保持不变 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">邮箱</label>
          <input v-model="form.email" type="email" required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">密码</label>
          <input v-model="form.password" type="password" required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" />
        </div>

        <!-- 兴趣选择部分改为更紧凑的布局 -->
        <div class="relative">
          <label class="block text-sm font-medium text-gray-700 mb-2">选择你感兴趣的领域</label>
          <div class="grid grid-cols-3 gap-2">
            <label v-for="interest in interests" :key="interest" class="interest-tag"
              :class="{ 'selected': form.interests.includes(interest) }">
              <input type="checkbox" v-model="form.interests" :value="interest" class="hidden" />
              <span class="text-sm">{{ interest }}</span>
            </label>
          </div>
        </div>

        <button type="submit" class="submit-button mt-6" :disabled="isLoading">
          <span v-if="!isLoading">创建账号</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>
    </div>
  </div>
</template>
<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    const isLoading = ref(false)
    const errors = reactive({})  // 添加 errors 对象

    const interests = [
      "工学",  
      "管理学",  
      "计算机科学",  
      "教育教学",  
      "经济学",  
      "理学",  
      "人工智能",  
      "社会科学",  
      "通识教育",  
      "外语",  
      "文学文化",  
      "医药卫生",  
      "艺术学"  
    ]

    const form = ref({
      username: '',
      email: '',
      password: '',
      interests: []
    })

    // 添加表单验证
    const validateForm = () => {
      const newErrors = {}

      if (!form.value.username) {
        newErrors.username = '请输入用户名'
      }

      if (!form.value.email) {
        newErrors.email = '请输入邮箱'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
        newErrors.email = '请输入有效的邮箱地址'
      }

      if (!form.value.password) {
        newErrors.password = '请输入密码'
      } else if (form.value.password.length < 6) {
        newErrors.password = '密码长度至少为6位'
      }

      Object.assign(errors, newErrors)
      return Object.keys(newErrors).length === 0
    }

    const handleRegister = async () => {
      if (!validateForm()) return

      isLoading.value = true
      try {
        await store.dispatch('auth/register', {
          username: form.value.username,
          email: form.value.email,
          password: form.value.password,
          interests: form.value.interests
        })
        router.push('/login')
      } catch (error) {
        if (error.response?.data?.detail) {
          // 处理后端返回的具体错误信息
          const errorMsg = error.response.data.detail
          if (errorMsg.includes('邮箱')) {
            errors.email = errorMsg
          } else if (errorMsg.includes('用户名')) {
            errors.username = errorMsg
          } else {
            errors.general = errorMsg
          }
        } else {
          errors.general = '注册失败，请稍后重试'
        }
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      interests,
      handleRegister,
      isLoading,
      errors
    }
  }
}
</script>
<style scoped>
.form-input {
  @apply block w-full px-4 py-3 rounded-lg border border-gray-300/80 bg-white/80 backdrop-blur-sm shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200;
}

.interest-tag {
  @apply flex items-center justify-center px-3 py-2 rounded-lg border border-gray-200/80 bg-white/80 backdrop-blur-sm cursor-pointer transition-all duration-200 hover:border-blue-500 hover:bg-blue-50;
}

.interest-tag.selected {
  @apply bg-blue-500 border-blue-600 text-white;
}

.submit-button {
  @apply w-full flex justify-center py-3 px-4 rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed text-base font-medium;
}

.loading-spinner {
  @apply w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin;
}

.error-message {
  @apply absolute text-sm text-red-500 mt-1;
}
</style>
