import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useFavoritesStore = defineStore('favorites', () => {
  const ids = ref(JSON.parse(localStorage.getItem('fav-races') || '[]'))

  function toggle(id) {
    const idx = ids.value.indexOf(id)
    if (idx === -1) ids.value.push(id)
    else ids.value.splice(idx, 1)
    localStorage.setItem('fav-races', JSON.stringify(ids.value))
  }

  function has(id) {
    return ids.value.includes(id)
  }

  return { ids, toggle, has }
})
