<template><div class="metric">
    <div class="small text-uppercase muted fw-semibold">{{ label }}

    </div><h3>
        {{ value }}</h3>
        </div></template><script setup>defineProps({ label: String, value: [String, Number] })
        </script>
