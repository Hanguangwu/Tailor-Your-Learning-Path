<template>
  <div class="container mx-auto px-4 py-8 mt-16">
    <h1 class="text-2xl font-bold mb-6">知识自测</h1>
    
    <!-- 文档输入区域 -->
    <div v-if="!questions.length" class="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">上传或输入学习内容</h2>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">选择文档上传</label>
        <input type="file" @change="handleFileUpload" class="border rounded p-2 w-full" accept=".txt,.pdf,.docx,.md" />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">或直接输入内容</label>
        <el-input type="textarea" v-model="documentContent" :rows="8" placeholder="请输入学习内容..." />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">生成题目数量</label>
        <el-input-number v-model="questionCount" :min="1" :max="10" />
      </div>
      
      <el-button type="primary" @click="generateQuestions" :loading="loading" :disabled="!documentContent.trim() && !uploadedFile">
        生成测试题
      </el-button>
    </div>
    
    <!-- 测试题展示区域 -->
    <div v-if="questions.length" class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-xl font-semibold mb-4">自测题目</h2>
      
      <div v-for="(question, qIndex) in questions" :key="qIndex" class="mb-6 p-4 border rounded">
        <div class="font-medium mb-3">{{ qIndex + 1 }}. {{ question.question }}</div>
        
        <div class="ml-4">
          <div v-for="(option, oIndex) in question.options" :key="oIndex" class="mb-2">
            <el-radio 
              v-model="userAnswers[qIndex]" 
              :label="oIndex"
              :disabled="showResults"
            >
              {{ ['A', 'B', 'C', 'D'][oIndex] }}. {{ option }}
            </el-radio>
          </div>
        </div>
        
        <div v-if="showResults" class="mt-3">
          <div v-if="userAnswers[qIndex] === question.correctIndex" class="text-green-600">
            回答正确！
          </div>
          <div v-else class="text-red-600">
            回答错误。正确答案是: {{ ['A', 'B', 'C', 'D'][question.correctIndex] }}
          </div>
          <div class="mt-2 text-gray-700">
            <strong>解析:</strong> {{ question.explanation }}
          </div>
        </div>
      </div>
      
      <div class="flex justify-between mt-6">
        <el-button @click="resetTest">重新开始</el-button>
        <el-button type="primary" @click="submitTest" v-if="!showResults" :disabled="!isAllAnswered">提交答案</el-button>
        <div v-if="showResults" class="text-lg font-semibold">
          得分: {{ score }}/{{ questions.length }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'SelfTest',
  setup() {
    const documentContent = ref('')
    const uploadedFile = ref(null)
    const questionCount = ref(5)
    const loading = ref(false)
    const questions = ref([])
    const userAnswers = ref([])
    const showResults = ref(false)
    const score = ref(0)
    
    const isAllAnswered = computed(() => {
      return userAnswers.value.length === questions.value.length && 
             !userAnswers.value.some(answer => answer === undefined)
    })
    
    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      uploadedFile.value = file
      
      const reader = new FileReader()
      reader.onload = (e) => {
        documentContent.value = e.target.result
      }
      reader.readAsText(file)
    }
    
    const generateQuestions = async () => {
      if (!documentContent.value.trim() && !uploadedFile.value) {
        ElMessage.warning('请输入学习内容或上传文档')
        return
      }
      
      loading.value = true
      
      try {
        const response = await axios.post('/api/self-test/generate', {
          content: documentContent.value,
          count: questionCount.value
        })
        
        questions.value = response.data
        userAnswers.value = new Array(questions.value.length)
        showResults.value = false
        score.value = 0
        
        ElMessage.success('测试题生成成功')
      } catch (error) {
        console.error('生成测试题失败:', error)
        ElMessage.error(error.response?.data?.detail || '生成测试题失败，请重试')
      } finally {
        loading.value = false
      }
    }
    
    const submitTest = () => {
      if (!isAllAnswered.value) {
        ElMessage.warning('请回答所有问题')
        return
      }
      
      score.value = userAnswers.value.reduce((acc, answer, index) => {
        return answer === questions.value[index].correctIndex ? acc + 1 : acc
      }, 0)
      
      showResults.value = true
    }
    
    const resetTest = () => {
      questions.value = []
      userAnswers.value = []
      documentContent.value = ''
      uploadedFile.value = null
      showResults.value = false
      score.value = 0
    }
    
    return {
      documentContent,
      uploadedFile,
      questionCount,
      loading,
      questions,
      userAnswers,
      showResults,
      score,
      isAllAnswered,
      handleFileUpload,
      generateQuestions,
      submitTest,
      resetTest
    }
  }
}
</script>