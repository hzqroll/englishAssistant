<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import LoginModal from '@/components/auth/LoginModal.vue'
import Toast from '@/components/common/Toast.vue'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'

const uiStore = useUIStore()
const authStore = useAuthStore()

onMounted(async () => {
  // Try to restore auth state if token exists
  if (localStorage.getItem('auth_token')) {
    await authStore.fetchUserProfile()
  }
})
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
        :toast="toast"
      />
    </div>
  </div>
</template>
