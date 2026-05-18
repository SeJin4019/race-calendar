<template>
  <div class="flex flex-col h-full bg-white overflow-hidden">
    <!-- Calendar -->
    <vue-cal
      class="vuecal--custom shrink-0"
      :events="calEvents"
      view="month"
      :time="false"
      :disable-views="['years', 'year', 'week', 'day']"
      :on-event-click="onEventClick"
      @cell-click="onCellClick"
      @view-change="onViewChange"
      locale="ko"
      style="height: 360px"
      events-on-month-view="short"
    />

    <!-- Section header -->
    <div class="flex items-center justify-between px-4 py-2.5 border-b border-gray-100 bg-white">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-gray-800">{{ listLabel }}</span>
        <button v-if="selectedDate" @click="clearDate" class="text-xs text-blue-500">전체 보기</button>
      </div>
      <span class="text-xs bg-gray-100 text-gray-500 font-medium px-2 py-0.5 rounded-full">{{ listRaces.length }}개</span>
    </div>

    <!-- Race list -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="listRaces.length > 0" class="divide-y divide-gray-50">
        <div
          v-for="race in listRaces"
          :key="race.id"
          @click="goToDetail(race.id)"
          class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 active:bg-gray-100 transition-colors"
        >
          <!-- Date column (월 전체 보기일 때만) -->
          <div v-if="!selectedDate" class="shrink-0 text-center w-9">
            <div class="text-base font-bold leading-tight" :class="dayOfWeek(race.date) === '토' ? 'text-blue-500' : dayOfWeek(race.date) === '일' ? 'text-red-500' : 'text-gray-800'">{{ dayStr(race.date) }}</div>
            <div class="text-xs" :class="dayOfWeek(race.date) === '토' ? 'text-blue-400' : dayOfWeek(race.date) === '일' ? 'text-red-400' : 'text-gray-400'">{{ dayOfWeek(race.date) }}</div>
          </div>

          <div class="flex-1 min-w-0">
            <p class="font-medium text-sm truncate text-gray-900">{{ race.name }}</p>
            <p class="text-xs text-gray-400 mt-0.5">📍 {{ race.location?.city }}</p>
          </div>

          <div class="flex flex-col items-end gap-1 shrink-0">
            <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="statusClass(race.status)">{{ race.status }}</span>
            <div class="flex gap-1">
              <span v-for="d in race.distances" :key="d" class="text-xs text-gray-400">{{ d }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 선택한 날짜에 대회 없음 -->
      <div v-else-if="selectedDate" class="flex flex-col items-center justify-center py-12 text-gray-300">
        <div class="text-4xl mb-2">📅</div>
        <p class="text-sm">이 날에 대회가 없어요</p>
        <button @click="clearDate" class="mt-3 text-xs text-blue-400">전체 보기</button>
      </div>

      <!-- 해당 월 대회 없음 -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-gray-300">
        <div class="text-4xl mb-2">🏃</div>
        <p class="text-sm">이번 달 대회가 없어요</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'
import { useRacesStore } from '../stores/races'
import { formatDate, dayStr, dayOfWeek } from '../utils/date'

const racesStore = useRacesStore()
const router = useRouter()

const selectedDate = ref(null)
const now = new Date()
const currentCalMonth = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)

const calEvents = computed(() =>
  racesStore.races
    .filter(r => r.date)
    .map(r => ({
      start: r.date,
      end: r.date,
      title: r.name,
      class: statusEventClass(r.status),
      raceId: r.id
    }))
)

const listRaces = computed(() => {
  if (selectedDate.value) {
    return racesStore.races.filter(r => r.date === selectedDate.value)
  }
  return racesStore.races
    .filter(r => r.date && r.date.startsWith(currentCalMonth.value))
    .sort((a, b) => a.date.localeCompare(b.date))
})

const listLabel = computed(() => {
  if (selectedDate.value) return formatDate(selectedDate.value)
  const [, month] = currentCalMonth.value.split('-')
  return `${parseInt(month)}월 대회`
})

function onEventClick(event) {
  const race = racesStore.races.find(r => r.id === event.raceId)
  if (race) selectedDate.value = race.date
}

function onCellClick({ date }) {
  const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  selectedDate.value = selectedDate.value === dateStr ? null : dateStr
}

function onViewChange({ startDate }) {
  currentCalMonth.value = `${startDate.getFullYear()}-${String(startDate.getMonth() + 1).padStart(2, '0')}`
  selectedDate.value = null
}

function clearDate() {
  selectedDate.value = null
}

function goToDetail(id) {
  router.push(`/races/${id}`)
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

function statusEventClass(status) {
  const map = {
    '접수중': 'event-open',
    '접수마감': 'event-closed',
    '접수예정': 'event-upcoming',
    '대회종료': 'event-done'
  }
  return map[status] || ''
}
</script>

<style>
.vuecal--custom .vuecal__title-bar { background-color: #2563eb; color: white; }
.vuecal--custom .vuecal__cell--today { background-color: #eff6ff; }
.vuecal--custom .vuecal__cell--selected { background-color: #dbeafe !important; }
.event-open { background-color: #22c55e !important; color: white; }
.event-closed { background-color: #ef4444 !important; color: white; }
.event-upcoming { background-color: #f59e0b !important; color: white; }
.event-done { background-color: #9ca3af !important; color: white; }
</style>
