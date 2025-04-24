<template>
    <div class="h-full">
        <div class="bg-white shadow rounded-lg p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold">成就日记</h2>
                <div class="flex space-x-2">
                    <el-button type="primary" @click="showAddDialog">
                        <i class="fas fa-feather-alt mr-1"></i> 记录新成就
                    </el-button>
                </div>
            </div>

            <!-- 成就日记列表 -->
            <div class="space-y-6">
                <template v-if="diaries.length > 0">
                    <div v-for="diary in diaries" :key="diary._id"
                        class="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-6 hover:shadow-lg transition-shadow">
                        <div class="flex justify-between items-start">
                            <h3 class="text-xl font-semibold text-indigo-700">{{ diary.title }}</h3>
                            <div class="flex items-center space-x-2">
                                <span class="text-sm text-gray-500">{{ formatDate(diary.createdAt) }}</span>
                                <el-button type="danger" size="small" @click="deleteDiary(diary._id)">
                                    <i class="fas fa-trash"></i>
                                </el-button>
                            </div>
                        </div>

                        <div class="mt-4 text-gray-600 whitespace-pre-line">{{ diary.content }}</div>

                        <div class="mt-4 flex flex-wrap gap-2">
                            <span v-for="tag in diary.tags" :key="tag"
                                class="px-3 py-1 bg-indigo-100 text-indigo-600 rounded-full text-sm">
                                #{{ tag }}
                            </span>
                        </div>
                    </div>
                </template>
                <div v-else class="text-center text-gray-500 py-8">
                    暂无成就记录，开始记录你的第一个成就吧！
                </div>
            </div>

            <!-- 新增成就日记对话框 -->
            <el-dialog v-model="addDialogVisible" title="记录新成就" width="50%">
                <el-form @submit.prevent="addDiary" :model="newDiary" label-position="top">
                    <el-form-item label="成就标题">
                        <el-input v-model="newDiary.title" placeholder="为你的成就取个标题"></el-input>
                    </el-form-item>

                    <el-form-item label="成就内容">
                        <el-input v-model="newDiary.content" type="textarea" :rows="6"
                            placeholder="详细描述你的成就故事..."></el-input>
                    </el-form-item>

                    <el-form-item label="标签">
                        <el-select v-model="newDiary.tags" multiple filterable allow-create default-first-option
                            placeholder="选择或创建标签">
                            <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag"></el-option>
                        </el-select>
                    </el-form-item>
                </el-form>
                <template #footer>
                    <span class="dialog-footer">
                        <el-button @click="addDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="addDiary" :disabled="!isValidDiary">
                            保存
                        </el-button>
                    </span>
                </template>
            </el-dialog>
        </div>
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
    name: 'AchievementDiary',
    setup() {
        const diaries = ref([])
        const addDialogVisible = ref(false)
        const newDiary = ref({
            title: '',
            content: '',
            tags: []
        })

        const commonTags = [
            '学习进步', '技能提升', '项目完成', '考试通过',
            '证书获取', '知识分享', '个人突破', '团队合作'
        ]

        const isValidDiary = computed(() => {
            return newDiary.value.title.trim() && newDiary.value.content.trim()
        })

        // 获取所有成就日记
        const fetchDiaries = async () => {
            try {
                const response = await axios.get('/api/profile/achievement-diaries')
                diaries.value = response.data
            } catch (error) {
                console.error('获取成就日记失败:', error)
                ElMessage.error('获取成就日记失败')
            }
        }

        // 添加成就日记
        const addDiary = async () => {
            if (!isValidDiary.value) return

            try {
                const response = await axios.post('/api/profile/achievement-diaries', {
                    title: newDiary.value.title.trim(),
                    content: newDiary.value.content.trim(),
                    tags: newDiary.value.tags
                })
                diaries.value.unshift(response.data)
                addDialogVisible.value = false
                resetNewDiary()
                ElMessage.success('成就记录添加成功')
            } catch (error) {
                console.error('添加成就日记失败:', error)
                ElMessage.error('添加失败')
            }
        }

        // 删除成就日记
        const deleteDiary = async (diaryId) => {
            try {
                await axios.delete(`/api/profile/achievement-diaries/${diaryId}`)
                diaries.value = diaries.value.filter(diary => diary._id !== diaryId)
                ElMessage.success('删除成功')
            } catch (error) {
                console.error('删除成就日记失败:', error)
                ElMessage.error('删除失败')
            }
        }

        // 重置表单
        const resetNewDiary = () => {
            newDiary.value = {
                title: '',
                content: '',
                tags: []
            }
        }

        // 显示新增对话框
        const showAddDialog = () => {
            addDialogVisible.value = true
            resetNewDiary()
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
        fetchDiaries()

        return {
            diaries,
            addDialogVisible,
            newDiary,
            commonTags,
            isValidDiary,
            showAddDialog,
            addDiary,
            deleteDiary,
            formatDate
        }
    }
}
</script>