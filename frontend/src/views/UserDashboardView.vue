<template>
  <SidebarLayout
    title="Welcome"
    subtitle="Trekker Panel"
    user="Trekker"
    :links="links"
  >
    <div class="banner d-flex justify-content-between align-items-center gap-3">
      <div>
        <h5 class="mb-1">Available Treks</h5>
        <p class="muted mb-0">Browse approved and open treks.</p>
      </div>
      <router-link to="/user/treks" class="btn btn-primary">
        Browse Treks
      </router-link>
    </div>
    <div class="grid-3 my-4">
      <StatCard label="Available Treks" :value="stats.available_treks" />
      <StatCard label="My Bookings" :value="stats.my_bookings" />
      <StatCard label="Completed Treks" :value="stats.completed_treks" />
    </div>
    <BookingTable
      title="My Bookings"
      :headers="['ID', 'Trek', 'Status', 'Payment']"
      :rows="rows"
    />
  </SidebarLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import StatCard from '../components/StatCard.vue'
import BookingTable from '../components/BookingTable.vue'
import { userApi, authApi } from '../services/api'

const router = useRouter()

const logout = async () => {
  await authApi.logout()
  router.push('/login')
}

const links = [
  { label: 'Dashboard', to: '/user/dashboard', icon: 'bi bi-grid' },
  { label: 'Browse Treks', to: '/user/treks', icon: 'bi bi-compass' },
  { label: 'History', to: '/user/history', icon: 'bi bi-clock-history' },
  { label: 'Profile', to: '/user/profile', icon: 'bi bi-person-circle' },
  { label: 'Logout', icon: 'bi bi-box-arrow-right', action: logout },
]

const stats = ref({ available_treks: 0, my_bookings: 0, completed_treks: 0 })
const rows = ref([])

onMounted(async () => {
  const { data } = await userApi.dashboard()
  stats.value = data.stats
  rows.value = (data.bookings || []).map((b) => [
    b.id,
    b.trek_name,
    b.status,
    b.payment_status,
  ])
})
</script>