<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4">
    <div class="max-w-lg w-full text-center">
      <h1 class="text-9xl font-bold text-indigo-600 mb-4">404</h1>
      <p class="text-2xl text-gray-700 mb-8">页面未找到</p>
      <router-link to="/home"
        class="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition duration-300">
        返回首页
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>