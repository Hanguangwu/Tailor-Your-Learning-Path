<template>
  <div class="mt-8">
    <h3 class="text-xl font-semibold mb-4">课程评论</h3>
    
    <!-- 发表评论 -->
    <div class="mb-6">
      <textarea
        v-model="newComment"
        rows="3"
        class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder="写下你的想法..."
      ></textarea>
      <button
        @click="submitComment"
        class="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        :disabled="!newComment.trim()"
      >
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
            <button 
              @click="likeComment(comment._id)"
              :class="['flex items-center space-x-1', 
                comment.liked_by.includes(currentUserId) ? 'text-blue-600' : 'text-gray-500']"
            >
              <i class="el-icon-thumb"></i>
              <span>{{ comment.likes }}</span>
            </button>
            <button 
              @click="dislikeComment(comment._id)"
              :class="['flex items-center space-x-1', 
                comment.disliked_by.includes(currentUserId) ? 'text-red-600' : 'text-gray-500']"
            >
              <i class="el-icon-thumb" style="transform: rotate(180deg)"></i>
              <span>{{ comment.dislikes }}</span>
            </button>
          </div>
        </div>
        <p class="mt-2 text-gray-700">{{ comment.content }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

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
    const currentUserId = store.state.auth.user?._id

    const fetchComments = async () => {
      try {
        const response = await axios.get(`/api/comments/${props.courseId}`)
        comments.value = response.data
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

    onMounted(fetchComments)

    return {
      comments,
      newComment,
      currentUserId,
      submitComment,
      likeComment,
      dislikeComment
    }
  }
}
</script>