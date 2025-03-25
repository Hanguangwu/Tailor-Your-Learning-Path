<template>
  <div class="flex h-screen bg-gray-100">
    <!-- 左侧模型选择栏 -->
    <div class="w-64 bg-white shadow-lg p-4">
      <h2 class="text-lg font-semibold mb-4">选择模型</h2>
      <div class="space-y-2">
        <button v-for="model in models" :key="model.id" @click="selectModel(model)" :class="[
          'w-full p-2 rounded text-left',
          currentModel.id === model.id
            ? 'bg-indigo-100 text-indigo-700'
            : 'hover:bg-gray-100'
        ]">
          <div class="flex items-center">
            <span class="flex-grow">{{ model.name }}</span>
            <span v-if="!model.available" class="text-xs text-gray-500">(即将推出)</span>
          </div>
        </button>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="flex-1 flex flex-col">
      <!-- 聊天记录 -->
      <div class="flex-1 p-4 overflow-y-auto" ref="chatContainer">
        <div v-for="(message, index) in messages" :key="index" class="mb-4">
          <div :class="[
          'max-w-3xl p-4 rounded-lg',
          message.role === 'user'
            ? 'bg-indigo-100 ml-auto'
            : 'bg-white shadow'
        ]">
            <div class="flex items-start">
              <div class="flex-grow whitespace-pre-wrap">{{ message.content }}</div>
            </div>
          </div>
        </div>
        <div v-if="loading" class="flex items-center space-x-2 text-gray-500">
          <span>AI思考中</span>
          <div class="loading-dots">...</div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="p-4 bg-white border-t">
        <div class="flex space-x-4">
          <el-input v-model="userInput" type="textarea" :rows="3" placeholder="输入您的问题..."
            @keyup.enter.ctrl="sendMessage" />
          <button @click="sendMessage" :disabled="loading || !userInput.trim()"
            class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
            发送
          </button>
        </div>
        <div class="text-xs text-gray-500 mt-2">
          按 Ctrl + Enter 快速发送
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'Chat',
  setup() {
    const models = [
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5', available: true },
      { id: 'gpt-4', name: 'GPT-4', available: true, dailyLimit: 3 },
      { id: 'gpt-4o-mini', name: 'GPT-4o Mini', available: true },
    ]

    const currentModel = ref(models[0])
    const messages = ref([])
    const userInput = ref('')
    const loading = ref(false)
    const chatContainer = ref(null)
    const gpt4UsageCount = ref(0)

    const selectModel = (model) => {
      if (model.id === 'gpt-4' && gpt4UsageCount.value >= 3) {
        ElMessage.warning('GPT-4 每天限制使用3次，请明天再试')
        return
      }
      currentModel.value = model
    }

    const scrollToBottom = async () => {
      await nextTick()
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    }

    const sendMessage = async () => {
      if (loading.value || !userInput.value.trim()) return

      if (currentModel.value.id === 'gpt-4' && gpt4UsageCount.value >= 3) {
        ElMessage.warning('GPT-4 每天限制使用3次，请明天再试')
        return
      }

      const userMessage = userInput.value.trim()
      messages.value.push({ role: 'user', content: userMessage })
      userInput.value = ''
      loading.value = true

      try {
        console.log('Sending message:', {
          message: userMessage,
          model: currentModel.value.id
        })

        const response = await axios.post('/api/chat', {
          message: userMessage,
          model: currentModel.value.id
        })

        console.log('Response:', response.data)

        if (response.data && response.data.response) {
          messages.value.push({
            role: 'assistant',
            content: response.data.response
          })

          if (currentModel.value.id === 'gpt-4') {
            gpt4UsageCount.value++
          }
        } else {
          throw new Error('Invalid response format')
        }
      } catch (error) {
        messages.value.pop() // 移除用户消息
        ElMessage.error(error.response?.data?.detail || '发送消息失败，请重试')
        console.error('发送消息失败:', error)
      } finally {
        loading.value = false
        scrollToBottom()
      }
    }

    // 每天重置 GPT-4 使用次数
    const resetGPT4Usage = () => {
      const now = new Date()
      const tomorrow = new Date(now)
      tomorrow.setDate(tomorrow.getDate() + 1)
      tomorrow.setHours(0, 0, 0, 0)

      const timeUntilReset = tomorrow - now
      setTimeout(() => {
        gpt4UsageCount.value = 0
        resetGPT4Usage()
      }, timeUntilReset)
    }

    onMounted(() => {
      userInput.value = ''
      messages.value = []
      resetGPT4Usage()
    })

    return {
      models,
      currentModel,
      messages,
      userInput,
      loading,
      chatContainer,
      selectModel,
      sendMessage
    }
  }
}
</script>

<style scoped>
.loading-dots {
  animation: loading 1.5s infinite;
}

@keyframes loading {

  0%,
  20% {
    content: '.';
  }

  40% {
    content: '..';
  }

  60% {
    content: '...';
  }

  80%,
  100% {
    content: '';
  }
}
</style>