<script setup lang="ts">
import { RouterView } from 'vue-router'
import LoginModal from '@/components/auth/LoginModal.vue'
import Toast from '@/components/common/Toast.vue'
import { useUIStore } from '@/stores/uiStore'

const uiStore = useUIStore()
</script>

<template>
  <div id="app" class="min-h-screen">
    <RouterView />
    <LoginModal />
    
    <!-- Toast notifications -->
    <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      <Toast
        v-for="toast in uiStore.toasts"
        :key="toast.id"
        :message="toast.message"
        :type="toast.type"
        :duration="toast.duration"
        @close="uiStore.removeToast(toast.id)"
      />
    </div>
  </div>
</template>
