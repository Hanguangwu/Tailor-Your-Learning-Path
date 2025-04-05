<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 头部介绍 -->
    <div class="relative py-16 bg-gradient-to-r from-indigo-600 to-blue-500">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center text-white">
          <h1 class="text-4xl font-bold mb-4">关于我们</h1>
          <p class="text-xl max-w-3xl mx-auto">
            我们的学习平台专注于多种学科，特别是计算机科学，但不仅限于此。我们致力于为学习者提供个性化的学习体验，通过AI驱动的智能助手和全面的资源网站导航，帮助学习者提升技能、获得认可和职业发展。
          </p>
        </div>
      </div>
    </div>

    <!-- 使命愿景 -->
    <div class="py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div class="bg-white p-8 rounded-lg shadow-sm">
            <h2 class="text-2xl font-bold mb-4 text-indigo-600">我们的使命</h2>
            <p class="text-gray-600">
              打造最智能、最个性化的学习平台，让每个人都能找到适合自己的学习方式。
              通过AI技术和个性化推荐，我们帮助学习者突破技术障碍，实现职业发展目标。
            </p>
          </div>
          <div class="bg-white p-8 rounded-lg shadow-sm">
            <h2 class="text-2xl font-bold mb-4 text-indigo-600">我们的愿景</h2>
            <p class="text-gray-600">
              成为全球领先的个性化教育平台，让技术学习变得更加轻松、高效。
              我们期望通过技术创新，为每位学习者提供量身定制的学习体验。
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心优势 -->
    <div class="bg-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-center mb-12">我们的核心优势</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-brain text-2xl text-indigo-600"></i>
            </div>
            <h3 class="text-xl font-semibold mb-2">AI驱动学习</h3>
            <p class="text-gray-600">
              采用先进的AI技术，分析学习行为，提供个性化课程推荐和学习路径规划。
            </p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-users text-2xl text-indigo-600"></i>
            </div>
            <h3 class="text-xl font-semibold mb-2">社区互动</h3>
            <p class="text-gray-600">
              建立活跃的学习社区，促进知识分享和经验交流，营造良好的学习氛围。
            </p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-chart-line text-2xl text-indigo-600"></i>
            </div>
            <h3 class="text-xl font-semibold mb-2">自测与间隔重复</h3>
            <p class="text-gray-600">
              通过自测工具和间隔重复回想策略，帮助学习者巩固所学知识，提高学习效率。
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系我们 -->
    <div class="bg-gray-50 py-16">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-8">联系我们</h2>
        <p class="text-lg text-gray-600 mb-8">
          如果您有任何问题或建议，欢迎随时与我们联系。我们期待听到您的声音！
        </p>
        <div class="flex justify-center space-x-6">
          <a href="mailto:contact@example.com" class="text-indigo-600 hover:text-indigo-800">
            <i class="fas fa-envelope mr-2"></i>
            邮件联系
          </a>
          <a href="#" class="text-indigo-600 hover:text-indigo-800">
            <i class="fab fa-github mr-2"></i>
            GitHub
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>