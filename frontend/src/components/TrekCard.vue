<template>
  <div class="trek-card h-100">
    <div class="trek-cover"></div>
    <h5 class="mb-1">{{ trek.trek_name }}</h5>
    <div class="muted mb-2">{{ trek.location }}</div>
    <div class="small mb-2">{{ trek.difficulty }} · {{ trek.duration_days }} Days</div>
    <div class="small mb-3">Slots Left: {{ trek.available_slots }}</div>
    <button class="btn w-100" :class="disabled ? 'btn-outline-secondary' : 'btn-primary'" :disabled="disabled" @click="$emit('action', trek)">{{ actionText }}</button>
  </div>
</template>
<script setup>
defineProps({ trek: Object, actionText: String, disabled: Boolean })
defineEmits(['action'])
</script>
