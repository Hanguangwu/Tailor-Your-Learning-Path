<template>
  <div class="relative w-full overflow-hidden">
    <div class="relative h-80">
      <transition-group name="fade">
        <div
          v-for="(slide, index) in slides"
          :key="index"
          v-show="currentSlide === index"
          class="absolute inset-0"
        >
          <div class="h-full w-full bg-cover bg-center" :style="{ backgroundImage: `url(${slide.image})` }">
            <div class="h-full w-full bg-black bg-opacity-50 flex items-center">
              <div class="container mx-auto px-6">
                <div class="max-w-lg text-white">
                  <h2 class="text-3xl font-bold mb-2">{{ slide.title }}</h2>
                  <p class="mb-4">{{ slide.description }}</p>
                  <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    立即查看
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 导航按钮 -->
    <button @click="prevSlide" class="absolute left-0 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-30 p-2 text-white">
      &lt;
    </button>
    <button @click="nextSlide" class="absolute right-0 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-30 p-2 text-white">
      &gt;
    </button>

    <!-- 指示点 -->
    <div class="absolute bottom-4 left-0 right-0 flex justify-center space-x-2">
      <button
        v-for="(_, index) in slides"
        :key="index"
        @click="setSlide(index)"
        class="w-3 h-3 rounded-full"
        :class="currentSlide === index ? 'bg-white' : 'bg-white bg-opacity-50'"
      ></button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'CourseCarousel',
  props: {
    slides: {
      type: Array,
      required: true
    },
    autoplay: {
      type: Boolean,
      default: true
    },
    interval: {
      type: Number,
      default: 5000
    }
  },
  setup(props) {
    const currentSlide = ref(0)
    let timer = null

    const nextSlide = () => {
      currentSlide.value = (currentSlide.value + 1) % props.slides.length
    }

    const prevSlide = () => {
      currentSlide.value = (currentSlide.value - 1 + props.slides.length) % props.slides.length
    }

    const setSlide = (index) => {
      currentSlide.value = index
    }

    const startAutoplay = () => {
      if (props.autoplay && props.slides.length > 1) {
        timer = setInterval(() => {
          nextSlide()
        }, props.interval)
      }
    }

    const stopAutoplay = () => {
      if (timer) {
        clearInterval(timer)
      }
    }

    onMounted(() => {
      startAutoplay()
    })

    onBeforeUnmount(() => {
      stopAutoplay()
    })

    return {
      currentSlide,
      nextSlide,
      prevSlide,
      setSlide
    }
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>