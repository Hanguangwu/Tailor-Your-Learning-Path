<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 主要内容区域 -->
    <div class="relative">
      <!-- 背景图片部分保持不变 -->
      <div class="absolute inset-0">
        <img src="@/assets/loolapalloza.jpg" alt="Background" class="w-full h-screen object-cover filter brightness-50">
      </div>

      <!-- 更新内容层 -->
      <div class="relative min-h-screen flex flex-col items-center justify-center text-white px-4">
        <h1 class="text-6xl font-bold mb-6 text-center">
          量身学程——自学指南
          <span class="block text-4xl mt-2">为每个学习者定制学习体验</span>
        </h1>
        <p class="text-xl mb-8 text-center max-w-2xl">
          基于AI驱动的学习平台，利用大语言模型提供个性化课程推荐和学习辅助，帮助用户成为更好的自己。
        </p>

        <!-- 添加特点列表 -->
        <ul class="flex flex-wrap justify-center gap-6 mb-8">
          <li class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            兴趣驱动
          </li>
          <li class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            提升技能
          </li>
          <li class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            职业发展
          </li>
        </ul>

        <div class="space-x-4">
          <router-link to="/dashboard"
            class="inline-block px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition duration-300">
            开始学习
          </router-link>
          <router-link to="/about"
            class="inline-block px-8 py-3 bg-white text-indigo-600 rounded-lg hover:bg-gray-100 transition duration-300">
            了解更多
          </router-link>
        </div>
      </div>
    </div>

    <!-- 平台特色 -->
    <div class="bg-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-center mb-12">为什么选择个性化学习平台？</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">个性化课程推荐</h3>
            <p class="text-gray-600">
              基于AI的智能推荐系统，根据用户行为、兴趣和职业目标推荐合适的课程。通过追踪学习记录和模式，为学习者规划从入门到进阶的学习路径。
            </p>
          </div>

          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">AI学习助手</h3>
            <p class="text-gray-600">
              集成智能学习助手，帮助用户查找课程、解答问题、提供持续学习支持。基于学习历史与用户互动，提供个性化建议和资源。
            </p>
          </div>

          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">资源网站导航</h3>
            <p class="text-gray-600">
              提供全面的资源网站导航，帮助学习者快速找到所需的学习材料和工具。通过精心筛选和分类，确保每个资源的质量和实用性。
            </p>
          </div>

          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">记忆强化工具</h3>
            <p class="text-gray-600">
              采用间隔重复回想策略，通过科学的时间间隔设置和主动回想练习，帮助学习者显著提高记忆的长期保持效果，使学习更加高效。
            </p>
          </div>

          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">智能自测系统</h3>
            <p class="text-gray-600">
              提供自测工具，帮助学习者及时发现知识盲点，评估学习效果。通过即时反馈和个性化建议，指导学习者调整学习策略。
            </p>
          </div>

          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-xl font-semibold mb-4">游戏化系统</h3>
            <p class="text-gray-600">
              结合游戏元素与项目导向学习，通过积分、等级和成就系统激励学习。在趣味化的学习环境中培养问题解决能力和团队协作精神。
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- AI助手介绍 -->
    <div class="bg-indigo-50 py-16">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-6">智能学习助手</h2>
        <p class="text-lg text-gray-700">
          我们的AI助手是您的个性化学习伙伴，旨在提升您的学习体验。通过先进的AI技术，它能够提供实时支持、解答疑问，并基于您的学习风格和进度提供定制化的课程建议。
          无论是课程选择、作业辅导还是补充资源，我们的AI助手都将全程为您提供指导。
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>