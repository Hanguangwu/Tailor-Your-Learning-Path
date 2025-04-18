<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-2xl font-bold mb-6">学习成就系统</h2>

    <!-- 用户积分和等级展示 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold opacity-80">当前积分</h3>
            <p class="text-3xl font-bold">{{ userPoints }}</p>
          </div>
          <div class="text-4xl">
            <i class="fas fa-star"></i>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-r from-blue-500 to-teal-400 rounded-lg p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold opacity-80">学习等级</h3>
            <p class="text-3xl font-bold">{{ userLevel.name }}</p>
          </div>
          <div class="text-4xl">
            <i class="fas fa-trophy"></i>
          </div>
        </div>
        <div class="mt-4">
          <div class="w-full bg-blue-200 bg-opacity-30 rounded-full h-2.5">
            <div class="bg-white h-2.5 rounded-full" :style="{ width: levelProgressPercentage + '%' }"></div>
          </div>
          <div class="flex justify-between text-sm mt-1">
            <span>{{ userPoints }}</span>
            <span>{{ nextLevelPoints }}</span>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-r from-orange-500 to-pink-500 rounded-lg p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold opacity-80">已获成就</h3>
            <p class="text-3xl font-bold">{{ earnedBadges.length }}/{{ badges.length }}</p>
          </div>
          <div class="text-4xl">
            <i class="fas fa-medal"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 成就展示区 -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">成就清单</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="badge in badgeStatus" :key="badge.id"
          class="badge-card relative group cursor-pointer rounded-lg overflow-hidden" @click="showBadgeDetail(badge)">
          <div class="p-4 h-full flex flex-col items-center justify-center text-center" :class="[
              badge.status ? badge.bgColorEarned : 'bg-gray-100',
              badge.status ? '' : 'badge-locked'
            ]">
            <div class="text-4xl mb-2" :class="badge.status ? 'text-white' : 'text-gray-400'">
              <i :class="badge.icon"></i>
            </div>
            <h4 class="font-semibold" :class="badge.status ? 'text-white' : 'text-gray-500'">
              {{ badge.name }}
            </h4>
            <p class="text-sm mt-1" :class="badge.status ? 'text-white opacity-80' : 'text-gray-400'">
              {{ badge.description }}
            </p>
          </div>
          <!-- 完成标记 -->
          <div v-if="badge.status" class="absolute top-2 right-2 bg-green-500 rounded-full p-1">
            <i class="fas fa-check text-white text-xs"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 排行榜 -->
    <!-- 在排行榜标题旁添加刷新按钮 -->
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-xl font-semibold">成就排行榜</h3>
      <button @click="refreshLeaderboard" class="text-blue-500 hover:text-blue-700 flex items-center text-sm">
        <i class="fas fa-sync-alt mr-1"></i> 刷新排行榜
      </button>
    </div>
    <div class="bg-gray-50 rounded-lg p-4">
      <div v-if="leaderboard.length > 0">
        <div v-for="(user, index) in leaderboard" :key="index" class="flex items-center p-3 mb-2 rounded-lg" :class="[
              index === 0 ? 'bg-gradient-to-r from-yellow-100 to-yellow-200' :
                index === 1 ? 'bg-gradient-to-r from-gray-100 to-gray-200' :
                  index === 2 ? 'bg-gradient-to-r from-orange-50 to-orange-100' : 'bg-white',
              isCurrentUser(user) ? 'border-2 border-blue-300' : ''
            ]">
          <div class="flex-shrink-0 mr-4">
            <div :class="[
              'flex items-center justify-center w-10 h-10 rounded-full text-white font-bold',
              index === 0 ? 'bg-yellow-500' :
                index === 1 ? 'bg-gray-500' :
                  index === 2 ? 'bg-orange-400' : 'bg-gray-400'
            ]">
              {{ index + 1 }}
            </div>
          </div>
          <div class="flex-1">
            <h4 class="font-semibold">{{ user.username }}</h4>
            <div class="flex items-center text-sm text-gray-600">
              <span class="mr-2">{{ user.points }} 积分</span>
              <span>{{ user.badgeCount }} 成就</span>
            </div>
          </div>
          <div v-if="isCurrentUser(user)" class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
            我
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4 text-gray-500">
        <div class="animate-pulse">
          <i class="fas fa-spinner fa-spin mr-2"></i>加载排行榜数据...
        </div>
      </div>
    </div>

    <!-- 成就详情弹窗 -->
    <el-dialog v-model="badgeDetailVisible" :title="selectedBadge ? selectedBadge.name : ''" width="30%"
      :show-close="true" :close-on-click-modal="true">
      <div v-if="selectedBadge" class="text-center">
        <div :class="[
              'inline-flex items-center justify-center w-20 h-20 rounded-full mb-4',
              isBadgeEarned(selectedBadge) ? selectedBadge.bgColorEarned : 'bg-gray-200'
            ]">
          <i
            :class="[selectedBadge.icon, 'text-4xl', isBadgeEarned(selectedBadge) ? 'text-white' : 'text-gray-400']"></i>
        </div>
        <p class="mb-4">{{ selectedBadge.description }}</p>
        <div v-if="isBadgeEarned(selectedBadge)" class="text-green-600 font-semibold">
          <i class="fas fa-check-circle mr-1"></i> 已获得
          <p class="text-gray-500 text-sm mt-1">获得时间: {{ formatDate(getBadgeEarnedDate(selectedBadge)) }}</p>
        </div>
        <div v-else class="text-gray-500">
          <i class="fas fa-lock mr-1"></i> 未解锁
          <p class="text-sm mt-1">完成条件: {{ selectedBadge.requirement }}</p>
        </div>
        <div v-if="selectedBadge.points" class="mt-4 text-indigo-600">
          <i class="fas fa-star mr-1"></i> 奖励积分: {{ selectedBadge.points }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'LearningPBL',
  setup() {
    const store = useStore()
    const userPoints = ref(0)
    const earnedBadges = ref([])
    const leaderboard = ref([])
    const badgeDetailVisible = ref(false)
    const selectedBadge = ref(null)

    // 定义所有可能的成就
    const badges = [
      {
        id: 'first_course',
        name: '初出茅庐',
        description: '选择第一门课程',
        icon: 'fas fa-seedling',
        bgColorEarned: 'bg-green-500',
        requirement: '选择一门课程',
        points: 10
      },
      {
        id: 'course_collector_bronze',
        name: '课程收藏家 I',
        description: '选择5门课程',
        icon: 'fas fa-book',
        bgColorEarned: 'bg-amber-500',
        requirement: '选择5门课程',
        points: 20
      },
      {
        id: 'course_collector_silver',
        name: '课程收藏家 II',
        description: '选择10门课程',
        icon: 'fas fa-books',
        bgColorEarned: 'bg-indigo-500',
        requirement: '选择10门课程',
        points: 50
      },
      {
        id: 'course_collector_gold',
        name: '课程收藏家 III',
        description: '选择20门课程',
        icon: 'fas fa-bookmark',
        bgColorEarned: 'bg-purple-600',
        requirement: '选择20门课程',
        points: 100
      },
      {
        id: 'profile_complete',
        name: '完善档案',
        description: '完成个人资料的填写',
        icon: 'fas fa-user-edit',
        bgColorEarned: 'bg-blue-500',
        requirement: '填写完整个人资料',
        points: 15
      },
      {
        id: 'learning_path',
        name: '规划未来',
        description: '生成个人学习路径',
        icon: 'fas fa-route',
        bgColorEarned: 'bg-teal-500',
        requirement: '使用学习路径推荐功能',
        points: 25
      },
      {
        id: 'first_comment',
        name: '初次发声',
        description: '发表第一条评论',
        icon: 'fas fa-comment',
        bgColorEarned: 'bg-yellow-500',
        requirement: '发表一条评论',
        points: 10
      },
      {
        id: 'social_butterfly',
        name: '社交达人',
        description: '发表10条评论',
        icon: 'fas fa-comments',
        bgColorEarned: 'bg-pink-500',
        requirement: '发表10条评论',
        points: 30
      }
    ]

    // 定义等级系统
    const levels = [
      { level: 1, name: '学习新手', minPoints: 0, maxPoints: 50 },
      { level: 2, name: '求知学徒', minPoints: 51, maxPoints: 150 },
      { level: 3, name: '知识探索者', minPoints: 151, maxPoints: 300 },
      { level: 4, name: '学习达人', minPoints: 301, maxPoints: 500 },
      { level: 5, name: '知识大师', minPoints: 501, maxPoints: 800 },
      { level: 6, name: '学术精英', minPoints: 801, maxPoints: 1200 },
      { level: 7, name: '智慧导师', minPoints: 1201, maxPoints: Infinity }
    ]

    // 计算用户当前等级
    const userLevel = computed(() => {
      return levels.find(level =>
        userPoints.value >= level.minPoints && userPoints.value <= level.maxPoints
      ) || levels[0]
    })

    // 计算下一级所需积分
    const nextLevelPoints = computed(() => {
      const currentLevelIndex = levels.findIndex(level => level.level === userLevel.value.level)
      if (currentLevelIndex < levels.length - 1) {
        return levels[currentLevelIndex + 1].minPoints
      }
      return userPoints.value
    })

    // 计算等级进度百分比
    const levelProgressPercentage = computed(() => {
      if (userLevel.value.level === levels[levels.length - 1].level) {
        return 100
      }

      const currentPoints = userPoints.value - userLevel.value.minPoints
      const pointsNeeded = userLevel.value.maxPoints - userLevel.value.minPoints
      return Math.round((currentPoints / pointsNeeded) * 100)
    })

    // 获取当前用户
    const currentUser = computed(() => store.getters['auth/currentUser'])

    // 检查成就是否已获得
    const isBadgeEarned = (badge) => {
      return earnedBadges.value?.some(earned => earned.badgeId === badge.id) || false
    }

    // 获取成就获得日期
    const getBadgeEarnedDate = (badge) => {
      const earned = earnedBadges.value?.find(earned => earned.badgeId === badge.id)
      return earned ? earned.earnedAt : null
    }

    // 获取成就状态的计算属性
    const badgeStatus = computed(() => {
      return badges.map(badge => ({
        ...badge,
        status: isBadgeEarned(badge),
        earnedDate: getBadgeEarnedDate(badge)
      }))
    })

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
    }

    // 显示成就详情
    const showBadgeDetail = (badge) => {
      selectedBadge.value = badge
      badgeDetailVisible.value = true
    }

    // 获取用户成就和积分
    const fetchUserAchievements = async () => {
      try {
        const response = await axios.get('/api/profile/achievements')
        userPoints.value = response.data.points
        earnedBadges.value = response.data.badges
      } catch (error) {
        console.error('获取用户成就失败:', error)
        ElMessage.error('获取用户成就失败')
      }
    }

    // 检查是否为当前用户
    const isCurrentUser = (user) => {
      return currentUser.value && user.userId === currentUser.value._id;
    }

    // 修改获取排行榜数据的方法
    const fetchLeaderboard = async () => {
      try {
        const response = await axios.get('/api/profile/leaderboard');
        if (response.data && Array.isArray(response.data)) {
          leaderboard.value = response.data.map(user => ({
            userId: user._id, // 保存用户ID
            username: user.username,
            points: user.points || 0,
            badgeCount: user.badgeCount || 0
          }));
        } else {
          leaderboard.value = [];
        }
      } catch (error) {
        console.error('获取排行榜失败:', error);
        ElMessage.error('获取排行榜失败');
        leaderboard.value = [];
      }
    }

    // 手动刷新排行榜
    const refreshLeaderboard = async () => {
      try {
        // 先检查成就更新
        await axios.post('/api/profile/check-achievements');
        // 然后刷新排行榜和用户成就
        await fetchLeaderboard();
        await fetchUserAchievements();
        ElMessage.success('排行榜已更新');
      } catch (error) {
        console.error('刷新排行榜失败:', error);
        ElMessage.error('刷新排行榜失败');
      }
    }

    onMounted(() => {
      fetchUserAchievements()
      fetchLeaderboard()

      // 每30秒刷新一次数据
      const refreshInterval = setInterval(() => {
        fetchUserAchievements();
        fetchLeaderboard();
      }, 30000);

      // 组件卸载时清除定时器
      onUnmounted(() => {
        clearInterval(refreshInterval);
      })
    })

    return {
      userPoints,
      badges,
      earnedBadges,
      leaderboard,
      badgeStatus,
      userLevel,
      nextLevelPoints,
      levelProgressPercentage,
      currentUser,
      badgeDetailVisible,
      selectedBadge,
      isBadgeEarned,
      getBadgeEarnedDate,
      formatDate,
      showBadgeDetail,
      isCurrentUser,
      refreshLeaderboard
    }
  }
}
</script>

<style scoped>
.badge-card {
  transition: all 0.3s ease;
}

.badge-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.badge-locked {
  opacity: 0.6;
  filter: grayscale(100%);
}

.aspect-w-1 {
  position: relative;
  padding-bottom: 100%;
}

.aspect-h-1 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
</style>