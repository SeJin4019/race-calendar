<template>
  <div class="relative w-full h-full">
    <!-- Map container -->
    <div ref="mapContainer" class="w-full h-full" />

    <!-- Bottom sheet: selected race -->
    <Transition name="slide-up">
      <div
        v-if="selectedRace"
        class="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-lg p-4 z-10"
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

    <!-- No API key warning -->
    <div
      v-if="!apiKey"
      class="absolute inset-0 flex flex-col items-center justify-center bg-gray-100 text-center p-6"
    >
      <div class="text-4xl mb-3">🗺️</div>
      <p class="font-bold mb-1">카카오 지도 API 키가 필요해요</p>
      <p class="text-sm text-gray-500 mb-3">.env 파일에 VITE_KAKAO_MAP_KEY를 설정하세요</p>
      <a
        href="https://developers.kakao.com"
        target="_blank"
        class="text-blue-600 text-sm underline"
      >카카오 개발자 콘솔 →</a>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/80">
      <div class="text-gray-500 text-sm">지도 불러오는 중...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRacesStore } from '../stores/races'
import { useUiStore } from '../stores/ui'

const racesStore = useRacesStore()
const uiStore = useUiStore()

const mapContainer = ref(null)
const loading = ref(true)
const apiKey = import.meta.env.VITE_KAKAO_MAP_KEY

let map = null
const markers = new Map() // raceId → kakao marker

const selectedRace = computed(() =>
  uiStore.selectedRaceId ? racesStore.getRaceById(uiStore.selectedRaceId) : null
)

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

function loadKakaoScript() {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps) { resolve(); return }
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`
    script.onload = () => window.kakao.maps.load(resolve)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

function createMarkers(racesData) {
  if (!map || !window.kakao?.maps) return
  // Remove old markers
  markers.forEach(m => m.setMap(null))
  markers.clear()

  racesData.forEach(race => {
    if (!race.location?.lat || !race.location?.lng) return
    const position = new window.kakao.maps.LatLng(race.location.lat, race.location.lng)
    const marker = new window.kakao.maps.Marker({ position, map })
    window.kakao.maps.event.addListener(marker, 'click', () => {
      uiStore.selectRace(race.id)
    })
    markers.set(race.id, marker)
  })
}

async function initMap() {
  if (!apiKey || !mapContainer.value) return
  try {
    await loadKakaoScript()
    const center = new window.kakao.maps.LatLng(36.5, 127.8)
    map = new window.kakao.maps.Map(mapContainer.value, {
      center,
      level: 13
    })
    createMarkers(racesStore.races)
  } catch (e) {
    console.error('Kakao map init failed:', e)
  } finally {
    loading.value = false
  }
}

// Re-create markers when races load
watch(() => racesStore.races, (newRaces) => {
  if (newRaces.length > 0) createMarkers(newRaces)
}, { immediate: false })

onMounted(async () => {
  if (!apiKey) { loading.value = false; return }
  await initMap()
})

onUnmounted(() => {
  markers.forEach(m => m.setMap(null))
  markers.clear()
  map = null
})
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.25s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
}
</style>
