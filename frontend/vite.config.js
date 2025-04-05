import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  // 获取后端URL，优先使用环境变量
  const backendUrl = env.VITE_BACKEND_BASE_URL || 'http://localhost:3000'
  
  return {
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
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false,
      // 优化构建
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'vuex', 'axios'],
            ui: ['element-plus']
          }
        }
      }
    }
  }
})