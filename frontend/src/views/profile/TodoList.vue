<template>
  <div class="h-full">
    <div class="bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">待办事项</h2>
        </div>
      <div class="flex space-x-2">
        <el-button type="primary" @click="showAddDialog">
          <i class="fas fa-plus mr-1"></i> 新增待办
        </el-button>
        <el-button @click="showHistory = !showHistory">
          <i class="fas fa-history mr-1"></i> {{ showHistory ? '当前待办' : '历史记录' }}
        </el-button>
      </div>
    </div>

    <!-- 待办列表 -->
    <div class="space-y-4">
        <template v-if="filteredTodos.length > 0">
          <div v-for="todo in filteredTodos" :key="todo._id"
               class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <el-checkbox 
              :model-value="todo.completed"
              @change="(val) => toggleTodoStatus(todo, val)"
              :disabled="showHistory"
            ></el-checkbox>
            <span class="flex-1 ml-3" :class="{'line-through text-gray-400': todo.completed}">
              {{ todo.content }}
            </span>
          <div class="flex items-center space-x-2 text-sm text-gray-500">
            <span>{{ formatDate(todo.createdAt) }}</span>
            <el-button type="danger" size="small" @click="deleteTodo(todo._id)">
              <i class="fas fa-trash"></i>
            </el-button>
          </div>
        </div>
      </template>
      <div v-else class="text-center text-gray-500 py-8">
        {{ showHistory ? '暂无历史记录' : '暂无待办事项' }}
      </div>
    </div>

    <!-- 新增待办对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="新增待办事项"
      width="30%"
    >
      <el-form @submit.prevent="addTodo">
        <el-form-item>
          <el-input
            v-model="newTodoContent"
            type="textarea"
            :rows="3"
            placeholder="请输入待办事项内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addTodo" :disabled="!newTodoContent.trim()">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
dayjs.extend(utc);
dayjs.extend(timezone);

export default {
  name: 'TodoList',
  setup() {
    const todos = ref([])
    const showHistory = ref(false)
    const addDialogVisible = ref(false)
    const newTodoContent = ref('')

    // 过滤显示当前待办或历史记录
    const filteredTodos = computed(() => {
      return showHistory.value
        ? todos.value.filter(todo => todo.completed)
        : todos.value.filter(todo => !todo.completed)
    })

    // 获取所有待办事项
    const fetchTodos = async () => {
      try {
        const response = await axios.get('/api/profile/todos')
        todos.value = response.data
      } catch (error) {
        console.error('获取待办事项失败:', error)
        ElMessage.error('获取待办事项失败')
      }
    }

    // 添加待办事项
    const addTodo = async () => {
      if (!newTodoContent.value.trim()) return
      
      try {
        const response = await axios.post('/api/profile/todos', {
          content: newTodoContent.value.trim()
        })
        todos.value.unshift(response.data)
        addDialogVisible.value = false
        newTodoContent.value = ''
        ElMessage.success('添加成功')
      } catch (error) {
        console.error('添加待办事项失败:', error)
        ElMessage.error('添加待办事项失败')
      }
    }

    // 修改切换待办事项状态的函数
    const toggleTodoStatus = async (todo, newStatus) => {
      try {
        await axios.put(`/api/profile/todos/${todo._id}`, {
          completed: newStatus,
          content: todo.content // 保持原有内容不变
        })
        todo.completed = newStatus // 更新本地状态
        ElMessage.success(newStatus ? '已完成' : '已恢复')
      } catch (error) {
        console.error('更新待办事项状态失败:', error)
        todo.completed = !newStatus // 恢复原状态
        ElMessage.error('更新状态失败')
      }
    }

    // 删除待办事项
    const deleteTodo = async (todoId) => {
      try {
        await axios.delete(`/api/profile/todos/${todoId}`)
        todos.value = todos.value.filter(todo => todo._id !== todoId)
        ElMessage.success('删除成功')
      } catch (error) {
        console.error('删除待办事项失败:', error)
        ElMessage.error('删除失败')
      }
    }

    // 显示新增对话框
    const showAddDialog = () => {
      addDialogVisible.value = true
      newTodoContent.value = ''
    }

    // 格式化日期
    const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const formatDate = (utcDateString) => {
            if (!utcDateString) return '';
            // 1. 先把字符串解析为UTC时间  
            const utcDate = dayjs.utc(utcDateString);
            // 2. 转换到用户所在时区  
            const customizedTime = utcDate.tz(userTimeZone);
            // 3. 格式化输出  
            return customizedTime.format('YYYY年MM月DD日 HH:mm');
        };

    // 初始化加载数据
    fetchTodos()

    return {
      todos,
      showHistory,
      addDialogVisible,
      newTodoContent,
      filteredTodos,
      showAddDialog,
      addTodo,
      toggleTodoStatus,
      deleteTodo,
      formatDate
    }
  }
}
</script>