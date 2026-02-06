<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAnalysis, useUI } from '@/composables'
import type { CorrectionMode } from '@/stores/types'

const { analyzeText, isAnalyzing } = useAnalysis()
const { showSuccess, showError, showToast } = useUI()

const text = ref('')
const selectedMode = ref<CorrectionMode>('accuracy')
const maxLength = 5000
const minLength = 10

const charCount = computed(() => text.value.length)
const canAnalyze = computed(() => {
  return !isAnalyzing.value &&
         text.value.trim().length >= minLength &&
         text.value.length <= maxLength
})

const modeDescriptions = {
  accuracy: '纠正语法错误，保留原本风格',
  naturalness: '改写成地道表达，可能调整结构'
}

watch(text, (newValue) => {
  if (newValue.length > maxLength) {
    text.value = newValue.slice(0, maxLength)
    showToast('文本超出 5000 字符限制，请分段处理', 'warning')
  }
})

async function handleAnalyze() {
  if (!text.value.trim()) {
    showError('请输入或粘贴文本')
    return
  }

  if (text.value.trim().length < minLength) {
    showError(`请至少输入 ${minLength} 个字符`)
    return
  }

  try {
    await analyzeText(text.value, selectedMode.value)
    showSuccess('分析完成')
  } catch (err: any) {
    showError(err.message || '分析失败')
  }
}

function clearText() {
  text.value = ''
}
</script>

<template>
  <div class="bg-[rgba(30,58,95,0.35)] backdrop-blur-md border border-white/10 rounded-xl overflow-hidden h-full">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
      <h2 class="font-semibold text-white">文本输入</h2>
      <button
        v-if="text"
        @click="clearText"
        class="p-1 hover:bg-slate-700/50 rounded transition-colors"
        title="清空"
      >
        <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- 内容区 -->
    <div class="p-4">
      <!-- 纠正模式切换 -->
      <div class="bg-[rgba(30,58,95,0.5)] border border-white/10 rounded-lg p-1 mb-4">
        <div class="flex gap-1">
          <button
            @click="selectedMode = 'accuracy'"
            class="flex-1 px-3 py-2 rounded text-sm font-medium transition-all"
            :class="selectedMode === 'accuracy'
              ? 'bg-[rgba(59,130,246,0.2)] border border-blue-500 text-white'
              : 'text-slate-300 hover:bg-slate-700/50'"
          >
            🎯 准确性优先
          </button>
          <button
            @click="selectedMode = 'naturalness'"
            class="flex-1 px-3 py-2 rounded text-sm font-medium transition-all"
            :class="selectedMode === 'naturalness'
              ? 'bg-[rgba(59,130,246,0.2)] border border-blue-500 text-white'
              : 'text-slate-300 hover:bg-slate-700/50'"
          >
            ✨ 自然度优先
          </button>
        </div>
        <p class="text-xs text-slate-400 mt-2 px-2">
          {{ modeDescriptions[selectedMode] }}
        </p>
      </div>

      <!-- 输入框 -->
      <textarea
        v-model="text"
        class="w-full h-64 bg-slate-900/50 border border-slate-700 rounded-lg p-4 text-slate-200 text-sm resize-none focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/10 transition-all"
        placeholder="粘贴任何英文文本...

支持：
• 对话（A: ... B: ...）
• 邮件、作文、演讲稿
• 日常表达
• 中英夹杂

AI 会自动识别文本类型并纠错"
        :disabled="isAnalyzing"
      ></textarea>

      <!-- 字符计数 -->
      <div class="flex justify-between items-center mt-2 text-xs text-slate-400">
        <span>{{ charCount }} / 5000</span>
        <span class="text-slate-500">字符</span>
      </div>

      <!-- 操作按钮 -->
      <div class="mt-4 space-y-2">
        <button
          @click="handleAnalyze"
          :disabled="!canAnalyze"
          class="w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="canAnalyze ? 'hover:-translate-y-px hover:shadow-lg hover:shadow-blue-500/30 text-white' : ''"
        >
          <svg v-if="!isAnalyzing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          {{ isAnalyzing ? '分析中...' : '分析文本' }}
        </button>

        <div class="flex gap-2">
          <button class="flex-1 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            导入文件
          </button>
          <button
            @click="clearText"
            class="flex-1 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
            清空
          </button>
        </div>
      </div>

      <!-- 支持格式 -->
      <div class="mt-4 pt-4 border-t border-slate-700/50">
        <p class="text-xs text-slate-500 mb-2">支持格式</p>
        <div class="flex flex-wrap gap-2">
          <span class="px-2 py-1 bg-slate-800/50 rounded text-xs text-slate-400">TXT</span>
          <span class="px-2 py-1 bg-slate-800/50 rounded text-xs text-slate-400">JSON</span>
          <span class="px-2 py-1 bg-slate-800/50 rounded text-xs text-slate-400">Markdown</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin { animation: spin 0.8s linear infinite; }
</style>
