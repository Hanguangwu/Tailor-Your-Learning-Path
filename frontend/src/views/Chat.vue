<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 模型切换 -->
    <el-select v-model="currentModel" :key="selectKey" placeholder="选择模型" class="mb-4">
      <el-option v-for="model in models" :key="model.id" :label="model.name" :value="model"
        :disabled="!model.available">
        <span>{{ model.name }}</span>
        <span v-if="!model.available" class="text-xs text-gray-500">(即将推出)</span>
      </el-option>
    </el-select>
    
    <!-- 显示当前选择的模型 -->
    <div class="mb-4 text-sm text-gray-600">
      当前使用模型: {{ currentModel.name }}
    </div>

    <!-- 聊天输入框 -->
    <div class="bg-white rounded-lg shadow-md overflow-hidden mb-4">
      <div class="bg-gray-100 px-4 py-3 flex justify-between items-center">
        <el-input v-model="userInput" type="textarea" :rows="3" placeholder="输入您的问题..."
          @keyup.enter.ctrl="sendMessage" />
        <el-button @click="sendMessage" :disabled="loading || !userInput.trim()" type="primary">
          发送
        </el-button>
      </div>
    </div>

    <!-- 聊天记录显示 -->
    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-4" ref="chatContainer">
        <div v-for="(message, index) in messages" :key="index" class="mb-4">
          <div :class="[
            'max-w-3xl p-4 rounded-lg',
            message.role === 'user'
              ? 'bg-indigo-100 ml-auto'
              : 'bg-white shadow'
          ]">
            <div class="flex items-start">
              <!-- 用户消息 -->
              <div v-if="message.role === 'user'" class="flex-grow whitespace-pre-wrap">
                {{ message.content }}
              </div>
              
              <!-- AI回复 -->
              <div v-else class="w-full">
                <div class="flex justify-between items-start mb-2">
                  <div class="text-sm text-gray-500">AI回复</div>
                  <div class="flex space-x-2">
                    <el-button type="text" size="small" @click="copyMessage(message.content)">
                      <i class="el-icon-document-copy"></i> 复制
                    </el-button>
                    <el-button type="text" size="small" @click="regenerateMessage(index)" :disabled="loading">
                      <i class="el-icon-refresh"></i> 重新生成
                    </el-button>
                  </div>
                </div>
                <div class="markdown-body" v-html="renderMarkdown(message.content)"></div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="loading" class="flex items-center space-x-2 text-gray-500">
          <span>AI思考中</span>
          <div class="loading-dots">...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'

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
    const selectKey = ref(0)
    const lastUserMessage = ref('')

    const renderMarkdown = (text) => {
      try {
        return marked(text)
      } catch (error) {
        console.error('Markdown渲染错误:', error)
        return text
      }
    }

    const copyMessage = (text) => {
      navigator.clipboard.writeText(text)
        .then(() => {
          ElMessage.success('已复制到剪贴板')
        })
        .catch(err => {
          console.error('复制失败:', err)
          ElMessage.error('复制失败')
        })
    }

    const regenerateMessage = async (index) => {
      if (loading.value) return
      
      // 找到最后一条用户消息
      const userMessageIndex = messages.value.findIndex(m => m.role === 'user' && m.content === lastUserMessage.value)
      
      if (userMessageIndex === -1) {
        ElMessage.warning('无法找到对应的用户消息')
        return
      }
      
      // 移除当前AI回复
      messages.value.splice(index, 1)
      
      loading.value = true
      
      try {
        const response = await axios.post('/api/chat/sendMessage', {
          message: lastUserMessage.value,
          model: currentModel.value.id
        })

        if (response.data && response.data.response) {
          messages.value.push({
            role: 'assistant',
            content: response.data.response
          })
        } else {
          throw new Error('Invalid response format')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '重新生成回复失败')
        console.error('重新生成回复失败:', error)
      } finally {
        loading.value = false
        scrollToBottom()
      }
    }

    const handleSelect = () => {
      selectKey.value += 1
    }

    const sendMessage = async () => {
      if (loading.value || !userInput.value.trim()) return

      if (currentModel.value.id === 'gpt-4' && gpt4UsageCount.value >= 3) {
        ElMessage.warning('GPT-4 每天限制使用3次，请明天再试')
        return
      }

      const userMessage = userInput.value.trim()
      lastUserMessage.value = userMessage // 保存最后一条用户消息
      messages.value.push({ role: 'user', content: userMessage })
      userInput.value = ''
      loading.value = true

      try {
        const response = await axios.post('/api/chat/sendMessage', {
          message: userMessage,
          model: currentModel.value.id
        })

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

    const scrollToBottom = async () => {
      await nextTick()
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    }

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
      selectKey,
      handleSelect,
      sendMessage,
      copyMessage,
      regenerateMessage,
      renderMarkdown
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

/* Markdown样式 */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  word-wrap: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 {
  font-size: 2em;
}

.markdown-body h2 {
  font-size: 1.5em;
}

.markdown-body h3 {
  font-size: 1.25em;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
}

.markdown-body pre code {
  padding: 0;
  margin: 0;
  font-size: 100%;
  background-color: transparent;
}

.markdown-body blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
}

.markdown-body table {
  display: block;
  width: 100%;
  overflow: auto;
  border-spacing: 0;
  border-collapse: collapse;
}

.markdown-body table th,
.markdown-body table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body table tr {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-body table tr:nth-child(2n) {
  background-color: #f6f8fa;
}
</style>
