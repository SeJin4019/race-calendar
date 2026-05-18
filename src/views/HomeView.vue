<template>
  <AppLayout>
    <div class="flex flex-col" style="height: calc(100vh - 64px - 57px)">
      <!-- Tab header -->
      <div class="flex bg-white border-b border-gray-200 sticky top-0 z-10 shrink-0">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="uiStore.setTab(tab.id)"
          class="flex-1 py-3 text-sm font-medium border-b-2 transition-colors"
          :class="uiStore.homeTab === tab.id
            ? 'border-blue-600 text-blue-600'
            : 'border-transparent text-gray-500'"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab content fills remaining height -->
      <div class="flex-1 overflow-hidden relative">
        <MapView v-show="uiStore.homeTab === 'map'" class="absolute inset-0" />
        <CalendarPlaceholder v-show="uiStore.homeTab === 'calendar'" class="absolute inset-0" />
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUiStore } from '../stores/ui'
import { useRacesStore } from '../stores/races'
import AppLayout from '../components/AppLayout.vue'
import MapView from '../components/MapView.vue'

const uiStore = useUiStore()
const racesStore = useRacesStore()

const CalendarPlaceholder = { template: '<div class="flex items-center justify-center h-full text-gray-400 text-sm">달력 뷰 (구현 예정)</div>' }

const tabs = [
  { id: 'map', label: '🗺️ 지도' },
  { id: 'calendar', label: '📅 달력' }
]

onMounted(() => {
  if (racesStore.races.length === 0) racesStore.loadRaces()
})
</script>
