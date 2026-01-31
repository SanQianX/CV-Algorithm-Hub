import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/stock-monitor',
      name: 'stock-monitor',
      component: () => import('../views/StockMonitorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/fund-monitor',
      name: 'fund-monitor',
      component: () => import('../views/FundMonitorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/DataAnalyticsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/database',
      name: 'database',
      component: () => import('../views/DatabaseManagerView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/explorer',
      name: 'explorer',
      component: () => import('../views/DataExplorerView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/alerts',
      name: 'alerts',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guard for authentication
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Initialize auth state if not already done
  if (!authStore.token && localStorage.getItem('token')) {
    await authStore.initAuth()
  }

  // Check if we have a token in localStorage (even if API validation failed)
  const hasTokenInStorage = !!localStorage.getItem('token')
  const isAuthenticated = authStore.isAuthenticated || hasTokenInStorage
  const isGuestOnly = to.matched.some(record => record.meta.guest)

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (isGuestOnly && isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
