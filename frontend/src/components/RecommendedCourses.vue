<template>
  <div class="w-full">
    <h2 class="text-2xl font-bold mb-4">推荐课程</h2>
    <div class="relative">
      <swiper
        :modules="[SwiperAutoplay, SwiperPagination, SwiperNavigation]"
        :slides-per-view="3"
        :space-between="30"
        :autoplay="{
          delay: 3000,
          disableOnInteraction: false,
        }"
        :pagination="{ clickable: true }"
        :navigation="true"
        class="mySwiper"
      >
        <swiper-slide v-for="course in recommendedCourses" :key="course._id">
          <CourseCard :course="course" @select="handleCourseSelect" />
        </swiper-slide>
      </swiper>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, Pagination, Navigation } from 'swiper'
import 'swiper/css'
import 'swiper/css/pagination'
import 'swiper/css/navigation'
import CourseCard from './CourseCard.vue'

const store = useStore()
const recommendedCourses = computed(() => store.state.courses.recommendedCourses)

const handleCourseSelect = async (courseId) => {
  try {
    await store.dispatch('courses/selectCourse', courseId)
  } catch (error) {
    console.error('选课失败:', error)
  }
}

onMounted(async () => {
  try {
    await store.dispatch('courses/fetchRecommendedCourses')
  } catch (error) {
    console.error('获取推荐课程失败:', error)
  }
})
</script>

<style scoped>
.swiper {
  width: 100%;
  height: 100%;
}

.swiper-slide {
  text-align: center;
  background: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  color: #4F46E5;
}

:deep(.swiper-pagination-bullet-active) {
  background: #4F46E5;
}
</style>