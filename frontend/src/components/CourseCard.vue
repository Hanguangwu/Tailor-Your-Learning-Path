<template>
  <div class="bg-white rounded-lg shadow p-8">
    <div class="flex items-center mb-6">
      <img :src="course.course_logo_url || '/frontend/src/assets/logo.png'" :alt="course.course_name"
        class="w-32 h-32 object-cover rounded-lg mr-6">
      <div>
        <h3 class="text-xl font-semibold mb-2">{{ course.course_name }}</h3>
        <p class="text-sm text-gray-500">{{ course.category }}</p>
      </div>
    </div>
    
    <p class="text-gray-600 mb-6 line-clamp-2 text-base">{{ course.description }}</p>
    
    <div class="flex items-center justify-between">
      <div class="flex space-x-2">
        <span class="px-2 py-1 text-xs rounded-full" 
              :class="difficultyClass">
          {{ course.difficulty }}
        </span>
        <span class="text-sm text-gray-500">
          已选人数 {{ course.enrollment_count || 0 }}
        </span>
      </div>
      
      <div class="flex space-x-2">
        <!-- 添加查看详情按钮 -->
        <button
          @click="viewDetail"
          class="text-sm text-indigo-600 hover:text-indigo-800"
        >
          查看详情
        </button>
        <button
          v-if="!course.is_selected"
          @click="$emit('select', course._id)"
          class="text-sm text-green-600 hover:text-green-800"
        >
          选择课程
        </button>
        <span v-else class="text-sm text-gray-500">
          已选
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'CourseCard',
  props: {
    course: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const router = useRouter()

    const difficultyClass = computed(() => {
      const classes = {
        '入门': 'bg-green-100 text-green-800',
        '中级': 'bg-yellow-100 text-yellow-800',
        '高级': 'bg-red-100 text-red-800'
      }
      return classes[props.course.difficulty] || 'bg-gray-100 text-gray-800'
    })

    // 添加查看详情方法
    const viewDetail = () => {
      router.push(`/courses/${props.course._id}`)
    }

    return {
      difficultyClass,
      viewDetail
    }
  }
}
</script>

<style>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>