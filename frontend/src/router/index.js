import { createRouter, createWebHistory } from 'vue-router'
import { authApi } from '../services/api'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

import AdminDashboardView from '../views/AdminDashboardView.vue'
import AdminTreksView from '../views/AdminTreksView.vue'
import AdminStaffView from '../views/AdminStaffView.vue'
import AdminUsersView from '../views/AdminUsersView.vue'

import StaffDashboardView from '../views/StaffDashboardView.vue'
import StaffTreksView from '../views/StaffTreksView.vue'
import StaffManageTrekView from '../views/StaffManageTrekView.vue'
import StaffProfileView from '../views/StaffProfileView.vue'

import UserDashboardView from '../views/UserDashboardView.vue'
import BrowseTreksView from '../views/BrowseTreksView.vue'
import HistoryView from '../views/HistoryView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView, meta: { public: true } },
  { path: '/register', component: RegisterView, meta: { public: true } },

  { path: '/admin/dashboard', component: AdminDashboardView, meta: { role: 'admin' } },
  { path: '/admin/treks', component: AdminTreksView, meta: { role: 'admin' } },
  { path: '/admin/staff', component: AdminStaffView, meta: { role: 'admin' } },
  { path: '/admin/users', component: AdminUsersView, meta: { role: 'admin' } },

  { path: '/staff/dashboard', component: StaffDashboardView, meta: { role: 'staff' } },
  { path: '/staff/treks', component: StaffTreksView, meta: { role: 'staff' } },
  { path: '/staff/manage/:id', component: StaffManageTrekView, meta: { role: 'staff' } },
  { path: '/staff/profile', component: StaffProfileView, meta: { role: 'staff' } },

  { path: '/user/dashboard', component: UserDashboardView, meta: { role: 'user' } },
  { path: '/user/treks', component: BrowseTreksView, meta: { role: 'user' } },
  { path: '/user/history', component: HistoryView, meta: { role: 'user' } },
  { path: '/user/profile', component: ProfileView, meta: { role: 'user' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

  try {
    const { data } = await authApi.me()
    const role = data.user.role
    const allowed = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role]

    if (!allowed.includes(role)) {
      if (role === 'admin') return '/admin/dashboard'
      if (role === 'staff') return '/staff/dashboard'
      return '/user/dashboard'
    }

    return true
  } catch {
    return '/login'
  }
})

export default router