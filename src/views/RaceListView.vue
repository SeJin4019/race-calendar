<template>
  <AppLayout>
    <div class="flex flex-col h-full">
      <!-- Search bar -->
      <div class="p-3 bg-white border-b border-gray-100 sticky top-0 z-10">
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          <input
            v-model="racesStore.searchQuery"
            type="search"
            placeholder="대회명, 지역 검색..."
            class="w-full pl-9 pr-4 py-2 bg-gray-100 rounded-xl text-sm outline-none"
          />
        </div>
      </div>

      <!-- Filter row -->
      <div class="flex gap-2 px-3 py-2 overflow-x-auto bg-white border-b border-gray-100 shrink-0">
        <!-- Status filter -->
        <button
          v-for="s in statusOptions"
          :key="s.value"
          @click="toggleStatus(s.value)"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="racesStore.filterStatus === s.value
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-600 border-gray-200'"
        >
          {{ s.label }}
        </button>

        <!-- City filter -->
        <button
          v-for="city in racesStore.cities"
          :key="city"
          @click="toggleCity(city)"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="racesStore.filterCity.includes(city)
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-600 border-gray-200'"
        >
          {{ city }}
        </button>
      </div>

      <!-- Count -->
      <div class="px-4 py-2 text-xs text-gray-400 bg-gray-50">
        {{ racesStore.filteredRaces.length }}개 대회
      </div>

      <!-- Race list -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="racesStore.loading" class="flex justify-center p-8">
          <span class="text-gray-400 text-sm">불러오는 중...</span>
        </div>

        <template v-else-if="racesStore.filteredRaces.length > 0">
          <RouterLink
            v-for="race in racesStore.filteredRaces"
            :key="race.id"
            :to="`/races/${race.id}`"
            class="flex items-center gap-3 px-4 py-3 border-b border-gray-100 bg-white hover:bg-gray-50 active:bg-gray-100"
          >
            <!-- Date block -->
            <div class="shrink-0 text-center w-12">
              <div class="text-xs text-gray-400">{{ monthStr(race.date) }}</div>
              <div class="text-xl font-bold leading-tight">{{ dayStr(race.date) }}</div>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm truncate">{{ race.name }}</p>
              <p class="text-xs text-gray-500">📍 {{ race.location?.city }}</p>
              <div class="flex gap-1 mt-1 flex-wrap">
                <span v-for="d in race.distances" :key="d"
                  class="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">{{ d }}</span>
              </div>
            </div>

            <!-- Status -->
            <span class="shrink-0 text-xs px-2 py-1 rounded-full font-medium" :class="statusClass(race.status)">
              {{ race.status }}
            </span>
          </RouterLink>
        </template>

        <div v-else class="flex flex-col items-center justify-center py-16 text-gray-400">
          <span class="text-4xl mb-2">🔍</span>
          <p class="text-sm">검색 결과가 없어요</p>
          <button @click="resetFilters" class="mt-3 text-blue-600 text-sm">필터 초기화</button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRacesStore } from '../stores/races'
import AppLayout from '../components/AppLayout.vue'

const racesStore = useRacesStore()

const statusOptions = [
  { value: '접수중', label: '접수중' },
  { value: '접수예정', label: '접수예정' },
  { value: '접수마감', label: '접수마감' }
]

function toggleStatus(val) {
  racesStore.filterStatus = racesStore.filterStatus === val ? '' : val
}

function toggleCity(city) {
  const idx = racesStore.filterCity.indexOf(city)
  if (idx === -1) racesStore.filterCity.push(city)
  else racesStore.filterCity.splice(idx, 1)
}

function resetFilters() {
  racesStore.filterStatus = ''
  racesStore.filterCity = []
  racesStore.filterDistances = []
  racesStore.searchQuery = ''
}

function monthStr(dateStr) {
  if (!dateStr) return ''
  return dateStr.substring(5, 7) + '월'
}

function dayStr(dateStr) {
  if (!dateStr) return ''
  return parseInt(dateStr.substring(8, 10))
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
