<template>
    <footer class="bg-gray-800 text-white py-4 mt-auto">
      <div class="container mx-auto text-center">
        <p>&copy; {{ currentYear }} 天漢 All Rights Reserved.</p>
      </div>
    </footer>
  </template>
  
  <script>
  export default {
    name: 'Footer',
    computed: {
      currentYear() {
        return new Date().getFullYear()
      }
    }
  }
  </script>