import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../views/RaceListView.vue'),
    meta: { title: '대회 목록' }
  },
  {
    path: '/map',
    component: () => import('../views/HomeView.vue'),
    meta: { title: '지도' }
  },
  {
    path: '/races',
    redirect: '/'
  },
  {
    path: '/races/:id',
    component: () => import('../views/RaceDetailView.vue'),
    meta: { title: '대회 상세' }
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} | 마라톤 코리아` : '마라톤 코리아'
})

export default router
