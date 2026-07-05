import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue')
        },
        {
          path: '/roads',
          name: 'Roads',
          component: () => import('@/views/Roads.vue')
        },
        {
          path: '/traffic',
          name: 'Traffic',
          component: () => import('@/views/Traffic.vue')
        },
        {
          path: '/events',
          name: 'Events',
          component: () => import('@/views/Events.vue')
        },
        {
          path: '/smart-traffic',
          name: 'SmartTraffic',
          component: () => import('@/views/SmartTraffic.vue')
        },
        {
          path: '/route-plan',
          name: 'RoutePlan',
          component: () => import('@/views/RoutePlan.vue')
        },
        {
          path: '/admin',
          name: 'Admin',
          component: () => import('@/views/Admin.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/analytics',
          name: 'Analytics',
          component: () => import('@/views/Analytics.vue')
        },
        {
          path: '/advanced-analytics',
          name: 'AdvancedAnalytics',
          component: () => import('@/views/AdvancedAnalytics.vue')
        },
        {
          path: '/data-export',
          name: 'DataExport',
          component: () => import('@/views/DataExport.vue')
        },
        {
          path: '/profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')

  console.log(`[Router] 导航到: ${to.path}, 需要认证: ${to.meta.requiresAuth}`)

  if (to.meta.requiresAuth) {
    if (!token) {
      console.log('[Router] 没有token，重定向到登录')
      next('/login')
    } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
      console.log('[Router] 不是管理员，重定向到首页')
      next('/')
    } else {
      console.log('[Router] 认证通过，继续导航')
      next()
    }
  } else {
    if (token && (to.path === '/login' || to.path === '/register')) {
      console.log('[Router] 已登录，重定向到首页')
      next('/')
    } else {
      next()
    }
  }
})

router.afterEach((to, from) => {
  console.log(`[Router] 导航完成: ${from.path} -> ${to.path}`)
})

export default router
