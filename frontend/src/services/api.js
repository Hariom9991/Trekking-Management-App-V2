import axios from 'axios'

const hostname = window.location.hostname || '127.0.0.1'
export const API_ORIGIN = `http://${hostname}:5000`
const API_BASE = `${API_ORIGIN}/api`

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true
})

api.interceptors.response.use(
  response => response,
  error => {
    const currentPath = window.location.pathname || ''
    if (error?.response?.status === 401 && currentPath !== '/login' && currentPath !== '/register') {
      alert('Session expired or not logged in. Please login again.')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  register: payload => api.post('/auth/register', payload),
  login: payload => api.post('/auth/login', payload),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me')
}

export const adminApi = {
  dashboard: () => api.get('/admin/dashboard'),
  treks: () => api.get('/admin/treks'),
  createTrek: payload => api.post('/admin/treks', payload),
  updateTrek: (id, payload) => api.put(`/admin/treks/${id}`, payload),
  deleteTrek: id => api.delete(`/admin/treks/${id}`),
  staff: () => api.get('/admin/staff'),
  createStaff: payload => api.post('/admin/staff', payload),
  updateStaffStatus: (id, payload) => api.patch(`/admin/staff/${id}/status`, payload),
  users: () => api.get('/admin/users'),
  updateUserStatus: (id, payload) => api.patch(`/admin/users/${id}/status`, payload),
  search: q => api.get(`/admin/search?q=${encodeURIComponent(q)}`),
  reportSummary: () => api.get('/admin/reports/summary'),
  monthlyReportUrl: `${API_BASE}/admin/reports/monthly-html`
}

export const staffApi = {
  dashboard: () => api.get('/staff/dashboard'),
  treks: () => api.get('/staff/treks'),
  trek: id => api.get(`/staff/treks/${id}`),
  updateTrek: (id, payload) => api.put(`/staff/treks/${id}`, payload),
  participants: id => api.get(`/staff/treks/${id}/participants`)
}

export const userApi = {
  dashboard: () => api.get('/user/dashboard'),
  treks: params => api.get(`/user/treks${params || ''}`),
  bookings: () => api.get('/user/bookings'),
  book: payload => api.post('/user/bookings', payload),
  cancelBooking: id => api.post(`/user/bookings/${id}/cancel`),
  history: () => api.get('/user/history'),
  startExport: () => api.post('/user/export-history'),
  exportStatus: taskId => api.get(`/user/export-history/status?task_id=${encodeURIComponent(taskId)}`),
  profile: () => api.get('/user/profile'),
  updateProfile: payload => api.put('/user/profile', payload),
  notifications: () => api.get('/user/notifications')
}

export default api
