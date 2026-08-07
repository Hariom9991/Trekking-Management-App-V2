<template>
  <SidebarLayout title="My Dashboard" subtitle="Staff Panel" user="Staff" :links="links">
    <div class="grid-3 mb-4">
      <StatCard label="Assigned Treks" :value="stats.assigned_treks" />
      <StatCard label="Total Participants" :value="stats.participants" />
      <StatCard label="Ongoing Treks" :value="stats.ongoing" />
    </div>

    <div class="panel">
      <h5 class="mb-3">Assigned Treks Overview</h5>

      <div class="table-responsive">
        <table class="table align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Trek</th>
              <th>Dates</th>
              <th>Participants</th>
              <th>Slots</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="treks.length === 0">
              <td colspan="6" class="text-muted">No assigned treks found.</td>
            </tr>

            <tr v-for="t in treks" :key="t.id">
              <td>{{ t.id }}</td>
              <td>{{ t.trek_name }}</td>
              <td>{{ t.start_date || '-' }} to {{ t.end_date || '-' }}</td>
              <td>{{ t.participants }}</td>
              <td>{{ t.available_slots }}/{{ t.total_slots }}</td>
              <td class="text-capitalize">{{ t.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </SidebarLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import StatCard from '../components/StatCard.vue'
import { staffApi, authApi } from '../services/api'

const router = useRouter()

const logout = async () => {
  await authApi.logout()
  router.push('/login')
}

const links = [
  { label: 'Dashboard', to: '/staff/dashboard', icon: 'bi bi-grid' },
  { label: 'My Treks', to: '/staff/treks', icon: 'bi bi-map' },
  { label: 'Profile', to: '/staff/profile', icon: 'bi bi-person-circle' },
  { label: 'Logout', icon: 'bi bi-box-arrow-right', action: logout }
]

const stats = ref({
  assigned_treks: 0,
  participants: 0,
  ongoing: 0
})

const treks = ref([])

onMounted(async () => {
  try {
    const { data } = await staffApi.dashboard()
    stats.value = data.stats || { assigned_treks: 0, participants: 0, ongoing: 0 }
    treks.value = data.treks || []
  } catch (err) {
    alert(err?.response?.data?.error || 'Failed to load dashboard.')
  }
})
</script>