import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

/**
 * Route definitions
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: false, title: 'English Transfer Assistant' },
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/Auth.vue'),
    meta: { requiresAuth: false, title: 'Login / Register' },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { requiresAuth: true, title: 'Analysis History' },
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { requiresAuth: true, title: 'Error Statistics' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true, title: 'Settings' },
  },
  {
    path: '/split',
    name: 'SplitAnalysisNotion',
    component: () => import('@/views/SplitAnalysisNotion.vue'),
    meta: { requiresAuth: false, title: 'Split Analysis (Notion Sample)' },
  },
  {
    path: '/split-analysis',
    name: 'SplitAnalysis',
    component: () => import('@/views/SplitAnalysis.vue'),
    meta: { requiresAuth: false, title: 'Split Analysis' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/',
  },
]

/**
 * Create router instance
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

/**
 * Navigation guards
 */
router.beforeEach((to, _from, next) => {
  // Update page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - English Transfer Assistant`
  }

  // Check auth requirement
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    // Save intended redirect URL
    next({ name: 'Auth', query: { redirect: to.fullPath } })
  } else if (to.name === 'Auth' && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
