<template>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-2xl font-bold mb-4">兴趣管理</h2>
      <div class="space-y-4">
        <div class="flex flex-wrap gap-2">
          <span v-for="interest in userInterests" :key="interest"
                class="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full flex items-center">
            {{ interest }}
            <button @click="removeInterest(interest)" class="ml-2 text-indigo-600 hover:text-indigo-800">
              ×
            </button>
          </span>
        </div>
        
        <div class="flex gap-2">
          <input v-model="newInterest" 
                 @keyup.enter="addInterest"
                 class="flex-1 border rounded-md px-3 py-2"
                 placeholder="添加新兴趣" />
          <button @click="addInterest"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
            添加
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue'
  import { useStore } from 'vuex'
  
  export default {
    name: 'Interests',
    setup() {
      const store = useStore()
      const userInterests = ref([])
      const newInterest = ref('')
  
      const fetchInterests = async () => {
        try {
          const response = await store.dispatch('profile/fetchInterests')
          userInterests.value = response.interests
        } catch (error) {
          console.error('获取兴趣失败:', error)
        }
      }
  
      const addInterest = async () => {
        if (!newInterest.value.trim()) return
        try {
          await store.dispatch('profile/addInterest', newInterest.value)
          await fetchInterests()
          newInterest.value = ''
        } catch (error) {
          console.error('添加兴趣失败:', error)
        }
      }
  
      const removeInterest = async (interest) => {
        try {
          await store.dispatch('profile/removeInterest', interest)
          await fetchInterests()
        } catch (error) {
          console.error('删除兴趣失败:', error)
        }
      }
  
      onMounted(fetchInterests)
  
      return {
        userInterests,
        newInterest,
        addInterest,
        removeInterest
      }
    }
  }
  </script>