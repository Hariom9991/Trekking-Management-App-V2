<template>
  <SidebarLayout
    title="Trekking Staff"
    subtitle="Create and manage staff"
    user="Admin"
    :links="links"
  >
    <div class="row g-4">
      <div class="col-lg-4">
        <div class="panel">
          <h5 class="mb-3">Create New Trekking Staff</h5>

          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>

          <form @submit.prevent="submitStaff" novalidate>
            <div class="row g-3">
              <div class="col-12">
                <input
                  v-model="form.full_name"
                  class="form-control"
                  placeholder="Full Name"
                  required
                >
              </div>
              <div class="col-12">
                <input
                  v-model="form.email"
                  type="email"
                  class="form-control"
                  placeholder="Email Address"
                  required
                >
              </div>
              <div class="col-12">
                <input
                  v-model="form.contact_number"
                  class="form-control"
                  placeholder="Contact Number"
                  required
                >
              </div>
              <div class="col-12">
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  placeholder="Password"
                  minlength="6"
                  required
                >
              </div>
              <div class="col-12">
                <input
                  v-model="form.experience"
                  class="form-control"
                  placeholder="Experience (e.g. 5 years)"
                >
              </div>
              <div class="col-12">
                <input
                  v-model="form.specialization"
                  class="form-control"
                  placeholder="Specialization"
                >
              </div>
              <div class="col-12">
                <select v-model="form.status" class="form-select">
                  <option value="active">Active</option>
                  <option value="blacklisted">Blacklisted</option>
                </select>
              </div>
            </div>

            <div class="d-flex gap-2 mt-3">
              <button class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Creating...' : 'Create Staff' }}
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="resetForm"
              >
                Reset
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
            <h5 class="mb-0">Trekking Staff List</h5>
            <div class="d-flex gap-2">
              <input
                v-model="search"
                class="form-control"
                placeholder="Search by name or email"
                style="min-width:220px"
              >
              <button
                class="btn btn-outline-primary btn-sm"
                @click="loadStaff"
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
                  <th>Name</th>
                  <th>Email</th>
                  <th>Contact</th>
                  <th>Status</th>
                  <th>Experience</th>
                  <th>Specialization</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(s, index) in filteredStaff"
                  :key="s.id"
                >
                  <td>{{ index + 1 }}</td>
                  <td>{{ s.full_name }}</td>
                  <td>{{ s.email }}</td>
                  <td>{{ s.contact_number }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="s.status === 'active' ? 'text-bg-success' : 'text-bg-danger'"
                    >
                      {{ s.status }}
                    </span>
                  </td>
                  <td>{{ s.experience || '-' }}</td>
                  <td>{{ s.specialization || '-' }}</td>
                  <td>
                    <button
                      v-if="s.status === 'active'"
                      class="btn btn-sm btn-outline-danger"
                      @click="toggleStaffStatus(s.id, 'blacklisted')"
                    >
                      Blacklist
                    </button>
                    <button
                      v-else
                      class="btn btn-sm btn-outline-success"
                      @click="toggleStaffStatus(s.id, 'active')"
                    >
                      Activate
                    </button>
                  </td>
                </tr>
                <tr v-if="!filteredStaff.length">
                  <td colspan="8" class="text-center text-muted">
                    No staff found.
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

const loading = ref(false)
const error = ref('')
const success = ref('')
const search = ref('')
const staff = ref([])

const form = reactive({
  full_name: '',
  email: '',
  contact_number: '',
  password: '',
  experience: '',
  specialization: '',
  status: 'active',
})

const filteredStaff = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return staff.value
  return staff.value.filter((s) =>
    [s.full_name, s.email, s.contact_number, s.specialization]
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function resetForm() {
  form.full_name = ''
  form.email = ''
  form.contact_number = ''
  form.password = ''
  form.experience = ''
  form.specialization = ''
  form.status = 'active'
}

async function loadStaff() {
  try {
    const { data } = await adminApi.staff()
    staff.value = data.items || []
  } catch (e) {
    error.value =
      e?.response?.data?.error || 'Failed to load staff list.'
  }
}

async function submitStaff() {
  error.value = ''
  success.value = ''

  if (!form.full_name || !form.email || !form.contact_number || !form.password) {
    error.value = 'Please fill all required fields.'
    return
  }

  loading.value = true
  try {
    await adminApi.createStaff({ ...form })
    success.value = 'Staff created successfully.'
    resetForm()
    await loadStaff()
  } catch (e) {
    error.value =
      e?.response?.data?.error ||
      (e?.response?.data?.errors || []).join(', ') ||
      'Failed to create staff.'
  } finally {
    loading.value = false
  }
}

async function toggleStaffStatus(staffId, status) {
  error.value = ''
  success.value = ''
  try {
    await adminApi.updateStaffStatus(staffId, { status })
    success.value =
      status === 'blacklisted'
        ? 'Staff blacklisted successfully.'
        : 'Staff activated successfully.'
    await loadStaff()
  } catch (e) {
    error.value =
      e?.response?.data?.error || 'Failed to update staff status.'
  }
}

onMounted(() => {
  loadStaff()
})
</script>