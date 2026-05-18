<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center p-8">
    <div class="text-6xl mb-4">🏃</div>
    <h1 class="text-2xl font-bold mb-2">페이지를 찾을 수 없어요</h1>
    <p class="text-gray-500 mb-6">요청한 페이지가 존재하지 않습니다.</p>
    <RouterLink to="/" class="bg-blue-600 text-white px-6 py-2 rounded-full text-sm font-medium">
      홈으로 돌아가기
    </RouterLink>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
