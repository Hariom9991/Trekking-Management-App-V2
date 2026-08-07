<template>
  <SidebarLayout
    title="Trekking History"
    subtitle="History"
    user="Trekker"
    :links="links"
  >
    <BookingTable
      title="Trekking History"
      :headers="['ID', 'Trek', 'Status', 'Booked On']"
      :rows="rows"
    />

    <div class="d-flex gap-2 mt-3">
      <button
        class="btn btn-outline-primary"
        :disabled="exportLoading"
        @click="startExport"
      >
        {{ exportLoading ? 'Exporting...' : 'Export CSV (Async)' }}
      </button>

      <button
        class="btn btn-outline-secondary"
        @click="loadNotifications"
      >
        Load Notifications
      </button>
    </div>

    <div class="panel mt-3" v-if="notifications.length">
      <h5>Notifications</h5>
      <ul class="mb-0">
        <li v-for="n in notifications" :key="n.id">
          {{ n.message }}
        </li>
      </ul>
    </div>
  </SidebarLayout>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import BookingTable from '../components/BookingTable.vue'
import { userApi, authApi, API_ORIGIN } from '../services/api'

const router = useRouter()

const rows = ref([])
const notifications = ref([])
const exportLoading = ref(false)
let pollInterval = null

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
  exportLoading.value = false
}

const logout = async () => {
  stopPolling()
  await authApi.logout()
  router.push('/login')
}

const links = [
  { label: 'Dashboard', to: '/user/dashboard', icon: 'bi bi-grid' },
  { label: 'Browse Treks', to: '/user/treks', icon: 'bi bi-compass' },
  { label: 'History', to: '/user/history', icon: 'bi bi-clock-history' },
  { label: 'Profile', to: '/user/profile', icon: 'bi bi-person-circle' },
  { label: 'Logout', icon: 'bi bi-box-arrow-right', action: logout }
]

async function load() {
  try {
    const { data } = await userApi.history()
    rows.value = (data.items || []).map((b) => [
      b.id,
      b.trek_name,
      b.status,
      b.booking_date
    ])
  } catch (error) {
    console.error('Failed to load history:', error)
    rows.value = []
  }
}

async function loadNotifications() {
  try {
    const { data } = await userApi.notifications()
    notifications.value = data.items || []
  } catch (error) {
    console.error('Failed to load notifications:', error)
    notifications.value = []
  }
}

async function startExport() {
  stopPolling()
  exportLoading.value = true

  try {
    const { data } = await userApi.startExport()
    const taskId = data.task_id

    pollInterval = setInterval(async () => {
      try {
        const res = await userApi.exportStatus(taskId)
        const status = res.data.status

        if (status === 'finished') {
          stopPolling()
          alert('CSV export is ready. Download will start now.')
          window.location.href = `${API_ORIGIN}${res.data.download_url}`
        } else if (status === 'failed') {
          stopPolling()
          alert('CSV export failed.')
        }
      } catch (error) {
        console.error('Export polling failed:', error)
        stopPolling()
      }
    }, 2000)
  } catch (error) {
    console.error('Failed to start export:', error)
    exportLoading.value = false
    alert('Failed to start export task.')
  }
}

onMounted(() => {
  load()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>