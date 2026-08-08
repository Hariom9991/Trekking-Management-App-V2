<template>
  <div class="auth-shell">
    <div class="auth-visual">
      <div>
        <div class="mb-3 text-primary fs-2">
          <i class="bi bi-signpost-split"></i>
        </div>
        <h2>Create Trekker Account</h2>
        <p>Register as a trekker to browse, book, and track trekking adventures.</p>
      </div>
    </div>
    <div class="auth-card-wrapper">
      <div class="auth-card">
        <h3 class="mb-2">Register</h3>
        <p class="text-muted mb-4">Only trekkers can self-register.</p>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <form @submit.prevent="submitRegister" novalidate>
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input
              v-model="form.full_name"
              type="text"
              class="form-control"
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="form-control"
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              minlength="6"
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Contact Number</label>
            <input
              v-model="form.contact_number"
              type="text"
              class="form-control"
              required
            />
          </div>
          <button class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? 'Creating Account...' : 'Register' }}
          </button>
        </form>
        <div class="mt-3 text-center">
          Already have an account? <router-link to="/login">Login here</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({
  full_name: '',
  email: '',
  password: '',
  contact_number: '',
})

async function submitRegister() {
  error.value = ''
  loading.value = true
  try {
    await authApi.register({ ...form })
    alert('Registration successful. Please login.')
    router.push('/login')
  } catch (e) {
    error.value =
      e?.response?.data?.error ||
      (e?.response?.data?.errors || []).join(', ') ||
      'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>