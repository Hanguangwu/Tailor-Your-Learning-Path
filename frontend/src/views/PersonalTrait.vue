<template>
  <div class="container mx-auto px-4 py-8 mt-16">
    <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-6">
      <h1 class="text-2xl font-bold mb-6 text-center">个人学习偏好设置</h1>
      <p class="text-gray-600 mb-6 text-center">完善您的个人信息，我们将为您推荐更适合的学习内容</p>

      <el-form :model="userProfile" :rules="rules" ref="profileForm" label-position="top">
        <!-- 基本信息 -->
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">基本信息</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="userProfile.age" :min="12" :max="100" />
          </el-form-item>

          <el-form-item label="学历" prop="education">
            <el-select v-model="userProfile.education" placeholder="请选择您的学历">
              <el-option v-for="item in educationOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </div>

        <!-- 职业方向 -->
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">职业方向</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <el-form-item label="行业类别" prop="industry">
            <el-select v-model="userProfile.industry" placeholder="请选择行业类别" filterable allow-create>
              <el-option v-for="item in industryOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="职位名称" prop="jobTitle">
            <el-input v-model="userProfile.jobTitle" placeholder="请输入职位名称" />
          </el-form-item>

          <el-form-item label="职业发展路径" prop="careerPath">
            <el-select v-model="userProfile.careerPath" placeholder="请选择职业发展路径">
              <el-option v-for="item in careerPathOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </div>

        <!-- 兴趣大类 -->
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">兴趣大类</h2>
        <div class="mb-6">
          <el-form-item label="选择您的兴趣领域（可多选）" prop="interests">
            <el-checkbox-group v-model="userProfile.interests">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <el-checkbox v-for="item in interestOptions" :key="item.value" :label="item.value">
                  {{ item.label }}
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </el-form-item>
        </div>

        <!-- 想要掌握的技能 -->
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">想要掌握的技能</h2>
        <div class="mb-6">
          <el-form-item label="技术技能" prop="technicalSkills">
            <el-select v-model="userProfile.technicalSkills" multiple filterable allow-create placeholder="请选择或输入技术技能">
              <el-option v-for="item in technicalSkillOptions" :key="item.value" :label="item.label"
                :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="软技能" prop="softSkills">
            <el-select v-model="userProfile.softSkills" multiple filterable allow-create placeholder="请选择或输入软技能">
              <el-option v-for="item in softSkillOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="特定工具或软件" prop="tools">
            <el-select v-model="userProfile.tools" multiple filterable allow-create placeholder="请选择或输入工具/软件">
              <el-option v-for="item in toolOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </div>

        <!-- 学习目标 -->
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">学习目标</h2>
        <div class="mb-6">
          <el-form-item label="您的学习目标是什么？" prop="learningGoals">
            <el-checkbox-group v-model="userProfile.learningGoals">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <el-checkbox v-for="item in learningGoalOptions" :key="item.value" :label="item.value">
                  {{ item.label }}
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="具体目标描述" prop="goalDescription">
            <el-input type="textarea" v-model="userProfile.goalDescription" placeholder="请描述您的具体学习目标..." :rows="3" />
          </el-form-item>
        </div>

        <!-- 学习方式偏好 -->
        <h2 class="text-xl font-semibold mb-4 border-b pb-2">学习方式偏好</h2>
        <div class="mb-6">
          <el-form-item label="您偏好的学习方式" prop="learningPreferences">
            <el-checkbox-group v-model="userProfile.learningPreferences">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <el-checkbox v-for="item in learningPreferenceOptions" :key="item.value" :label="item.value">
                  {{ item.label }}
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </el-form-item>
        </div>

        <div class="flex justify-center mt-8">
          <el-button type="primary" @click="saveProfile" :loading="loading">保存设置</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

export default {
  name: 'PersonalTrait',
  setup() {
    const store = useStore()
    const router = useRouter()
    const profileForm = ref(null)
    const loading = ref(false)

    // 用户资料数据
    const userProfile = reactive({
      age: null,
      education: '',
      industry: '',
      jobTitle: '',
      careerPath: '',
      interests: [],
      technicalSkills: [],
      softSkills: [],
      tools: [],
      learningGoals: [],
      goalDescription: '',
      learningPreferences: []
    })

    // 表单验证规则
    const rules = {
      age: [
        { type: 'number', required: false, message: '请输入有效年龄', trigger: 'blur' }
      ],
      education: [
        { required: false, message: '请选择学历', trigger: 'change' }
      ],
      industry: [
        { required: false, message: '请选择行业类别', trigger: 'change' }
      ],
      interests: [
        { type: 'array', required: false, message: '请至少选择一个兴趣领域', trigger: 'change' }
      ],
      learningGoals: [
        { type: 'array', required: false, message: '请至少选择一个学习目标', trigger: 'change' }
      ]
    }

    // 选项数据
    const educationOptions = [
      { value: '初中及以下', label: '初中及以下' },
      { value: '高中/中专', label: '高中/中专' },
      { value: '大专', label: '大专' },
      { value: '本科', label: '本科' },
      { value: '硕士', label: '硕士' },
      { value: '博士', label: '博士' }
    ]

    const industryOptions = [
      { value: '科技/IT', label: '科技/IT' },
      { value: '金融/银行', label: '金融/银行' },
      { value: '医疗/健康', label: '医疗/健康' },
      { value: '教育/培训', label: '教育/培训' },
      { value: '艺术/设计', label: '艺术/设计' },
      { value: '媒体/娱乐', label: '媒体/娱乐' },
      { value: '制造/工程', label: '制造/工程' },
      { value: '零售/电商', label: '零售/电商' },
      { value: '咨询/服务', label: '咨询/服务' },
      { value: '其他', label: '其他' }
    ]

    const careerPathOptions = [
      { value: '入门/初级', label: '入门/初级' },
      { value: '中级', label: '中级' },
      { value: '高级/专家', label: '高级/专家' },
      { value: '管理层', label: '管理层' },
      { value: '创业者', label: '创业者' },
      { value: '学生', label: '学生' }
    ]

    const interestOptions = [
      { value: '艺术与设计', label: '艺术与设计' },
      { value: '科学与技术', label: '科学与技术' },
      { value: '商业与经济', label: '商业与经济' },
      { value: '社会科学', label: '社会科学' },
      { value: '健康与医学', label: '健康与医学' },
      { value: '语言与文学', label: '语言与文学' },
      { value: '历史与文化', label: '历史与文化' },
      { value: '音乐与表演', label: '音乐与表演' },
      { value: '体育与健身', label: '体育与健身' },
      { value: '旅游与探索', label: '旅游与探索' }
    ]

    const technicalSkillOptions = [
      { value: '编程/开发', label: '编程/开发' },
      { value: '数据分析', label: '数据分析' },
      { value: '人工智能/机器学习', label: '人工智能/机器学习' },
      { value: '网络安全', label: '网络安全' },
      { value: '云计算', label: '云计算' },
      { value: '设计/UI/UX', label: '设计/UI/UX' },
      { value: '项目管理', label: '项目管理' },
      { value: '数字营销', label: '数字营销' }
    ]

    const softSkillOptions = [
      { value: '沟通能力', label: '沟通能力' },
      { value: '团队协作', label: '团队协作' },
      { value: '领导力', label: '领导力' },
      { value: '问题解决', label: '问题解决' },
      { value: '时间管理', label: '时间管理' },
      { value: '创新思维', label: '创新思维' },
      { value: '情商/人际关系', label: '情商/人际关系' },
      { value: '适应能力', label: '适应能力' }
    ]

    const toolOptions = [
      { value: 'Microsoft Office', label: 'Microsoft Office' },
      { value: 'Adobe Creative Suite', label: 'Adobe Creative Suite' },
      { value: '编程语言', label: '编程语言' },
      { value: '数据库工具', label: '数据库工具' },
      { value: '项目管理工具', label: '项目管理工具' },
      { value: '设计工具', label: '设计工具' },
      { value: '营销工具', label: '营销工具' },
      { value: '协作工具', label: '协作工具' }
    ]

    const learningGoalOptions = [
      { value: '职业提升', label: '职业提升' },
      { value: '获取认证', label: '获取认证' },
      { value: '个人兴趣发展', label: '个人兴趣发展' },
      { value: '考试准备', label: '考试准备' },
      { value: '创业准备', label: '创业准备' },
      { value: '学术研究', label: '学术研究' },
      { value: '技能拓展', label: '技能拓展' },
      { value: '其他', label: '其他' }
    ]

    const learningPreferenceOptions = [
      { value: '线上课程', label: '线上课程' },
      { value: '线下课程', label: '线下课程' },
      { value: '实践项目', label: '实践项目' },
      { value: '理论学习', label: '理论学习' },
      { value: '自主学习', label: '自主学习' },
      { value: '导师指导', label: '导师指导' },
      { value: '小组学习', label: '小组学习' },
      { value: '视频教程', label: '视频教程' },
      { value: '文字教程', label: '文字教程' },
      { value: '互动式学习', label: '互动式学习' }
    ]

    // 加载用户资料
    onMounted(async () => {
      try {
        loading.value = true
        const profileData = await store.dispatch('auth/getUserProfile')
        if (profileData) {
          Object.keys(userProfile).forEach(key => {
            if (profileData[key] !== undefined) {
              userProfile[key] = profileData[key]
            }
          })
        }
        loading.value = false
      } catch (error) {
        console.error('加载用户资料失败:', error)
        ElMessage.error('加载用户资料失败')
        loading.value = false
      }
    })

    const saveProfile = async () => {
      try {
        loading.value = true
        await store.dispatch('auth/updateUserProfile', userProfile)
        ElMessage.success('个人资料保存成功')
        router.push('/dashboard')
        loading.value = false
      } catch (error) {
        console.error('保存用户资料失败:', error)
        ElMessage.error(error.response?.data?.detail || '保存用户资料失败')
        loading.value = false
      }
    }

    return {
      userProfile,
      profileForm,
      loading,
      saveProfile,
      rules,
      educationOptions,
      industryOptions,
      careerPathOptions,
      interestOptions,
      technicalSkillOptions,
      softSkillOptions,
      toolOptions,
      learningGoalOptions,
      learningPreferenceOptions
    }
  }
}
</script>