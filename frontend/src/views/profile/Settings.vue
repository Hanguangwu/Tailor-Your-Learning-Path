<template>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-2xl font-bold mb-6">个人设置</h2>
      <form @submit.prevent="updateProfile" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700">用户名</label>
          <input v-model="form.username" 
                 type="text" 
                 class="mt-1 block w-full border rounded-md px-3 py-2" />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">当前密码</label>
          <input v-model="form.currentPassword" 
                 type="password" 
                 class="mt-1 block w-full border rounded-md px-3 py-2" />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">新密码</label>
          <input v-model="form.newPassword" 
                 type="password" 
                 class="mt-1 block w-full border rounded-md px-3 py-2" />
        </div>
        
        <div>
          <button type="submit" 
                  class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700">
            保存修改
          </button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue'
  import { useStore } from 'vuex'
  import {ElMessage} from 'element-plus'
  export default {
    name: 'Settings',
    setup() {
      const store = useStore()
      const form = ref({
        username: '',
        currentPassword: '',
        newPassword: ''
      })
  
      const updateProfile = async () => {
        try {
          await store.dispatch('profile/updateProfile', form.value)
          ElMessage.success('个人信息更新成功')
          form.value.currentPassword = ''
          form.value.newPassword = ''
        } catch (error) {
          console.error('更新个人信息失败:', error)
          ElMessage.error(error.response?.data?.detail || '更新失败')
        }
      }
  
      return {
        form,
        updateProfile
      }
    }
  }
  </script>