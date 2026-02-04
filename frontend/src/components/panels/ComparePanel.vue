<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'
import type { ViewMode } from '@/stores/types'
import ErrorHighlight from '@/components/errors/ErrorHighlight.vue'

interface Props {
  showActions?: boolean
}

withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<{
  save: [result: any]
  export: [result: any]
  reanalyze: [text: string]
}>()

const { currentResult, viewMode, setViewMode } = useAnalysis()

const hasResult = computed(() => currentResult.value !== null)
const originalText = computed(() => currentResult.value?.originalText || '')
const correctedText = computed(() => currentResult.value?.correctedText || '')

const viewModes = [
  { key: 'side-by-side', label: '并排对照', icon: '⇄' },
  { key: 'original-only', label: '仅原文', icon: '⎔' },
  { key: 'corrected-only', label: '仅纠正后', icon: '✓' }
] as const

const stats = computed(() => {
  if (!currentResult.value) return null

  return {
    totalErrors: currentResult.value.errors.length,
    grammar: currentResult.value.errors.filter(e => e.type === 'grammar').length,
    tense: currentResult.value.errors.filter(e => e.type === 'tense').length,
    wordChoice: currentResult.value.errors.filter(e => e.type === 'word_choice').length,
    spelling: currentResult.value.errors.filter(e => e.type === 'spelling').length,
    punctuation: currentResult.value.errors.filter(e => e.type === 'punctuation').length,
    style: currentResult.value.errors.filter(e => e.type === 'style').length,
    mixed: currentResult.value.errors.filter(e => e.type === 'mixed_language' || e.type === 'chinese').length
  }
})

function setView(mode: ViewMode) {
  setViewMode(mode)
}

function handleSave() {
  emit('save', currentResult.value)
}

function handleExport() {
  emit('export', currentResult.value)
}

function handleReanalyze() {
  emit('reanalyze', originalText.value)
}
</script>

<template>
  <div class="bg-[rgba(30,58,95,0.35)] backdrop-blur-md border border-white/10 rounded-xl overflow-hidden h-full">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
      <h2 class="font-semibold text-white">纠错对照</h2>
      <button class="p-1 hover:bg-slate-700/50 rounded transition-colors">
        <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
    </div>

    <!-- 内容区 -->
    <div class="p-4">
      <div v-if="!hasResult" class="flex-1 flex items-center justify-center text-slate-400">
        <div class="text-center p-8">
          <div class="text-4xl mb-4">📄</div>
          <p class="text-lg font-medium text-slate-300">等待分析结果</p>
          <p class="text-sm text-slate-500 mt-2">在左侧输入文本开始分析</p>
        </div>
      </div>

      <div v-else class="flex-1 flex flex-col">
        <!-- 视图切换 -->
        <div class="flex gap-2 mb-4">
          <button
            v-for="mode in viewModes"
            :key="mode.key"
            @click="setView(mode.key as ViewMode)"
            class="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all border border-white/10"
            :class="viewMode === mode.key
              ? 'bg-[rgba(59,130,246,0.2)] border-blue-500 text-blue-400'
              : 'bg-transparent text-slate-300 hover:bg-blue-500/10'"
          >
            {{ mode.icon }} {{ mode.label }}
          </button>
        </div>

        <!-- 错误统计面板 -->
        <div v-if="stats" class="grid grid-cols-4 gap-2 mb-4">
          <div class="bg-[rgba(30,58,95,0.3)] border border-white/8 rounded-lg p-3 text-center hover:bg-[rgba(59,130,246,0.12)] hover:border-blue-500/30 transition-all">
            <div class="text-xs text-slate-400 mb-1">━━</div>
            <div class="text-2xl font-bold text-red-400">{{ stats.grammar }}</div>
            <div class="text-xs text-slate-500">语法</div>
          </div>
          <div class="bg-[rgba(30,58,95,0.3)] border border-white/8 rounded-lg p-3 text-center hover:bg-[rgba(59,130,246,0.12)] hover:border-blue-500/30 transition-all">
            <div class="text-xs text-slate-400 mb-1">Ab</div>
            <div class="text-2xl font-bold text-yellow-400">{{ stats.spelling }}</div>
            <div class="text-xs text-slate-500">拼写</div>
          </div>
          <div class="bg-[rgba(30,58,95,0.3)] border border-white/8 rounded-lg p-3 text-center hover:bg-[rgba(59,130,246,0.12)] hover:border-blue-500/30 transition-all">
            <div class="text-xs text-slate-400 mb-1">↻</div>
            <div class="text-2xl font-bold text-orange-400">{{ stats.tense }}</div>
            <div class="text-xs text-slate-500">时态</div>
          </div>
          <div class="bg-[rgba(30,58,95,0.3)] border border-white/8 rounded-lg p-3 text-center hover:bg-[rgba(59,130,246,0.12)] hover:border-blue-500/30 transition-all">
            <div class="text-xs text-slate-400 mb-1">文</div>
            <div class="text-2xl font-bold text-pink-400">{{ stats.mixed }}</div>
            <div class="text-xs text-slate-500">中英混用</div>
          </div>
        </div>

        <!-- 对照内容 -->
        <div class="flex-1 overflow-y-auto space-y-3 mb-4 custom-scrollbar">
          <ErrorHighlight
            :original-text="originalText"
            :corrected-text="correctedText"
            :errors="currentResult.errors"
            :view-mode="viewMode"
          />
        </div>

        <!-- 底部操作 -->
        <div v-if="showActions" class="pt-4 border-t border-slate-700/50 flex gap-2">
          <button
            @click="handleExport"
            class="flex-1 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            导出
          </button>
          <button
            @click="handleSave"
            class="flex-1 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
            </svg>
            保存
          </button>
          <button
            @click="handleReanalyze"
            class="flex-1 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            重新分析
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(30, 58, 95, 0.2);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.5);
}
</style>
