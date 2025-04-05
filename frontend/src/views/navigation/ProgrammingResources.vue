<template>
  <div>
    <div class="resource-grid">
      <div v-for="website in websites" :key="website._id" class="resource-item">
        <img :src="website.logoUrl" alt="Website Logo" class="resource-logo" />
        <h3 class="text-lg font-medium mt-2">{{ website.name }}</h3>
        <p class="text-gray-600 text-sm mt-1">{{ website.description }}</p>
        <a :href="website.url" target="_blank" class="resource-link">访问网站</a>
      </div>
    </div>
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
    <div v-if="!loading && websites.length === 0" class="text-center py-8 text-gray-500">
      暂无编程相关资源
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from '@/axios'

export default {
  name: 'ProgrammingResources',
  setup() {
    const websites = ref([])
    const loading = ref(true)

    const fetchWebsites = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/websites/category/编程')
        websites.value = response.data
      } catch (error) {
        console.error('获取编程网站数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchWebsites)

    return {
      websites,
      loading
    }
  }
}
</script>

<style scoped>
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.resource-item {
  border: 1px solid #e2e8f0;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.resource-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.resource-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin: 0 auto;
}

.resource-link {
  display: inline-block;
  margin-top: 12px;
  padding: 6px 12px;
  background-color: #4f46e5;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.resource-link:hover {
  background-color: #4338ca;
}
</style>