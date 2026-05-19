<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white sticky top-0 z-10 flex items-center gap-3 px-4 py-3 border-b border-gray-200">
      <button @click="router.back()" class="text-xl">←</button>
      <h1 class="font-bold text-base truncate flex-1">{{ race?.name || '대회 상세' }}</h1>
    </div>

    <div v-if="race" class="p-4 space-y-4">
      <!-- Status badge -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="inline-block text-sm px-3 py-1 rounded-full font-medium" :class="statusClass(race.status)">
          {{ race.status }}
        </span>
        <span v-if="registrationCountdown" class="text-sm font-semibold" :class="registrationCountdown.colorClass">
          {{ registrationCountdown.text }}
        </span>
      </div>

      <!-- Date & Location -->
      <div class="bg-white rounded-2xl p-4 space-y-3">
        <div class="flex items-start gap-3">
          <span class="text-xl">📅</span>
          <div>
            <p class="text-xs text-gray-400">대회 날짜</p>
            <p class="font-medium">{{ formatDate(race.date) }}{{ race.start_time ? ' · ' + race.start_time + ' 출발' : '' }}</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <span class="text-xl">📍</span>
          <div>
            <p class="text-xs text-gray-400">장소</p>
            <p class="font-medium">{{ race.location?.address }}</p>
          </div>
        </div>
        <div v-if="race.registration_start" class="flex items-start gap-3">
          <span class="text-xl">📝</span>
          <div>
            <p class="text-xs text-gray-400">접수 시작</p>
            <p class="font-medium">{{ formatDateWithTime(race.registration_start, race.registration_start_time) }}</p>
          </div>
        </div>
        <div v-if="race.registration_deadline" class="flex items-start gap-3">
          <span class="text-xl">⏰</span>
          <div>
            <p class="text-xs text-gray-400">접수 마감</p>
            <p class="font-medium">{{ formatDateWithTime(race.registration_deadline, race.registration_deadline_time) }}</p>
          </div>
        </div>
      </div>

      <!-- Description -->
      <div v-if="race.description" class="bg-white rounded-2xl p-4">
        <p class="text-xs text-gray-400 mb-2">코스 소개</p>
        <p class="text-sm text-gray-700 leading-relaxed">{{ race.description }}</p>
      </div>

      <!-- Course Info -->
      <div v-if="race.course" class="bg-white rounded-2xl p-4 space-y-3">
        <p class="text-xs text-gray-400">코스 정보</p>
        <div class="grid grid-cols-3 gap-2">
          <div class="bg-gray-50 rounded-xl p-2 text-center">
            <p class="text-xs text-gray-400 mb-0.5">유형</p>
            <p class="text-xs font-medium text-gray-700">{{ race.course.type }}</p>
          </div>
          <div class="bg-gray-50 rounded-xl p-2 text-center">
            <p class="text-xs text-gray-400 mb-0.5">노면</p>
            <p class="text-xs font-medium text-gray-700">{{ race.course.surface }}</p>
          </div>
        </div>
        <div v-if="race.course.highlights?.length">
          <p class="text-xs text-gray-400 mb-1.5">주요 포인트</p>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="(h, i) in race.course.highlights"
              :key="h"
              class="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700"
            >{{ i + 1 }}. {{ h }}</span>
          </div>
        </div>
        <div v-if="race.course.routes">
          <p class="text-xs text-gray-400 mb-1.5">종목별 코스</p>
          <div class="space-y-2">
            <div v-for="(route, dist) in race.course.routes" :key="dist" class="bg-gray-50 rounded-xl p-2">
              <span class="text-xs font-semibold text-blue-600 mr-1.5">{{ dist }}</span>
              <span class="text-xs text-gray-600">{{ route }}</span>
            </div>
          </div>
        </div>
        <div v-if="race.course.images?.length">
          <p class="text-xs text-gray-400 mb-1.5">코스 사진</p>
          <div class="flex flex-col gap-2">
            <img
              v-for="img in race.course.images"
              :key="img"
              :src="img"
              alt="코스 사진"
              class="w-full rounded-xl object-cover"
              @error="$event.target.style.display='none'"
            />
          </div>
        </div>
      </div>

      <!-- Organizer / Contact -->
      <div v-if="race.organizer || race.contact" class="bg-white rounded-2xl p-4 space-y-2">
        <p class="text-xs text-gray-400 mb-1">주최 / 문의</p>
        <div v-if="race.organizer" class="flex items-center gap-2 text-sm text-gray-700">
          <span class="text-gray-400 text-xs w-10 shrink-0">주최</span>
          <span>{{ race.organizer }}</span>
        </div>
        <a v-if="race.contact?.phone" :href="`tel:${race.contact.phone}`" class="flex items-center gap-2 text-sm text-blue-600">
          <span class="text-gray-400 text-xs w-10 shrink-0">전화</span>
          <span>{{ race.contact.phone }}</span>
        </a>
        <a v-if="race.contact?.email" :href="`mailto:${race.contact.email}`" class="flex items-center gap-2 text-sm text-blue-600">
          <span class="text-gray-400 text-xs w-10 shrink-0">이메일</span>
          <span>{{ race.contact.email }}</span>
        </a>
      </div>

      <!-- Entry Fee -->
      <div v-if="race.fee" class="bg-white rounded-2xl p-4">
        <p class="text-xs text-gray-400 mb-2">참가비</p>
        <div class="flex flex-wrap gap-2">
          <div v-for="(price, dist) in race.fee" :key="dist"
            class="flex-1 min-w-[80px] bg-gray-50 rounded-xl p-2 text-center">
            <p class="text-xs text-gray-400 mb-0.5">{{ dist }}</p>
            <p class="text-sm font-semibold text-gray-800">{{ (price / 10000).toFixed(0) }}만원</p>
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
import { formatDate, formatDateWithTime } from '../utils/date'

const route = useRoute()
const router = useRouter()
const racesStore = useRacesStore()

const race = computed(() => racesStore.getRaceById(route.params.id))

function daysUntil(dateStr) {
  if (!dateStr) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(dateStr + 'T00:00:00')
  return Math.round((target - today) / (1000 * 60 * 60 * 24))
}

const registrationCountdown = computed(() => {
  if (!race.value) return null
  const { status, registration_start, registration_deadline } = race.value

  if (status === '접수예정' && registration_start) {
    const days = daysUntil(registration_start)
    if (days === null || days < 0) return null
    if (days === 0) return { text: '오늘 접수 시작!', colorClass: 'text-yellow-600' }
    return { text: `접수까지 ${days}일 남았어요`, colorClass: 'text-yellow-600' }
  }

  if (status === '접수중' && registration_deadline) {
    const days = daysUntil(registration_deadline)
    if (days === null || days < 0) return null
    if (days === 0) return { text: '오늘 접수 마감!', colorClass: 'text-red-600' }
    if (days <= 3) return { text: `접수 마감까지 ${days}일 남았어요`, colorClass: 'text-red-600' }
    return { text: `접수 마감까지 ${days}일 남았어요`, colorClass: 'text-green-600' }
  }

  return null
})

function terrainClass(terrain) {
  const map = {
    '평탄': 'text-green-600',
    '완만': 'text-yellow-600',
    '언덕': 'text-red-600'
  }
  return map[terrain] || 'text-gray-700'
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
