<script setup lang="ts">
// TODO: Implement loading spinner component
interface Props {
  size?: 'sm' | 'md' | 'lg'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'text-primary-600',
})

const sizes = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
}
</script>

<template>
  <div
    class="animate-spin rounded-full border-2 border-gray-200 border-t-current"
    :class="[sizes[size], color]"
  ></div>
</template>
