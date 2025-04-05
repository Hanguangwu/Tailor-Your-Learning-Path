<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-2xl font-bold mb-6">个人设置</h2>
    <form @submit.prevent="updateProfile" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700">邮箱</label>
        <input v-model="form.email" type="email" disabled
          class="mt-1 block w-full border rounded-md px-3 py-2 bg-gray-100" />
        <span class="text-xs text-gray-500">邮箱地址不可修改</span>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">用户名</label>
        <input v-model="form.username" type="text" class="mt-1 block w-full border rounded-md px-3 py-2" />
      </div>

      <div class="border-t pt-6 mt-6">
        <h3 class="text-lg font-medium mb-4">修改密码</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">当前密码</label>
            <input v-model="form.currentPassword" type="password"
              class="mt-1 block w-full border rounded-md px-3 py-2" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">新密码</label>
            <input v-model="form.newPassword" type="password" class="mt-1 block w-full border rounded-md px-3 py-2" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">确认新密码</label>
            <input v-model="form.confirmPassword" type="password"
              class="mt-1 block w-full border rounded-md px-3 py-2" />
          </div>
        </div>
      </div>

      <div class="flex justify-end space-x-4">
        <button type="button" @click="resetForm" class="px-4 py-2 border rounded-md hover:bg-gray-50">
          取消
        </button>
        <button type="submit" class="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700">
          保存修改
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Settings',
  setup() {
    const store = useStore()
    const form = ref({
      email: '',
      username: '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    // 获取用户信息
    const fetchUserInfo = async () => {
      try {
        const userInfo = await store.dispatch('auth/getUserProfile')  // 修改为 getUserProfile
        form.value.email = userInfo.email
        form.value.username = userInfo.username
      } catch (error) {
        console.error('获取用户信息失败:', error)
        ElMessage.error('获取用户信息失败')
      }
    }

    // 重置表单
    const resetForm = () => {
      form.value.currentPassword = ''
      form.value.newPassword = ''
      form.value.confirmPassword = ''
      fetchUserInfo() // 重新获取用户信息
    }

    // 更新个人信息
    // 更新个人信息
    const updateProfile = async () => {
      try {
        // 验证密码修改
        if (form.value.newPassword || form.value.currentPassword) {
          if (!form.value.currentPassword) {
            ElMessage.warning('请输入当前密码')
            return
          }
          if (!form.value.newPassword) {
            ElMessage.warning('请输入新密码')
            return
          }
          if (form.value.newPassword !== form.value.confirmPassword) {
            ElMessage.warning('两次输入的新密码不一致')
            return
          }
          if (form.value.newPassword.length < 6) {
            ElMessage.warning('新密码长度不能小于6位')
            return
          }
        }

        await store.dispatch('auth/updateUserProfile', {  // 确保调用 updateUserProfile
          username: form.value.username,
          currentPassword: form.value.currentPassword,
          newPassword: form.value.newPassword
        })

        ElMessage.success('个人信息更新成功')
        resetForm()
      } catch (error) {
        console.error('更新个人信息失败:', error)
        ElMessage.error(error.response?.data?.detail || '更新失败')
      }
    }

    onMounted(fetchUserInfo)

    return {
      form,
      updateProfile,
      resetForm
    }
  }
}
</script>