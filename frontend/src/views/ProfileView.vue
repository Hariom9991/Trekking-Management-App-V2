<template>
  <SidebarLayout title="Profile" subtitle="Account" user="Account" :links="links"><div class="panel"><h5>Profile</h5><form class="row g-3 mt-1" @submit.prevent="save"><div class="col-md-6"><input v-model="form.full_name" class="form-control" placeholder="Full Name"></div><div class="col-md-6"><input v-model="form.email" class="form-control" disabled></div><div class="col-md-6"><input v-model="form.contact_number" class="form-control" placeholder="Contact Number"></div><div class="col-12"><button class="btn btn-primary">Update Profile</button></div></form></div></SidebarLayout>
</template>
<script setup>
import { onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import SidebarLayout from '../components/SidebarLayout.vue'
import { userApi, authApi } from '../services/api'
const router=useRouter(); const logout = async()=>{ await authApi.logout(); router.push('/login') }
const links=[{label:'Dashboard',to:'/user/dashboard',icon:'bi bi-grid'},{label:'Browse Treks',to:'/user/treks',icon:'bi bi-compass'},{label:'History',to:'/user/history',icon:'bi bi-clock-history'},{label:'Profile',to:'/user/profile',icon:'bi bi-person-circle'},{label:'Logout',icon:'bi bi-box-arrow-right',action:logout}]
const form=reactive({ full_name:'', email:'', contact_number:'' })
async function load(){ Object.assign(form,(await userApi.profile()).data) }
async function save(){ await userApi.updateProfile(form); alert('Profile updated successfully') }
onMounted(load)
</script>
