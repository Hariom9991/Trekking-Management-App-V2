<template>
  <SidebarLayout
    title="Users (Trekkers)"
    subtitle="User Management"
    user="Admin"
    :links="links"
  >
    <div class="panel">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0">Users</h5>
        <input
          v-model="search"
          class="form-control"
          placeholder="Search users..."
          style="max-width:260px"
        >
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
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(u, index) in filteredUsers"
              :key="u.id"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ u.full_name }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.contact_number }}</td>
              <td>{{ u.status }}</td>
              <td>
                <button
                  class="btn btn-sm btn-outline-danger"
                  @click="toggleStatus(u)"
                >
                  {{ u.status === 'active' ? 'Blacklist' : 'Activate' }}
                </button>
              </td>
            </tr>
            <tr v-if="!filteredUsers.length">
              <td colspan="6" class="text-center text-muted">
                No users found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </SidebarLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
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
  {
    label: 'Users (Trekkers)',
    to: '/admin/users',
    icon: 'bi bi-person-lines-fill',
  },
  { label: 'Logout', icon: 'bi bi-box-arrow-right', action: logout },
]

const users = ref([])
const search = ref('')

const filteredUsers = computed(() =>
  users.value.filter((u) =>
    `${u.full_name} ${u.email} ${u.id}`
      .toLowerCase()
      .includes(search.value.toLowerCase()),
  ),
)

async function load() {
  const { data } = await adminApi.users()
  users.value = data.items || []
}

async function toggleStatus(u) {
  await adminApi.updateUserStatus(u.id, {
    status: u.status === 'active' ? 'blacklisted' : 'active',
  })
  await load()
}

onMounted(load)
</script>