<template>
  <SidebarLayout
    title="Management App"
    subtitle="Staff Panel"
    user="TREKKING"
    :links="links"
  >
    <div class="panel">
      <h4 class="mb-3">Profile</h4>

      <form class="row g-3" @submit.prevent="saveProfile">
        <div class="col-md-6">
          <label class="form-label">Full Name</label>
          <input v-model="form.full_name" class="form-control" />
        </div>

        <div class="col-md-6">
          <label class="form-label">Email</label>
          <input v-model="form.email" class="form-control" disabled />
        </div>

        <div class="col-md-6">
          <label class="form-label">Contact Number</label>
          <input v-model="form.contact_number" class="form-control" />
        </div>

        <div class="col-12">
          <button class="btn btn-primary">Update Profile</button>
        </div>
      </form>
    </div>
  </SidebarLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import { userApi, authApi } from '../services/api'

const router = useRouter()

const form = ref({
  full_name: '',
  email: '',
  contact_number: ''
})

const logout = async () => {
  await authApi.logout()
  router.push('/login')
}

const links = [
  { label: 'Dashboard', to: '/staff/dashboard', icon: 'bi bi-grid' },
  { label: 'My Treks', to: '/staff/manage', icon: 'bi bi-map' },
  { label: 'Profile', to: '/staff/profile', icon: 'bi bi-person-circle' },
  { label: 'Logout', icon: 'bi bi-box-arrow-right', action: logout }
]

async function loadProfile() {
  const { data } = await userApi.profile()
  form.value = {
    full_name: data.full_name || '',
    email: data.email || '',
    contact_number: data.contact_number || ''
  }
}

async function saveProfile() {
  await userApi.updateProfile(form.value)
  alert('Profile updated successfully.')
}

onMounted(loadProfile)
</script>