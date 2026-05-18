<template>
  <div class="relative w-full h-full">
    <l-map
      ref="mapRef"
      :zoom="7"
      :center="[36.5, 127.8]"
      :use-global-leaflet="false"
      class="w-full h-full"
    >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        layer-type="base"
        name="OpenStreetMap"
      />

      <l-marker
        v-for="race in mappableRaces"
        :key="race.id"
        :lat-lng="[race.location.lat, race.location.lng]"
        @click="onMarkerClick(race)"
      >
        <l-tooltip>{{ race.name }}</l-tooltip>
      </l-marker>
    </l-map>

    <!-- Bottom sheet: selected race -->
    <Transition name="slide-up">
      <div
        v-if="selectedRace"
        class="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-lg p-4 z-[1000]"
      >
        <div class="flex justify-between items-start mb-2">
          <h3 class="font-bold text-base leading-tight pr-4">{{ selectedRace.name }}</h3>
          <button @click="uiStore.clearSelection()" class="text-gray-400 text-xl leading-none">✕</button>
        </div>
        <p class="text-sm text-gray-600 mb-1">📅 {{ formatDate(selectedRace.date) }}</p>
        <p class="text-sm text-gray-600 mb-3">📍 {{ selectedRace.location?.address }}</p>
        <div class="flex gap-2 flex-wrap mb-3">
          <span
            v-for="d in selectedRace.distances"
            :key="d"
            class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
          >{{ d }}</span>
          <span
            class="px-2 py-0.5 rounded-full text-xs font-medium"
            :class="statusClass(selectedRace.status)"
          >{{ selectedRace.status }}</span>
        </div>
        <RouterLink
          :to="`/races/${selectedRace.id}`"
          class="block w-full text-center bg-blue-600 text-white py-2 rounded-lg text-sm font-medium"
        >
          상세보기
        </RouterLink>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { LMap, LTileLayer, LMarker, LTooltip } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import { useRacesStore } from '../stores/races'
import { useUiStore } from '../stores/ui'

const racesStore = useRacesStore()
const uiStore = useUiStore()
const mapRef = ref(null)

const mappableRaces = computed(() =>
  racesStore.races.filter(r => r.location?.lat && r.location?.lng)
)

const selectedRace = computed(() =>
  uiStore.selectedRaceId ? racesStore.getRaceById(uiStore.selectedRaceId) : null
)

function onMarkerClick(race) {
  uiStore.selectRace(race.id)
}

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
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.25s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
}
</style>
