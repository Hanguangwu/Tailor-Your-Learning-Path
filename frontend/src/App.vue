<template>
  <div class="min-h-screen flex flex-col">
    <Navbar />
    <!-- 添加顶部间距以防止内容被 Navbar 遮挡 -->
    <div class="pt-16 flex-grow">
      <router-view />
    </div>
    <Footer />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  }
}
</script>