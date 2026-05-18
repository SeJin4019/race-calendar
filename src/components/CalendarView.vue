<template>
  <div class="flex flex-col h-full bg-white overflow-hidden">
    <!-- vue-cal monthly calendar -->
    <vue-cal
      class="vuecal--blue-theme shrink-0"
      :events="calEvents"
      view="month"
      :time="false"
      :disable-views="['years', 'year', 'week', 'day']"
      :on-event-click="onEventClick"
      locale="ko"
      style="height: 380px"
      events-on-month-view="short"
    />

    <!-- Selected date race list -->
    <div class="flex-1 overflow-y-auto border-t border-gray-100">
      <div v-if="selectedDateRaces.length > 0" class="p-3">
        <p class="text-xs text-gray-400 mb-2">{{ selectedDateLabel }}</p>
        <div
          v-for="race in selectedDateRaces"
          :key="race.id"
          @click="goToDetail(race.id)"
          class="flex items-center gap-3 p-3 mb-2 rounded-xl border border-gray-100 cursor-pointer hover:bg-gray-50 active:bg-gray-100"
          :class="uiStore.selectedRaceId === race.id ? 'border-blue-300 bg-blue-50' : ''"
        >
          <div class="flex-1 min-w-0">
            <p class="font-medium text-sm truncate">{{ race.name }}</p>
            <p class="text-xs text-gray-500">{{ race.location?.city }}</p>
          </div>
          <div class="flex flex-col items-end gap-1 shrink-0">
            <span class="text-xs px-2 py-0.5 rounded-full" :class="statusClass(race.status)">{{ race.status }}</span>
            <div class="flex gap-1">
              <span v-for="d in race.distances" :key="d" class="text-xs text-gray-500">{{ d }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="selectedDate" class="flex flex-col items-center justify-center h-32 text-gray-400">
        <span class="text-2xl mb-1">🏃</span>
        <p class="text-sm">이 날짜에 대회가 없어요</p>
      </div>

      <div v-else class="flex flex-col items-center justify-center h-32 text-gray-400">
        <p class="text-sm">날짜를 클릭해서 대회를 확인하세요</p>
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
import { useUiStore } from '../stores/ui'
import { formatDate } from '../utils/date'

const racesStore = useRacesStore()
const uiStore = useUiStore()
const router = useRouter()

const selectedDate = ref(null)

// Build vue-cal events from races
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

// Races on the selected date
const selectedDateRaces = computed(() => {
  if (!selectedDate.value) return []
  return racesStore.races.filter(r => r.date === selectedDate.value)
})

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  return formatDate(selectedDate.value)
})

function onEventClick(event) {
  selectedDate.value = event.start?.substring(0, 10) || event.start
  uiStore.selectRace(event.raceId)
}

function goToDetail(id) {
  uiStore.selectRace(id)
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
/* vue-cal custom colors */
.vuecal--blue-theme .vuecal__title-bar { background-color: #2563eb; color: white; }
.vuecal--blue-theme .vuecal__cell--today { background-color: #eff6ff; }
.vuecal--blue-theme .vuecal__cell--selected { background-color: #dbeafe !important; }
.event-open { background-color: #22c55e !important; color: white; }
.event-closed { background-color: #ef4444 !important; color: white; }
.event-upcoming { background-color: #f59e0b !important; color: white; }
.event-done { background-color: #9ca3af !important; color: white; }
</style>
