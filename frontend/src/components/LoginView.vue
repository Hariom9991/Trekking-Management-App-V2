<template>
  <section class="auth-wrap">
    <div class="auth-art"><div class="auth-card auth-visual"><div class="small text-uppercase text-primary fw-bold mb-2">Roles</div><div class="d-flex gap-2 flex-wrap mb-3"><span class="badge text-bg-light border">Admin</span><span class="badge text-bg-light border">Trekking Staff</span><span class="badge text-bg-light border">User (Trekker)</span></div><h2>Welcome Back!</h2><p class="muted">Login to your account and manage treks, staff, bookings, and reports.</p><div class="mountains"><div></div><div></div><div></div></div><div class="note-box mt-4">Only trekkers can register themselves. Trek staff are created by Admin.</div></div></div>
    <div class="auth-form"><div class="auth-card"><h2 class="mb-3">Sign in</h2><div v-if="error" class="alert alert-danger">{{ error }}</div><form class="row g-3" @submit.prevent="submit"><div class="col-12"><input v-model="form.email" type="email" class="form-control" placeholder="Email address" required></div><div class="col-12"><input v-model="form.password" type="password" class="form-control" placeholder="Password" required></div><div class="col-12"><button class="btn btn-primary w-100" :disabled="loading">{{ loading ? 'Logging in...' : 'Login' }}</button></div></form><p class="mt-3 mb-0">Don't have an account? <router-link to="/register">Register as User (Trekker)</router-link></p></div></div>
  </section>
</template>
<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'
const router = useRouter(); const loading = ref(false); const error = ref(''); const form = reactive({ email:'', password:'' })
async function submit(){ loading.value=true; error.value=''; try{ const {data}=await authApi.login(form); if(data.user.role==='admin') router.push('/admin/dashboard'); else if(data.user.role==='staff') router.push('/staff/dashboard'); else router.push('/user/dashboard') }catch(e){ error.value=e?.response?.data?.error || 'Login failed.' } finally{ loading.value=false } }
</script>
