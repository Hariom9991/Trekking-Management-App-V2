<template>
  <div class="panel">
    <div class="d-flex justify-content-between align-items-center mb-3"><h5 class="mb-0">{{ title }}</h5></div>
    <div class="table-responsive">
      <table class="table align-middle">
        <thead><tr><th v-for="h in headers" :key="h">{{ h }}</th></tr></thead>
        <tbody>
          <tr v-if="!rows.length"><td :colspan="headers.length"><div class="empty-state">No records found.</div></td></tr>
          <tr v-for="(row,index) in rows" :key="index"><td v-for="(value,i) in row" :key="i">{{ value }}</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup>
defineProps({ title: String, headers: Array, rows: Array })
</script>
