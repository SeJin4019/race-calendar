<template>
  <AppLayout>
    <div class="flex flex-col h-full">
      <!-- Tab header -->
      <div class="flex bg-white border-b border-gray-200 sticky top-0 z-10">
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

      <!-- Tab content -->
      <div class="flex-1 relative overflow-hidden">
        <KeepAlive>
          <component :is="currentTabComponent" />
        </KeepAlive>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUiStore } from '../stores/ui'
import { useRacesStore } from '../stores/races'
import AppLayout from '../components/AppLayout.vue'

const uiStore = useUiStore()
const racesStore = useRacesStore()

const tabs = [
  { id: 'map', label: '🗺️ 지도' },
  { id: 'calendar', label: '📅 달력' }
]

// Components will be replaced in Tasks #5 and #6
const MapPlaceholder = { template: '<div class="flex items-center justify-center h-full text-gray-400 text-sm">지도 뷰 (구현 예정)</div>' }
const CalendarPlaceholder = { template: '<div class="flex items-center justify-center h-full text-gray-400 text-sm">달력 뷰 (구현 예정)</div>' }

const currentTabComponent = computed(() =>
  uiStore.homeTab === 'map' ? MapPlaceholder : CalendarPlaceholder
)

onMounted(() => {
  if (racesStore.races.length === 0) racesStore.loadRaces()
})
</script>
