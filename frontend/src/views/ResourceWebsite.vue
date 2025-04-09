<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row">
      <!-- 侧边栏导航 -->
      <div class="sidebar bg-gray-100 p-4 rounded-lg mb-4 md:mb-0 md:mr-4 md:w-64">
        <h2 class="text-xl font-bold mb-4">仙人指路</h2>
        <ul class="space-y-2">
          <li>
            <router-link to="/websites/nav" class="block p-2 hover:bg-gray-200 rounded">
              <i class='bx bx-code-alt mr-2'></i>导航网站
            </router-link>
          </li>
          <li>
            <router-link to="/websites/study" class="block p-2 hover:bg-gray-200 rounded">
              <i class='bx bx-code-alt mr-2'></i>学习指北
            </router-link>
          </li>
          <li>
            <router-link to="/websites/programming" class="block p-2 hover:bg-gray-200 rounded">
              <i class='bx bx-code-alt mr-2'></i>编程工具
            </router-link>
          </li>
          <li>
            <router-link to="/websites/ai-tools" class="block p-2 hover:bg-gray-200 rounded">
              <i class='bx bx-brain mr-2'></i>AI 工具
            </router-link>
          </li>
          <li>
            <router-link to="/websites/practical-tools" class="block p-2 hover:bg-gray-200 rounded">
              <i class='bx bx-wrench mr-2'></i>普通实用工具
            </router-link>
          </li>
        </ul>
      </div>

      <!-- 主内容区域 -->
      <div class="flex-1">
        <h1 class="text-2xl font-bold mb-6">网站资源清单</h1>
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'ResourceWebsite'
}
</script>

<style scoped>
.container {
  min-height: calc(100vh - 120px); /* 减去导航栏和页脚的高度 */
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
  }
}
</style>