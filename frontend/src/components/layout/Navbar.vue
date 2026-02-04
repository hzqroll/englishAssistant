<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useUIStore } from '@/stores/uiStore'

const { isAuthenticated, user, logout } = useAuth()
const uiStore = useUIStore()
</script>

<template>
  <nav class="fixed top-0 left-0 right-0 z-50 px-6 py-4 bg-[rgba(30,58,95,0.4)] backdrop-blur-md border-b border-white/10">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/>
          </svg>
        </div>
        <div>
          <span class="text-lg font-bold text-white">English Transfer</span>
          <span class="bg-gradient-to-r from-orange-500 to-orange-400 bg-clip-text text-transparent font-bold">Assistant</span>
        </div>
      </RouterLink>

      <!-- Navigation menu -->
      <div class="hidden md:flex items-center gap-6">
        <RouterLink to="/" class="text-slate-300 hover:text-white transition-colors">首页</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/history" class="text-slate-300 hover:text-white transition-colors">历史记录</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/statistics" class="text-slate-300 hover:text-white transition-colors">统计分析</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/settings" class="text-slate-300 hover:text-white transition-colors">设置</RouterLink>
      </div>

      <!-- Right side actions -->
      <div class="flex items-center gap-3">
        <!-- Settings button -->
        <RouterLink v-if="isAuthenticated" to="/settings" class="p-2 rounded-lg hover:bg-slate-700/50 transition-colors">
          <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </RouterLink>

        <!-- User menu or login button -->
        <div v-if="isAuthenticated" class="flex items-center gap-2">
          <span class="text-slate-300">{{ user?.username }}</span>
          <button
            @click="logout"
            class="px-5 py-2 rounded-lg text-white font-medium bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transition-all hover:-translate-y-px hover:shadow-lg hover:shadow-blue-500/30"
          >
            登出
          </button>
        </div>
        <button
          v-else
          @click="uiStore.openLoginModal()"
          class="px-5 py-2 rounded-lg text-white font-medium bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transition-all hover:-translate-y-px hover:shadow-lg hover:shadow-blue-500/30"
        >
          登录
        </button>
      </div>
    </div>
  </nav>
</template>
