<template>
  <div class="flex flex-col h-full overflow-hidden bg-gray-50">
    <!-- Calendar -->
    <div class="bg-white">
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
        style="height: 420px"
        events-on-month-view="short"
      />
    </div>

    <!-- Section header -->
    <div class="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-100 shadow-sm">
      <div class="flex items-center gap-2">
        <span class="text-sm font-bold text-gray-900">{{ listLabel }}</span>
        <button
          v-if="selectedDate"
          @click="clearDate"
          class="text-xs text-blue-500 bg-blue-50 px-2.5 py-0.5 rounded-full font-medium"
        >전체 보기</button>
      </div>
      <span class="text-xs bg-blue-500 text-white font-bold px-2.5 py-0.5 rounded-full">
        {{ listRaces.length }}
      </span>
    </div>

    <!-- Race list -->
    <div class="flex-1 overflow-y-auto px-3 pt-3 pb-20 space-y-2.5">

      <div
        v-for="race in listRaces"
        :key="race.id"
        @click="goToDetail(race.id)"
        class="bg-white rounded-2xl overflow-hidden shadow-sm cursor-pointer active:scale-95 transition-transform border-l-4 flex"
        :class="statusBorderClass(race.status)"
      >
        <!-- Date badge (월별 보기일 때) -->
        <div
          v-if="!selectedDate"
          class="flex flex-col items-center justify-center px-3 py-3 shrink-0"
          :class="dayOfWeek(race.date) === '토' ? 'bg-blue-50' : dayOfWeek(race.date) === '일' ? 'bg-red-50' : 'bg-gray-50'"
        >
          <span
            class="text-xl font-black leading-none"
            :class="dayOfWeek(race.date) === '토' ? 'text-blue-500' : dayOfWeek(race.date) === '일' ? 'text-red-500' : 'text-gray-700'"
          >{{ dayStr(race.date) }}</span>
          <span
            class="text-xs font-semibold mt-0.5"
            :class="dayOfWeek(race.date) === '토' ? 'text-blue-400' : dayOfWeek(race.date) === '일' ? 'text-red-400' : 'text-gray-400'"
          >{{ dayOfWeek(race.date) }}</span>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0 px-3 py-3">
          <div class="flex items-start justify-between gap-2">
            <p class="font-bold text-sm text-gray-900 leading-snug line-clamp-2">{{ race.name }}</p>
            <span
              class="text-xs px-2 py-0.5 rounded-full font-semibold shrink-0 mt-0.5"
              :class="statusClass(race.status)"
            >{{ race.status }}</span>
          </div>
          <p class="text-xs text-gray-400 mt-1">📍 {{ race.location?.city }}{{ race.start_time ? ' · ' + race.start_time : '' }}</p>
          <div v-if="race.distances?.length" class="flex gap-1 mt-1.5 flex-wrap">
            <span
              v-for="d in race.distances"
              :key="d"
              class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-md font-medium"
            >{{ d }}</span>
          </div>
        </div>
      </div>

      <!-- 선택한 날짜에 대회 없음 -->
      <div v-if="listRaces.length === 0 && selectedDate"
        class="flex flex-col items-center justify-center py-14 text-gray-300">
        <div class="text-5xl mb-3">📅</div>
        <p class="text-sm font-medium text-gray-400">이 날에 대회가 없어요</p>
        <button @click="clearDate"
          class="mt-4 text-xs text-blue-500 bg-blue-50 px-4 py-1.5 rounded-full font-medium">
          전체 보기
        </button>
      </div>

      <!-- 해당 월 대회 없음 -->
      <div v-else-if="listRaces.length === 0"
        class="flex flex-col items-center justify-center py-14 text-gray-300">
        <div class="text-5xl mb-3">🏃</div>
        <p class="text-sm font-medium text-gray-400">이번 달 대회가 없어요</p>
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

function onCellClick(date) {
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
    '접수예정': 'bg-amber-100 text-amber-700',
    '대회종료': 'bg-gray-100 text-gray-400'
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

function statusBorderClass(status) {
  const map = {
    '접수중': 'border-green-400',
    '접수마감': 'border-red-400',
    '접수예정': 'border-amber-400',
    '대회종료': 'border-gray-200'
  }
  return map[status] || 'border-gray-200'
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
/* ── 뷰 선택 탭 숨기기 ── */
.vuecal--custom .vuecal__menu { display: none !important; }

/* ── 타이틀 바 ── */
.vuecal--custom .vuecal__title-bar {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 10px 16px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.2px;
}
.vuecal--custom .vuecal__arrow { color: rgba(255,255,255,0.85); font-size: 16px; }
.vuecal--custom .vuecal__arrow:hover { color: white; }

/* ── 요일 헤더 ── */
.vuecal--custom .vuecal__weekdays-headings {
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  padding: 2px 0;
}
.vuecal--custom .vuecal__heading {
  font-size: 11px;
  font-weight: 700;
  color: #aaa;
  letter-spacing: 0.3px;
}
.vuecal--custom .vuecal__heading:nth-child(6) { color: #60a5fa; }
.vuecal--custom .vuecal__heading:nth-child(7) { color: #f87171; }

/* ── 셀 ── */
.vuecal--custom .vuecal__cell {
  border-color: #f3f4f6 !important;
}
.vuecal--custom .vuecal__cell-date {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  padding: 3px 5px;
}
.vuecal--custom .vuecal__cell--out-of-scope .vuecal__cell-date { color: #d1d5db; }

/* ── 오늘 ── */
.vuecal--custom .vuecal__cell--today { background: #eff6ff !important; }
.vuecal--custom .vuecal__cell--today .vuecal__cell-date {
  color: #2563eb;
  font-weight: 800;
}

/* ── 선택된 셀 ── */
.vuecal--custom .vuecal__cell--selected { background: #dbeafe !important; }

/* ── 이벤트 ── */
.vuecal--custom .vuecal__event {
  border-radius: 3px !important;
  padding: 1px 3px !important;
  font-size: 9px !important;
  line-height: 1.3 !important;
  margin: 0 2px 1px 2px !important;
  color: white;
  font-weight: 600;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.event-open   { background-color: #22c55e !important; }
.event-closed { background-color: #ef4444 !important; }
.event-upcoming { background-color: #f59e0b !important; }
.event-done   { background-color: #d1d5db !important; color: #9ca3af !important; }
</style>
