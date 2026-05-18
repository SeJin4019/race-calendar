import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STALE_THRESHOLD_MS = 7 * 24 * 60 * 60 * 1000 // 7 days

export const useRacesStore = defineStore('races', () => {
  const races = ref([])
  const lastUpdated = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Filters
  const filterCity = ref([])
  const filterDistances = ref([])
  const filterStatus = ref('접수중')
  const filterDateFrom = ref('')
  const filterDateTo = ref('')
  const filterDays = ref([])
  const hideEnded = ref(true)
  const searchQuery = ref('')

  const isStale = computed(() => {
    if (!lastUpdated.value) return false
    return Date.now() - new Date(lastUpdated.value).getTime() > STALE_THRESHOLD_MS
  })

  const cities = computed(() => {
    const set = new Set(races.value.map(r => r.location?.province).filter(Boolean))
    return [...set].sort()
  })

  const filteredRaces = computed(() => {
    const todayStr = new Date().toISOString().slice(0, 10)
    return races.value.filter(race => {
      if (hideEnded.value && race.date < todayStr) return false
      if (filterCity.value.length > 0 && !filterCity.value.includes(race.location?.province)) return false
      if (filterDistances.value.length > 0 && !filterDistances.value.some(d => race.distances?.includes(d))) return false
      if (filterStatus.value && race.status !== filterStatus.value) return false
      if (filterDateFrom.value && race.date < filterDateFrom.value) return false
      if (filterDateTo.value && race.date > filterDateTo.value) return false
      if (filterDays.value.length > 0) {
        const day = new Date(race.date + 'T00:00:00').getDay()
        if (!filterDays.value.includes(day)) return false
      }
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        if (!race.name?.toLowerCase().includes(q) && !race.location?.city?.toLowerCase().includes(q) && !race.location?.province?.toLowerCase().includes(q)) return false
      }
      return true
    })
  })

  function sanitizeUrl(url) {
    if (!url) return ''
    try {
      const { protocol } = new URL(url)
      return (protocol === 'http:' || protocol === 'https:') ? url : ''
    } catch {
      return ''
    }
  }

  async function loadRaces() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${import.meta.env.BASE_URL}races.json`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      races.value = (data.races || []).map(r => ({
        ...r,
        registration_url: sanitizeUrl(r.registration_url),
        source_url: sanitizeUrl(r.source_url)
      }))
      lastUpdated.value = data.last_updated || null
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  function getRaceById(id) {
    return races.value.find(r => r.id === id)
  }

  return {
    races, lastUpdated, loading, error,
    filterCity, filterDistances, filterStatus, filterDateFrom, filterDateTo, filterDays, hideEnded, searchQuery,
    isStale, cities, filteredRaces,
    loadRaces, getRaceById
  }
})
