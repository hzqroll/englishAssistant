<script setup lang="ts">
import { onMounted } from 'vue'
import { useUI } from '@/composables/useUI'
import Navbar from '@/components/layout/Navbar.vue'
import MainLayout from '@/components/layout/MainLayout.vue'
import LayoutControls from '@/components/layout/LayoutControls.vue'

const { loadDarkModePreference } = useUI()

onMounted(() => {
  loadDarkModePreference()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-[#1e3a5f] to-slate-900">
    <Navbar />

    <main class="pt-24 px-6 pb-8">
      <div class="max-w-7xl mx-auto">
        <!-- 页面标题 -->
        <div class="text-center mb-6">
          <h1 class="text-3xl font-bold text-white mb-2">
            <span class="bg-gradient-to-r from-blue-400 to-blue-300 bg-clip-text text-transparent">AI文本纠错</span>
            <span class="text-white">与分析</span>
          </h1>
          <p class="text-slate-400 text-base">粘贴任何英文文本，智能纠错并深度分析错误</p>
        </div>

        <!-- Layout controls -->
        <LayoutControls class="mb-6" />

        <!-- Main layout with three panels -->
        <MainLayout />
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="mt-8 px-6 py-4 border-t border-slate-800">
      <div class="max-w-7xl mx-auto flex items-center justify-between text-sm text-slate-500">
        <p>© 2025 English Transfer Assistant. All rights reserved.</p>
        <div class="flex gap-6">
          <a href="#" class="hover:text-slate-400 transition-colors">隐私政策</a>
          <a href="#" class="hover:text-slate-400 transition-colors">服务条款</a>
          <a href="#" class="hover:text-slate-400 transition-colors">联系我们</a>
        </div>
      </div>
    </footer>
  </div>
</template>
