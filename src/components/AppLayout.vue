<template>
  <div class="flex flex-col overflow-hidden bg-gray-50" style="position: fixed; inset: 0; padding-top: env(safe-area-inset-top)">
    <!-- Stale data warning -->
    <div v-if="racesStore.isStale" class="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-sm text-yellow-800 text-center">
      ⚠️ 데이터가 오래되었습니다. 새로고침 해보세요.
    </div>

    <!-- Main content -->
    <main class="flex-1 overflow-hidden">
      <slot />
    </main>

    <!-- Bottom navigation -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex z-50" style="padding-bottom: env(safe-area-inset-bottom)">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex-1 flex flex-col items-center py-2 text-xs gap-1 transition-colors"
        :class="[isActive(item.to) ? 'text-blue-600' : 'text-gray-500']"
      >
        <span class="text-xl">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { useRacesStore } from '../stores/races'
import { useRoute, RouterLink } from 'vue-router'

const racesStore = useRacesStore()
const $route = useRoute()

function isActive(to) {
  if (to === '/') return $route.path === '/' || $route.path.startsWith('/races')
  return $route.path === to
}

const navItems = [
  { to: '/', icon: '📋', label: '목록' },
  { to: '/map', icon: '📅', label: '달력' }
]
</script>
