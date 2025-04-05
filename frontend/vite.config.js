import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// 获取环境变量
const backendUrl = process.env.BACKEND_BASE_URL || 'http://localhost:3000'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,  // 前端使用不同的端口
    proxy: {
      '/api': {
        target: backendUrl,  // 使用环境变量中的后端地址
        changeOrigin: true,
        secure: false,
        ws: true,
        rewrite: (path) => path
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})