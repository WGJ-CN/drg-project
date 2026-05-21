<template>
  <component :is="currentLayout" />
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PCLayout from '../layouts/PCLayout.vue'
import MobileLayout from '../layouts/MobileLayout.vue'
import { getDeviceType } from '../utils/device'

const deviceType = ref('pc')

onMounted(() => {
  deviceType.value = getDeviceType()
})

const currentLayout = computed(() => {
  return deviceType.value === 'mobile' ? MobileLayout : PCLayout
})
</script>