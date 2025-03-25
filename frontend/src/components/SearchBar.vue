<template>
  <div class="relative">
    <div class="relative flex items-center">
      <input
        v-model="searchText"
        type="text"
        placeholder="搜索课程..."
        class="w-full px-4 py-2 pr-12 rounded-lg border focus:outline-none focus:ring-2 focus:ring-indigo-500"
        @keyup.enter="handleSearch"
      />
      <button
        v-if="searchText"
        @click="clearSearch"
        class="absolute right-10 text-gray-400 hover:text-gray-600"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M6 18L18 6M6 6l12 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <button
        @click="handleSearch"
        class="absolute right-3 text-gray-400 hover:text-gray-600"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'SearchBar',
  emits: ['search'],
  setup(props, { emit }) {
    const searchText = ref('')

    const handleSearch = () => {
      if (searchText.value.trim()) {
        emit('search', searchText.value)
      }
    }

    const clearSearch = () => {
      searchText.value = ''
    }

    return {
      searchText,
      handleSearch,
      clearSearch
    }
  }
}
</script>