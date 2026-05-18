import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const selectedRaceId = ref(null)
  const homeTab = ref('map') // 'map' | 'calendar'

  function selectRace(id) { selectedRaceId.value = id }
  function clearSelection() { selectedRaceId.value = null }
  function setTab(tab) { homeTab.value = tab }

  return { selectedRaceId, homeTab, selectRace, clearSelection, setTab }
})
