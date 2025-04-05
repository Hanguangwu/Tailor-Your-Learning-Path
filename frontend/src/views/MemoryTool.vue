<template>
  <div class="min-h-screen bg-gray-50 pt-24"> <!-- 将 pt-16 修改为 pt-24 以避免遮挡 -->
    <!-- 顶部标题 -->
    <div class="bg-white shadow-md z-10 mb-6"> <!-- 移除 fixed 属性 -->
      <div class="container mx-auto py-4">
        <h2 class="text-2xl font-bold text-center text-indigo-600">记忆工具——背个X啊</h2>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="container mx-auto px-4 py-8 max-w-5xl">
      <!-- 设置区域 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <!-- 设置选项 -->
        <div class="flex flex-wrap justify-center items-center gap-6 mb-6">
          <div class="flex items-center">
            <label for="maskChar" class="mr-2 text-gray-700 font-medium">隔字符：</label>
            <input type="text" id="maskChar" v-model="maskChar" placeholder="X"
              class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-16 text-center">
          </div>
          
          <div class="flex items-center">
            <label for="interval" class="mr-2 text-gray-700 font-medium">间隔数：</label>
            <select id="interval" v-model="interval"
              class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
              <option value="6">6</option>
              <option value="random">随机</option>
            </select>
          </div>
          
          <div class="flex items-center">
            <label for="fontSize" class="mr-2 text-gray-700 font-medium">字体大小：</label>
            <select id="fontSize" v-model="fontSize"
              class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="14">14</option>
              <option value="17">17</option>
              <option value="20">20</option>
              <option value="23">23</option>
              <option value="26">26</option>
              <option value="29">29</option>
              <option value="32">32</option>
              <option value="35">35</option>
              <option value="38">38</option>
            </select>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-wrap justify-center gap-3 mb-4">
          <button @click="processText('chinese')" 
            class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-md transition-colors">
            中文
          </button>
          <button @click="processText('english')" 
            class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors">
            英文句子
          </button>
          <button @click="processText('japanese')" 
            class="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-md transition-colors">
            日语
          </button>
          <button @click="processText('word')" 
            class="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-md transition-colors">
            英文单词
          </button>
          <button @click="loadHistory" 
            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-md transition-colors">
            历史记录
          </button>
          <button @click="clearText" 
            class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors">
            清空
          </button>
        </div>
      </div>

      <!-- 文本区域 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 输入区域 -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="bg-gray-100 px-4 py-3 flex justify-between items-center">
            <input type="file" @change="handleFileUpload" class="text-sm text-gray-700" />
            <button @click="saveToDatabase" 
              class="px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-sm rounded transition-colors">
              保存
            </button>
          </div>
          <div class="p-4">
            <textarea v-model="text" placeholder="需要背诵的文本粘贴到这里" 
              class="w-full h-64 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"></textarea>
          </div>
        </div>

        <!-- 输出区域 -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="bg-gray-100 px-4 py-3 flex justify-end">
            <button @click="fullScreen" 
              class="px-3 py-1 bg-indigo-500 hover:bg-indigo-600 text-white text-sm rounded transition-colors">
              全屏
            </button>
          </div>
          <div class="p-4">
            <div class="w-full h-64 p-3 border border-gray-300 rounded-md overflow-auto" 
              :style="{ fontSize: fontSize + 'px' }">
              {{ processedText }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史记录弹窗 -->
    <div v-if="showHistoryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4">
        <div class="flex justify-between items-center px-6 py-4 border-b">
          <h3 class="text-lg font-medium text-gray-900">历史记录</h3>
          <button @click="showHistoryModal = false" class="text-gray-400 hover:text-gray-500">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="px-6 py-4 max-h-96 overflow-y-auto">
          <div v-if="historyDocuments.length === 0" class="text-center py-8 text-gray-500">
            暂无历史记录
          </div>
          <div v-else class="divide-y divide-gray-200">
            <div v-for="(doc, index) in historyDocuments" :key="index" 
              class="py-3 hover:bg-gray-50 cursor-pointer flex justify-between items-center">
              <div class="flex-1" @click="loadDocument(doc)">
                <div class="text-sm text-gray-900 truncate">{{ doc.text.substring(0, 50) }}{{ doc.text.length > 50 ? '...' : '' }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ new Date(doc.createdAt).toLocaleString() }}</div>
              </div>
              <button @click.stop="deleteDocument(doc.id)" class="text-red-500 hover:text-red-700">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-50 rounded-b-lg text-right">
          <button @click="showHistoryModal = false" 
            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-md transition-colors">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 全屏显示 -->
    <div v-if="isFullScreen" 
      class="fixed inset-0 bg-white z-50 flex items-center justify-center p-8 overflow-auto"
      @click="exitFullScreen">
      <div class="max-w-4xl mx-auto" :style="{ fontSize: fontSize + 'px' }">
        {{ processedText }}
      </div>
    </div>

    <!-- 使用方法和效果说明 -->
    <div class="bg-gray-100 py-8">
      <div class="container mx-auto px-4">
        <h3 class="text-xl font-bold text-center text-indigo-600 mb-4">使用方法和效果</h3>
        <p class="text-gray-700 text-center">
          记忆工具通过间隔重复回想策略，帮助学习者巩固所学知识，提高学习效率。用户可以选择不同的语言模式和间隔设置，生成适合自己的记忆文本。通过定期使用该工具，可以显著提升信息的长期记忆效果。
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'MemoryTool',
  data() {
    return {
      text: '',
      processedText: '',
      maskChar: 'X',
      interval: 3,
      fontSize: 20,
      isFullScreen: false,
      showHistoryModal: false,
      currentMode: 'chinese' // 默认中文模式
    }
  },
  computed: {
    ...mapGetters('documents', [
      'allDocuments',
      'isLoading',
      'hasError',
      'errorMessage'
    ]),
    historyDocuments() {
      return this.allDocuments
    }
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.text = e.target.result
      }
      reader.readAsText(file)
    },
    
    processText(mode) {
      if (!this.text.trim()) {
        ElMessage.warning('请先输入或上传文本')
        return
      }
      
      this.currentMode = mode || this.currentMode
      
      // 根据不同模式处理文本
      switch (this.currentMode) {
        case 'chinese':
          this.processChinese()
          break
        case 'english':
          this.processEnglish()
          break
        case 'japanese':
          this.processJapanese()
          break
        case 'word':
          this.processWord()
          break
        default:
          this.processChinese()
      }
    },
    
    processChinese() {
      const chars = this.text.split('')
      let result = ''
      
      for (let i = 0; i < chars.length; i++) {
        if (this.interval === 'random') {
          // 随机间隔
          if (Math.random() > 0.7) {
            result += this.maskChar
          } else {
            result += chars[i]
          }
        } else {
          // 固定间隔
          if ((i + 1) % parseInt(this.interval) === 0) {
            result += this.maskChar
          } else {
            result += chars[i]
          }
        }
      }
      
      this.processedText = result
    },
    
    processEnglish() {
      // 英语处理逻辑，可以按单词处理
      const words = this.text.split(' ')
      let result = []
      
      for (let i = 0; i < words.length; i++) {
        if (this.interval === 'random') {
          if (Math.random() > 0.7) {
            result.push(this.maskChar.repeat(words[i].length))
          } else {
            result.push(words[i])
          }
        } else {
          if ((i + 1) % parseInt(this.interval) === 0) {
            result.push(this.maskChar.repeat(words[i].length))
          } else {
            result.push(words[i])
          }
        }
      }
      
      this.processedText = result.join(' ')
    },
    
    processJapanese() {
      // 日语处理逻辑，类似中文
      this.processChinese()
    },
    
    processWord() {
      // 单词处理逻辑
      const words = this.text.split(/\s+/)
      let result = []
      
      for (let i = 0; i < words.length; i++) {
        const word = words[i]
        if (word.length > 2) {
          // 保留首尾字母，中间用遮罩
          result.push(word[0] + this.maskChar.repeat(word.length - 2) + word[word.length - 1])
        } else {
          result.push(word)
        }
      }
      
      this.processedText = result.join(' ')
    },
    
    clearText() {
      this.text = ''
      this.processedText = ''
      ElMessage.success('文本已清空')
    },
    
    async saveToDatabase() {
      if (!this.text.trim()) {
        ElMessage.warning('请先输入或上传文本')
        return
      }

      const token = this.$store.state.auth.token
      if (!token) {  
        ElMessage.warning('请先登录')
        return
      }  
          
      try {
        const response = await this.$store.dispatch('documents/saveDocument', { 
          text: this.text,
          createdAt: new Date()
        })
        ElMessage.success('文档保存成功')
      } catch (error) {
        console.error('保存文档失败:', error)
        ElMessage.error(error.response?.data?.detail || '保存失败，请稍后重试')
      }
    },
    
    async loadHistory() {
      this.showHistoryModal = true
      try {
        await this.$store.dispatch('documents/fetchDocuments')
      } catch (error) {
        console.error('获取历史记录失败:', error)
        ElMessage.error('获取历史记录失败，请稍后重试')
      }
    },
    
    loadDocument(doc) {
      this.text = doc.text
      this.showHistoryModal = false
      this.processText()
      ElMessage.success('文档加载成功')
    },
    
    async deleteDocument(documentId) {
      try {
        await this.$store.dispatch('documents/deleteDocument', documentId)
        ElMessage.success('文档删除成功')
      } catch (error) {
        console.error('删除文档失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    },
    
    fullScreen() {
      if (!this.processedText) {
        ElMessage.warning('请先生成记忆文本')
        return
      }
      this.isFullScreen = true
    },
    
    exitFullScreen() {
      this.isFullScreen = false
    }
  }
}
</script>