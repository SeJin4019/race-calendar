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
        <!-- 즐겨찾기 filter -->
        <button
          @click="filterFavorites = !filterFavorites"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="filterFavorites
            ? 'bg-yellow-400 text-white border-yellow-400'
            : 'bg-white text-yellow-500 border-yellow-200'"
        >
          ★ 즐겨찾기
        </button>

        <div class="w-px bg-gray-200 shrink-0"></div>

        <!-- 공인대회 filter -->
        <button
          @click="filterCertified = !filterCertified"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="filterCertified
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-blue-600 border-blue-200'"
        >
          🏅 공인대회
        </button>

        <!-- 풀코스 filter -->
        <button
          @click="toggleFullOnly"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="racesStore.filterDistances.includes('풀')
            ? 'bg-purple-600 text-white border-purple-600'
            : 'bg-white text-gray-600 border-gray-200'"
        >
          풀코스
        </button>

        <div class="w-px bg-gray-200 shrink-0"></div>

        <!-- Day of week filter -->
        <button
          @click="toggleDay(6)"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="racesStore.filterDays.includes(6)
            ? 'bg-blue-500 text-white border-blue-500'
            : 'bg-white text-blue-500 border-blue-200'"
        >
          토요일
        </button>
        <button
          @click="toggleDay(0)"
          class="shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors"
          :class="racesStore.filterDays.includes(0)
            ? 'bg-red-500 text-white border-red-500'
            : 'bg-white text-red-500 border-red-200'"
        >
          일요일
        </button>

        <div class="w-px bg-gray-200 shrink-0"></div>

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

        <!-- Province filter -->
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

      <!-- Count + 종료 대회 토글 -->
      <div class="px-4 py-2 text-xs text-gray-400 bg-gray-50 flex items-center justify-between">
        <span>{{ displayedRaces.length }}개 대회</span>
        <button
          @click="racesStore.hideEnded = !racesStore.hideEnded"
          class="text-xs transition-colors"
          :class="racesStore.hideEnded ? 'text-gray-400' : 'text-blue-500'"
        >
          {{ racesStore.hideEnded ? '종료 대회 포함' : '종료 대회 숨기기' }}
        </button>
      </div>

      <!-- Race list -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="racesStore.loading" class="flex justify-center p-8">
          <span class="text-gray-400 text-sm">불러오는 중...</span>
        </div>

        <template v-else-if="groupedRaces.length > 0">
          <template v-for="group in groupedRaces" :key="group.month">
            <!-- Month header -->
            <div class="sticky top-0 z-10 px-4 py-1.5 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
              <span class="text-sm font-bold text-gray-700">{{ group.label }}</span>
              <span class="text-xs text-gray-400">{{ group.races.length }}개</span>
            </div>

            <RouterLink
              v-for="race in group.races"
              :key="race.id"
              :to="`/races/${race.id}`"
              class="flex items-center gap-3 pl-0 pr-4 py-3 border-b border-gray-100 bg-white hover:bg-gray-50 active:bg-gray-100"
              :class="{ 'opacity-50': race.status === '접수마감' || race.status === '대회종료' }"
            >
              <!-- Status stripe -->
              <div class="self-stretch w-1 shrink-0 rounded-r-full" :class="statusStripe(race.status)"></div>
              <!-- Date block -->
              <div class="shrink-0 text-center w-12">
                <div class="text-xl font-bold leading-tight">{{ dayStr(race.date) }}</div>
                <div class="text-xs" :class="dayOfWeek(race.date) === '토' ? 'text-blue-500' : dayOfWeek(race.date) === '일' ? 'text-red-500' : 'text-gray-400'">{{ dayOfWeek(race.date) }}</div>
                <div v-if="dday(race.date)" class="text-xs font-medium mt-0.5" :class="ddayClass(race.date)">{{ dday(race.date) }}</div>
              </div>

              <!-- Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5">
                  <p class="font-medium text-sm truncate">{{ race.name }}</p>
                  <span v-if="race.is_certified" class="shrink-0 text-xs px-1 py-0 bg-blue-100 text-blue-600 rounded font-medium">공인</span>
                  <span v-if="race.distances?.includes('풀')" class="shrink-0 text-xs px-1 py-0 bg-purple-100 text-purple-600 rounded font-medium">풀</span>
                </div>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <p class="text-xs text-gray-500">📍 {{ race.location?.city }}{{ race.start_time ? ' · ' + race.start_time : '' }}</p>
                </div>
                <div v-if="race.registration_start || race.registration_deadline" class="flex items-center gap-1.5 mt-0.5 flex-wrap">
                  <p class="text-xs text-gray-400">
                    <span class="text-gray-300">접수</span>
                    {{ race.registration_start ? monthStr(race.registration_start) + ' ' + dayStr(race.registration_start) + '일' + (race.registration_start_time ? ' ' + race.registration_start_time : '') : '-' }}
                    ~
                    {{ race.registration_deadline ? monthStr(race.registration_deadline) + ' ' + dayStr(race.registration_deadline) + '일' + (race.registration_deadline_time ? ' ' + race.registration_deadline_time : '') : '-' }}
                  </p>
                  <span v-if="regDday(race)" class="text-xs px-1.5 py-0 rounded-full font-medium" :class="regDdayClass(race)">
                    접수 {{ regDday(race) }}
                  </span>
                </div>
                <div class="flex items-center gap-1 mt-1 flex-wrap">
                  <span v-for="d in race.distances" :key="d"
                    class="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">{{ d }}</span>
                </div>
                <div v-if="race.fee" class="flex items-center gap-1 mt-1 flex-wrap">
                  <template v-for="d in race.distances" :key="d">
                    <span v-if="race.fee[d]"
                      class="text-xs px-1.5 py-0.5 bg-emerald-50 text-emerald-700 rounded font-medium">
                      {{ d }} {{ (race.fee[d] / 10000).toFixed(0) }}만원
                    </span>
                  </template>
                </div>
              </div>

              <!-- Right: favorite + status -->
              <div class="shrink-0 flex flex-col items-end gap-1.5">
                <button
                  @click.prevent.stop="favoritesStore.toggle(race.id)"
                  class="text-lg leading-none transition-colors"
                  :class="favoritesStore.has(race.id) ? 'text-yellow-400' : 'text-gray-200'"
                >★</button>
                <span class="text-xs px-2 py-1 rounded-full font-medium" :class="statusClass(race.status)">
                  {{ race.status }}
                </span>
              </div>
            </RouterLink>
          </template>
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
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRacesStore } from '../stores/races'
import { useFavoritesStore } from '../stores/favorites'
import AppLayout from '../components/AppLayout.vue'
import { monthStr, dayStr, dayOfWeek, dday } from '../utils/date'

const racesStore = useRacesStore()
const favoritesStore = useFavoritesStore()

const filterFavorites = ref(false)
const filterCertified = ref(false)

const displayedRaces = computed(() => {
  let races = racesStore.filteredRaces
  if (filterFavorites.value) races = races.filter(r => favoritesStore.has(r.id))
  if (filterCertified.value) races = races.filter(r => r.is_certified)
  return races
})

const groupedRaces = computed(() => {
  const groups = {}
  for (const race of displayedRaces.value) {
    const key = race.date ? race.date.slice(0, 7) : 'unknown'
    if (!groups[key]) groups[key] = []
    groups[key].push(race)
  }
  return Object.entries(groups)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, races]) => {
      const [year, m] = month.split('-')
      return { month, label: `${year}년 ${parseInt(m)}월`, races }
    })
})

const statusOptions = [
  { value: '접수중', label: '접수중' },
  { value: '접수예정', label: '접수예정' },
  { value: '접수마감', label: '접수마감' }
]

function toggleFullOnly() {
  const idx = racesStore.filterDistances.indexOf('풀')
  if (idx === -1) racesStore.filterDistances.push('풀')
  else racesStore.filterDistances.splice(idx, 1)
}

function toggleStatus(val) {
  racesStore.filterStatus = racesStore.filterStatus === val ? '' : val
}

function toggleCity(city) {
  const idx = racesStore.filterCity.indexOf(city)
  if (idx === -1) racesStore.filterCity.push(city)
  else racesStore.filterCity.splice(idx, 1)
}

function toggleDay(day) {
  const idx = racesStore.filterDays.indexOf(day)
  if (idx === -1) racesStore.filterDays.push(day)
  else racesStore.filterDays.splice(idx, 1)
}

function resetFilters() {
  racesStore.filterStatus = ''
  racesStore.filterCity = []
  racesStore.filterDistances = []
  racesStore.filterDays = []
  racesStore.searchQuery = ''
  filterFavorites.value = false
  filterCertified.value = false
}

function regDday(race) {
  if (!race.registration_deadline) return null
  if (race.status !== '접수중' && race.status !== '접수예정') return null
  return dday(race.registration_deadline)
}

function regDdayClass(race) {
  const d = regDday(race)
  if (!d) return ''
  if (d === 'D-day') return 'bg-green-100 text-green-700'
  const n = parseInt(d.replace('D-', ''))
  if (n <= 3) return 'bg-red-100 text-red-700'
  if (n <= 7) return 'bg-orange-100 text-orange-700'
  if (n <= 14) return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-500'
}

function ddayClass(dateStr) {
  const d = dday(dateStr)
  if (!d) return ''
  if (d === 'D-day') return 'text-green-600'
  const n = parseInt(d.replace('D-', ''))
  if (n <= 7) return 'text-red-500'
  if (n <= 30) return 'text-orange-500'
  return 'text-gray-400'
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

function statusStripe(status) {
  const map = {
    '접수중': 'bg-green-400',
    '접수예정': 'bg-yellow-400',
    '접수마감': 'bg-gray-200',
    '대회종료': 'bg-gray-200'
  }
  return map[status] || 'bg-gray-200'
}

onMounted(() => {
  if (racesStore.races.length === 0) racesStore.loadRaces()
})
</script>
