<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white sticky top-0 z-10 flex items-center gap-3 px-4 py-3 border-b border-gray-200">
      <button @click="router.back()" class="text-xl">←</button>
      <h1 class="font-bold text-base truncate flex-1">{{ race?.name || '대회 상세' }}</h1>
    </div>

    <div v-if="race" class="p-4 space-y-4">
      <!-- Status badge -->
      <span class="inline-block text-sm px-3 py-1 rounded-full font-medium" :class="statusClass(race.status)">
        {{ race.status }}
      </span>

      <!-- Date & Location -->
      <div class="bg-white rounded-2xl p-4 space-y-3">
        <div class="flex items-start gap-3">
          <span class="text-xl">📅</span>
          <div>
            <p class="text-xs text-gray-400">대회 날짜</p>
            <p class="font-medium">{{ formatDate(race.date) }}</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <span class="text-xl">📍</span>
          <div>
            <p class="text-xs text-gray-400">장소</p>
            <p class="font-medium">{{ race.location?.address }}</p>
          </div>
        </div>
        <div v-if="race.registration_deadline" class="flex items-start gap-3">
          <span class="text-xl">⏰</span>
          <div>
            <p class="text-xs text-gray-400">접수 마감</p>
            <p class="font-medium">{{ formatDate(race.registration_deadline) }}</p>
          </div>
        </div>
      </div>

      <!-- Distances -->
      <div class="bg-white rounded-2xl p-4">
        <p class="text-xs text-gray-400 mb-2">종목</p>
        <div class="flex gap-2 flex-wrap">
          <span v-for="d in race.distances" :key="d"
            class="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            {{ d }}
          </span>
        </div>
      </div>

      <!-- Map placeholder / Kakao map link -->
      <div class="bg-white rounded-2xl p-4">
        <p class="text-xs text-gray-400 mb-2">지도</p>
        <a
          v-if="race.location?.lat"
          :href="`https://map.kakao.com/link/map/${encodeURIComponent(race.name)},${race.location.lat},${race.location.lng}`"
          target="_blank"
          class="flex items-center gap-2 text-blue-600 text-sm"
        >
          <span>🗺️</span>
          카카오맵에서 보기 →
        </a>
        <p v-else class="text-gray-400 text-sm">위치 정보 없음</p>
      </div>

      <!-- Registration button -->
      <a
        v-if="race.registration_url"
        :href="race.registration_url"
        target="_blank"
        class="block w-full text-center bg-blue-600 text-white py-3 rounded-2xl font-medium text-base"
      >
        신청하기 →
      </a>

      <!-- Source link -->
      <a
        v-if="race.source_url"
        :href="race.source_url"
        target="_blank"
        class="block text-center text-gray-400 text-xs py-2"
      >
        원본 페이지 보기
      </a>
    </div>

    <!-- Loading -->
    <div v-else-if="racesStore.loading" class="flex justify-center p-8">
      <span class="text-gray-400 text-sm">불러오는 중...</span>
    </div>

    <!-- Not found -->
    <div v-else class="flex flex-col items-center justify-center py-24 text-gray-400">
      <span class="text-4xl mb-3">😕</span>
      <p class="text-sm mb-4">대회를 찾을 수 없어요</p>
      <RouterLink to="/" class="text-blue-600 text-sm">홈으로</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useRacesStore } from '../stores/races'

const route = useRoute()
const router = useRouter()
const racesStore = useRacesStore()

const race = computed(() => racesStore.getRaceById(route.params.id))

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`
}

function statusClass(status) {
  const map = {
    '접수중': 'bg-green-100 text-green-700',
    '접수마감': 'bg-red-100 text-red-700',
    '접수예정': 'bg-yellow-100 text-yellow-700',
    '대회종료': 'bg-gray-100 text-gray-500'
  }
  return map[status] || 'bg-gray-100 text-gray-600'
}

onMounted(() => {
  if (racesStore.races.length === 0) racesStore.loadRaces()
})
</script>
