<template>
  <AppLayout>
    <div class="flex flex-col h-full">
      <CalendarView class="flex-1 overflow-hidden" />
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRacesStore } from '../stores/races'
import AppLayout from '../components/AppLayout.vue'
import CalendarView from '../components/CalendarView.vue'

const racesStore = useRacesStore()

onMounted(() => {
  if (racesStore.races.length === 0) racesStore.loadRaces()
})
</script>
