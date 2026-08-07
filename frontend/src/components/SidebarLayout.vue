<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand-card">
        <div class="brand-badge"><i class="bi bi-signpost-split"></i></div>
        <div>
          <div class="small text-uppercase text-primary fw-bold">Trekking</div>
          <h5 class="mb-0">Management App</h5>
          <small class="muted">{{ subtitle }}</small>
        </div>
      </div>
      <div class="nav-group">
        <template v-for="link in links" :key="link.label">
          <button v-if="link.action" class="nav-link-lite border-0 w-100 text-start" @click="link.action"><i :class="link.icon"></i><span>{{ link.label }}</span></button>
          <router-link v-else :to="link.to" class="nav-link-lite"><i :class="link.icon"></i><span>{{ link.label }}</span></router-link>
        </template>
      </div>
    </aside>
    <main class="content">
      <div class="brand-card topbar">
        <div>
          <div class="small text-uppercase text-primary fw-bold">Trekking Management Application</div>
          <h3 class="mb-0">{{ title }}</h3>
        </div>
        <div class="user-chip"><i class="bi bi-person-circle me-2"></i>{{ user }}</div>
      </div>
      <section class="mt-3"><slot /></section>
    </main>
  </div>
</template>
<script setup>
defineProps({ title: String, subtitle: String, user: String, links: Array })
</script>
