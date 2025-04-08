<template>
  <div class="mt-8 mx-4 md:mx-8">
    <h3 class="text-xl font-semibold mb-4">课程评论</h3>

    <!-- 发表评论 -->
    <div class="mb-6">
      <textarea v-model="newComment" rows="3"
        class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder="写下你的想法..."></textarea>
      <button @click="submitComment" class="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        :disabled="!newComment.trim()">
        发表评论
      </button>
    </div>

    <!-- 评论列表 -->
    <div class="space-y-4">
      <div v-for="comment in comments" :key="comment._id" class="bg-gray-50 p-4 rounded-lg">
        <div class="flex justify-between items-start">
          <div>
            <div class="font-medium">{{ comment.username }}</div>
            <div class="text-sm text-gray-500">
              {{ new Date(comment.created_at).toLocaleString() }}
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <button @click="likeComment(comment._id)" 
              :class="['flex items-center space-x-1 px-2 py-1 rounded hover:bg-gray-200',
                comment.liked_by.includes(currentUserId) ? 'text-blue-600' : 'text-gray-500']"
              title="喜欢">
              <i class="fas fa-thumbs-up"></i>
              <span>{{ comment.likes }}</span>
            </button>
            <button @click="dislikeComment(comment._id)" 
              :class="['flex items-center space-x-1 px-2 py-1 rounded hover:bg-gray-200',
                comment.disliked_by.includes(currentUserId) ? 'text-red-600' : 'text-gray-500']"
              title="不喜欢">
              <i class="fas fa-thumbs-down"></i>
              <span>{{ comment.dislikes }}</span>
            </button>
            <!-- 修改删除按钮的条件判断，确保字符串比较 -->
            <button v-if="isCommentOwner(comment)" 
              @click="deleteComment(comment._id)"
              class="text-gray-500 hover:text-red-600 px-2 py-1 rounded hover:bg-gray-200"
              title="删除评论">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        </div>
        <p class="mt-2 text-gray-700">{{ comment.content }}</p>
      </div>
      
      <!-- 无评论时显示 -->
      <div v-if="comments.length === 0" class="text-center py-8 text-gray-500">
        暂无评论，快来发表第一条评论吧！
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import axios from '@/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'CourseComments',
  props: {
    courseId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const store = useStore()
    const comments = ref([])
    const newComment = ref('')
    
    // 从 localStorage 获取用户信息
    const getUserFromLocalStorage = () => {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          return JSON.parse(userStr)
        }
      } catch (e) {
        console.error('解析 localStorage 中的用户信息失败:', e)
      }
      return null
    }
    
    // 使用计算属性获取当前用户，优先从 store 获取，如果没有则从 localStorage 获取
    const currentUser = computed(() => {
      return getUserFromLocalStorage() || store.state.auth.user
    })
    
    // 获取当前用户 ID
    const currentUserId = computed(() => {
      const user = currentUser.value
      return user ? user.id : ''
    })
    
    // 判断评论是否属于当前用户
    const isCommentOwner = (comment) => {
      if (!currentUser.value) {
        console.log('用户未登录')
        return false
      }
      
      // 确保两边都是字符串类型进行比较
      const commentUserId = String(comment.user_id || '')
      const userId = String(currentUserId.value || '')
      
      console.log('评论用户ID:', commentUserId)
      console.log('当前用户ID:', userId)
      
      return commentUserId === userId
    }

    const fetchComments = async () => {
      try {
        const response = await axios.get(`/api/comments/${props.courseId}`)
        comments.value = response.data
        console.log('获取到的评论:', comments.value)
      } catch (error) {
        ElMessage.error('获取评论失败')
        console.error('获取评论失败:', error)
      }
    }

    const submitComment = async () => {
      if (!newComment.value.trim()) return

      try {
        await axios.post(`/api/comments/${props.courseId}`, {
          content: newComment.value.trim()
        })
        ElMessage.success('评论发表成功')
        newComment.value = ''
        await fetchComments()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '发表评论失败')
        console.error('发表评论失败:', error)
      }
    }

    const likeComment = async (commentId) => {
      try {
        await axios.post(`/api/comments/${commentId}/like`)
        await fetchComments()
      } catch (error) {
        ElMessage.error('操作失败')
        console.error('点赞失败:', error)
      }
    }

    const dislikeComment = async (commentId) => {
      try {
        await axios.post(`/api/comments/${commentId}/dislike`)
        await fetchComments()
      } catch (error) {
        ElMessage.error('操作失败')
        console.error('踩失败:', error)
      }
    }

    // 修改删除评论功能，添加错误处理
    const deleteComment = async (commentId) => {
      try {
        // 弹出确认对话框
        await ElMessageBox.confirm(
          '确定要删除这条评论吗？此操作不可撤销。',
          '删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        // 添加超时设置和错误处理
        const response = await axios.delete(`/api/comments/${commentId}`, {
          timeout: 10000,  // 设置超时时间为10秒
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`  // 确保发送认证信息
          }
        })
        
        if (response.status === 200) {
          ElMessage.success('评论已删除')
          await fetchComments()
        } else {
          throw new Error(`删除失败: ${response.status}`)
        }
      } catch (error) {
        if (error === 'cancel') {
          return
        }
        
        // 详细记录错误信息
        console.error('删除评论错误详情:', error)
        console.error('错误响应:', error.response)
        
        // 显示更友好的错误信息
        if (error.response?.status === 403) {
          ElMessage.error('没有权限删除此评论')
        } else if (error.response?.status === 404) {
          ElMessage.error('评论不存在或已被删除')
          await fetchComments()  // 刷新评论列表
        } else {
          ElMessage.error(error.response?.data?.detail || '删除评论失败，请稍后再试')
        }
      }
    }

    onMounted(() => {
      fetchComments()
    })

    return {
      comments,
      newComment,
      currentUserId,
      submitComment,
      likeComment,
      dislikeComment,
      deleteComment,
      isCommentOwner
    }
  }
}
</script>

<style scoped>
/* 添加一些额外的样式 */
.space-y-4 {
  margin-bottom: 2rem;
}

/* 确保按钮有足够的点击区域 */
button {
  min-width: 36px;
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>