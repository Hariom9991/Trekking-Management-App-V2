<template>
  <SidebarLayout title="Dashboard" subtitle="Admin Panel" user="Admin" :links="links"><div class="grid-4 mb-4"><StatCard label="Total Treks" :value="stats.treks" /><StatCard label="Total Users" :value="stats.users" /><StatCard label="Total Staff" :value="stats.staff" /><StatCard label="Total Bookings" :value="stats.bookings" /></div><div class="two-col"><BookingTable title="Recent Bookings" :headers="['ID','User','Trek','Status','Payment']" :rows="recentRows" /><div class="panel"><div class="d-flex justify-content-between align-items-center gap-2 flex-wrap"><h5 class="mb-0">Popular Treks</h5><a :href="reportUrl" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm">Open Monthly Report</a></div><div class="chart-wrap mt-3"><canvas ref="chartRef" class="chart-box"></canvas></div></div></div></SidebarLayout>
</template>
<script setup>
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import SidebarLayout from '../components/SidebarLayout.vue'
import StatCard from '../components/StatCard.vue'
import BookingTable from '../components/BookingTable.vue'
import { adminApi, authApi } from '../services/api'
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)
const router = useRouter()
const logout = async()=>{ await authApi.logout(); router.push('/login') }
const links=[{label:'Dashboard',to:'/admin/dashboard',icon:'bi bi-grid'},{label:'Treks',to:'/admin/treks',icon:'bi bi-map'},{label:'Trekking Staff',to:'/admin/staff',icon:'bi bi-people'},{label:'Users (Trekkers)',to:'/admin/users',icon:'bi bi-person-lines-fill'},{label:'Logout',icon:'bi bi-box-arrow-right',action:logout}]
const stats = ref({ treks:0, users:0, staff:0, bookings:0 }); const recentRows = ref([]); const reportUrl = adminApi.monthlyReportUrl; const chartRef = ref(null); let chartInstance = null
onMounted(async()=>{ const { data } = await adminApi.dashboard(); stats.value = data.stats || { treks:0, users:0, staff:0, bookings:0 }; recentRows.value = (data.recent_bookings || []).map(b => [b.id, b.user_name, b.trek_name, b.status, b.payment_status]); await nextTick(); if (chartInstance) { chartInstance.destroy(); chartInstance = null } if (chartRef.value) { chartInstance = new Chart(chartRef.value, { type: 'bar', data: { labels: Object.keys(data.popular_treks || {}), datasets: [{ label: 'Bookings', data: Object.values(data.popular_treks || {}), backgroundColor: '#2e6bff' }] }, options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } } }) } })
onBeforeUnmount(() => { if (chartInstance) chartInstance.destroy() })
</script>
