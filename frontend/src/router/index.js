import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import store from '../store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue')
  },
  {
    path: '/websites',
    name: 'ResourceWebsite',
    component: () => import('@/views/ResourceWebsite.vue'),
    children: [
      { path: '', redirect: '/websites/programming', component: () => import('@/views/navigation/ProgrammingResources.vue')  },
      { path: 'programming', component: () => import('@/views/navigation/ProgrammingResources.vue') },
      { path: 'general-tools', component: () => import('@/views/navigation/GeneralToolsResources.vue') },
      { path: 'ai-tools', component: () => import('@/views/navigation/AIToolsResources.vue') }
    ]
  },
  {
    path: '/memory-tool',
    name: 'MemoryTool',
    component: () => import('@/views/MemoryTool.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/self-test',
    name: 'SelfTest',
    component: () => import('../views/SelfTest.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/personal-trait',
    name: 'PersonalTrait',
    component: () => import('../views/PersonalTrait.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/learning-path',
    name: 'LearningPath',
    component: () => import('../views/LearningPath.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/search',
    name: 'SearchResults',
    component: () => import('@/views/SearchResults.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'personal-info',
        component: () => import('@/views/profile/SelectedCourses.vue')
      },
      {
        path: 'selected-courses',
        component: () => import('@/views/profile/SelectedCourses.vue')
      },
      {
        path: 'interests',
        component: () => import('@/views/profile/Interests.vue')
      },
      {
        path: 'achievement-diary',
        name: 'AchievementDiary',
        component: () => import('../views/profile/AchievementDiary.vue')
      },
      {
        path: 'todo',
        name: 'TodoList',
        component: () => import('../views/profile/TodoList.vue')
      },
      {
        path: 'learning-pbl',
        component: () => import('@/views/profile/LearningPBL.vue')
      },
      {
        path: 'settings',
        component: () => import('@/views/profile/Settings.vue')
      },
      {
        path: '',
        redirect: '/profile/personal-info'
      }
    ]
  },
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('@/views/Courses.vue'),
    meta: { requiresAuth: true },
    props: (route) => ({
      category: route.query.category || '',
      platform: route.query.platform || '',
      page: parseInt(route.query.page) || 1,
      keyword: route.query.keyword || ''
    })
  },
  {
    path: '/courses/:id',
    name: 'CourseDetail',
    component: () => import('@/views/courses/CourseDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters['auth/isLoggedIn']) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router