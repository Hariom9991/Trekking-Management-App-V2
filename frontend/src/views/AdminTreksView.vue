<template>
  <SidebarLayout
    title="Treks"
    subtitle="Manage trekking routes and availability"
    user="Admin"
    :links="links"
  >
    <div class="row g-4">
      <div class="col-lg-4">
        <div class="panel">
          <h5 class="mb-3">{{ editingId ? 'Edit Trek' : 'Add New Trek' }}</h5>

          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>

          <form @submit.prevent="submitTrek" novalidate>
            <div class="row g-3">
              <div class="col-12">
                <input
                  v-model="form.trek_name"
                  class="form-control"
                  placeholder="Trek Name"
                  required
                >
              </div>
              <div class="col-12">
                <input
                  v-model="form.location"
                  class="form-control"
                  placeholder="Location"
                  required
                >
              </div>
              <div class="col-md-6">
                <select
                  v-model="form.difficulty"
                  class="form-select"
                  required
                >
                  <option value="">Difficulty</option>
                  <option>Easy</option>
                  <option>Moderate</option>
                  <option>Hard</option>
                </select>
              </div>
              <div class="col-md-6">
                <input
                  v-model="form.duration_days"
                  type="number"
                  min="1"
                  class="form-control"
                  placeholder="Duration (days)"
                  required
                >
              </div>
              <div class="col-md-6">
                <input
                  v-model="form.total_slots"
                  type="number"
                  min="1"
                  class="form-control"
                  placeholder="Total Slots"
                  required
                >
              </div>
              <div class="col-md-6">
                <input
                  v-model="form.available_slots"
                  type="number"
                  min="0"
                  class="form-control"
                  placeholder="Available Slots"
                  required
                >
              </div>
              <div class="col-md-6">
                <input
                  v-model="form.start_date"
                  type="date"
                  class="form-control"
                >
              </div>
              <div class="col-md-6">
                <input
                  v-model="form.end_date"
                  type="date"
                  class="form-control"
                >
              </div>
              <div class="col-md-6">
                <select
                  v-model="form.status"
                  class="form-select"
                  required
                >
                  <option value="">Status</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="open">Open</option>
                  <option value="closed">Closed</option>
                  <option value="ongoing">Ongoing</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div class="col-md-6">
                <select
                  v-model="form.assigned_staff_id"
                  class="form-select"
                >
                  <option value="">
                    Assigned Staff
                  </option>
                  <option
                    v-for="s in staffOptions"
                    :key="s.id"
                    :value="s.id"
                  >
                    {{ s.full_name }}
                  </option>
                </select>
              </div>
              <div class="col-12">
                <input
                  v-model="form.altitude"
                  class="form-control"
                  placeholder="Altitude"
                >
              </div>
              <div class="col-12">
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="3"
                  placeholder="Description"
                />
              </div>
            </div>

            <div class="d-flex gap-2 mt-3">
              <button class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Saving...' : (editingId ? 'Save Trek' : 'Create Trek') }}
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="resetForm"
              >
                {{ editingId ? 'Cancel Edit' : 'Reset' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="panel">
          <div
            class="d-flex justify-content-between align-items-center mb-3 gap-2 flex-wrap"
          >
            <h5 class="mb-0">All Treks</h5>
            <div class="d-flex gap-2">
              <input
                v-model="search"
                class="form-control"
                placeholder="Search treks or location"
                style="min-width:220px"
              >
              <button
                class="btn btn-outline-primary btn-sm"
                @click="loadTreks"
              >
                Refresh
              </button>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Trek</th>
                  <th>Location</th>
                  <th>Difficulty</th>
                  <th>Slots</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(trek, index) in filteredTreks"
                  :key="trek.id"
                >
                  <td>{{ index + 1 }}</td>
                  <td>{{ trek.trek_name }}</td>
                  <td>{{ trek.location }}</td>
                  <td>{{ trek.difficulty }}</td>
                  <td>
                    {{ trek.available_slots }} / {{ trek.total_slots }}
                  </td>
                  <td>
                    <span class="badge text-bg-light border text-capitalize">
                      {{ trek.status }}
                    </span>
                  </td>
                  <td class="d-flex gap-2">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="editTrek(trek)"
                    >
                      Edit
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteTrek(trek.id)"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
                <tr v-if="!filteredTreks.length">
                  <td colspan="7" class="text-center text-muted">
                    No treks found.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </SidebarLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import { adminApi, authApi } from '../services/api'

const router = useRouter()
const logout = async () => {
  await authApi.logout()
  router.push('/login')
}

const links = [
  { label: 'Dashboard', to: '/admin/dashboard', icon: 'bi bi-grid' },
  { label: 'Treks', to: '/admin/treks', icon: 'bi bi-map' },
  { label: 'Trekking Staff', to: '/admin/staff', icon: 'bi bi-people' },
  { label: 'Users', to: '/admin/users', icon: 'bi bi-person-badge' },
  { label: 'Logout', icon: 'bi bi-box-arrow-right', action: logout },
]

const treks = ref([])
const staffOptions = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const search = ref('')
const editingId = ref(null)

const form = reactive({
  trek_name: '',
  location: '',
  difficulty: '',
  duration_days: '',
  total_slots: '',
  available_slots: '',
  start_date: '',
  end_date: '',
  status: 'open',
  assigned_staff_id: '',
  altitude: '',
  description: '',
})

const filteredTreks = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return treks.value
  return treks.value.filter((t) =>
    [t.trek_name, t.location, t.difficulty, t.status, String(t.id)]
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function resetForm() {
  editingId.value = null
  form.trek_name = ''
  form.location = ''
  form.difficulty = ''
  form.duration_days = ''
  form.total_slots = ''
  form.available_slots = ''
  form.start_date = ''
  form.end_date = ''
  form.status = 'open'
  form.assigned_staff_id = ''
  form.altitude = ''
  form.description = ''
}

async function loadTreks() {
  const { data } = await adminApi.treks()
  treks.value = data.items || []
}

async function loadStaff() {
  const { data } = await adminApi.staff()
  staffOptions.value = (data.items || []).filter(
    (s) => s.status === 'active',
  )
}

function editTrek(trek) {
  editingId.value = trek.id
  form.trek_name = trek.trek_name || ''
  form.location = trek.location || ''
  form.difficulty = trek.difficulty || ''
  form.duration_days = trek.duration_days ?? ''
  form.total_slots = trek.total_slots ?? ''
  form.available_slots = trek.available_slots ?? ''
  form.start_date = trek.start_date || ''
  form.end_date = trek.end_date || ''
  form.status = trek.status || 'open'
  form.assigned_staff_id = trek.assigned_staff_id || ''
  form.altitude = trek.altitude || ''
  form.description = trek.description || ''
}

async function submitTrek() {
  error.value = ''
  success.value = ''

  if (
    !form.trek_name ||
    !form.location ||
    !form.difficulty ||
    !form.duration_days ||
    !form.total_slots ||
    form.available_slots === '' ||
    !form.status
  ) {
    error.value = 'Please fill all required fields.'
    return
  }

  loading.value = true
  try {
    const payload = { ...form }
    if (editingId.value) {
      await adminApi.updateTrek(editingId.value, payload)
      success.value = 'Trek updated successfully.'
    } else {
      await adminApi.createTrek(payload)
      success.value = 'Trek created successfully.'
    }
    resetForm()
    await loadTreks()
    await loadStaff()
  } catch (e) {
    error.value =
      e?.response?.data?.error ||
      (e?.response?.data?.errors || []).join(', ') ||
      'Failed to save trek.'
  } finally {
    loading.value = false
  }
}

async function deleteTrek(id) {
  if (!confirm('Delete this trek?')) return
  try {
    await adminApi.deleteTrek(id)
    await loadTreks()
  } catch (e) {
    alert(e?.response?.data?.error || 'Failed to delete trek.')
  }
}

onMounted(async () => {
  await loadTreks()
  await loadStaff()
})
</script>