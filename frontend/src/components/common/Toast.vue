<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useUI } from '@/composables/useUI'
import type { ToastMessage } from '@/stores/types'

// TODO: Implement toast notification component
interface Props {
  toast: ToastMessage
}

const props = defineProps<Props>()
const emit = defineEmits<{
  remove: []
}>()

const { removeToast } = useUI()

const icons = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

const colors = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  warning: 'bg-yellow-500',
  info: 'bg-blue-500',
}

let timer: number | null = null

onMounted(() => {
  if (props.toast.duration && props.toast.duration > 0) {
    timer = window.setTimeout(() => {
      removeToast(props.toast.id)
    }, props.toast.duration)
  }
})

onUnmounted(() => {
  if (timer) {
    clearTimeout(timer)
  }
})

function handleRemove() {
  if (timer) {
    clearTimeout(timer)
  }
  removeToast(props.toast.id)
}
</script>

<template>
  <div
    class="flex items-center space-x-3 p-4 rounded-lg shadow-lg text-white min-w-[300px] max-w-md"
    :class="colors[toast.type]"
  >
    <span class="text-xl">{{ icons[toast.type] }}</span>
    <p class="flex-1">{{ toast.message }}</p>
    <button
      @click="handleRemove"
      class="text-white hover:text-gray-200"
    >
      ✕
    </button>
  </div>
</template>
