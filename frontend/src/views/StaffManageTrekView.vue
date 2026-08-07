<template>
  <SidebarLayout
    title="Manage Trek"
    subtitle="Staff Trek Control"
    user="Staff"
    :links="links"
  >
    <div class="two-col">
      <div class="panel">
        <h5>Trek Details</h5>

        <form class="row g-3 mt-1" @submit.prevent="save">
          <div class="col-12">
            <input
              v-model="trek.trek_name"
              class="form-control"
              disabled
            >
          </div>

          <div class="col-md-6">
            <input
              v-model.number="trek.available_slots"
              type="number"
              class="form-control"
              placeholder="Available Slots"
              min="0"
            >
          </div>

          <div class="col-md-6">
            <select v-model="trek.status" class="form-select">
              <option value="open">open</option>
              <option value="closed">closed</option>
              <option value="ongoing">ongoing</option>
              <option value="completed">completed</option>
            </select>
          </div>

          <div class="col-12">
            <button class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Updating...' : 'Update Trek' }}
            </button>
          </div>
        </form>
      </div>

      <div class="panel">
        <h5>Participants</h5>

        <div class="table-responsive mt-3">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr v-if="participants.length === 0">
                <td colspan="3" class="text-muted">No participants found.</td>
              </tr>

              <tr v-for="p in participants" :key="p.id">
                <td>{{ p.full_name }}</td>
                <td>{{ p.email }}</td>
                <td>{{ p.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </SidebarLayout>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import { staffApi, authApi } from '../services/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const participants = ref([])

const trek = reactive({
  id: null,
  trek_name: '',
  available_slots: 0,
  status: 'open'
})

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

async function load() {
  const trekId = route.params.id

  if (!trekId) {
    alert('No trek selected.')
    router.push('/staff/dashboard')
    return
  }

  try {
    const trekRes = await staffApi.trek(trekId)
    Object.assign(trek, trekRes.data)

    const participantRes = await staffApi.participants(trekId)
    participants.value = participantRes.data.items || []
  } catch (err) {
    alert(err?.response?.data?.error || 'Failed to load trek.')
    router.push('/staff/dashboard')
  }
}

async function save() {
  const trekId = route.params.id

  if (!trekId) {
    alert('Invalid trek ID.')
    return
  }

  try {
    loading.value = true
    await staffApi.updateTrek(trekId, {
      available_slots: trek.available_slots,
      status: trek.status
    })
    await load()
    alert('Trek updated successfully.')
  } catch (err) {
    alert(err?.response?.data?.error || 'Failed to update trek.')
  } finally {
    loading.value = false
  }
}

onMounted(load)

watch(() => route.params.id, () => {
  load()
})
</script>