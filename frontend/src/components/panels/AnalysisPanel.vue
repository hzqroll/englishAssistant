<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'

const { currentResult } = useAnalysis()

const hasResult = computed(() => currentResult.value !== null)

const stats = computed(() => {
  if (!currentResult.value) return null

  return {
    grammar: currentResult.value.errors.filter(e => e.type === 'grammar'),
    tense: currentResult.value.errors.filter(e => e.type === 'tense'),
    wordChoice: currentResult.value.errors.filter(e => e.type === 'word_choice'),
    spelling: currentResult.value.errors.filter(e => e.type === 'spelling'),
    punctuation: currentResult.value.errors.filter(e => e.type === 'punctuation'),
    style: currentResult.value.errors.filter(e => e.type === 'style'),
    mixed: currentResult.value.errors.filter(e => e.type === 'mixed_language' || e.type === 'chinese')
  }
})

const errorCategories = computed(() => {
  if (!stats.value) return []

  return [
    {
      key: 'grammar',
      name: '语法错误',
      englishName: 'Grammar',
      icon: '━━',
      colorClass: 'red',
      borderClass: 'error-card-grammar',
      bgClass: 'bg-red-500/20',
      count: stats.value.grammar.length,
      errors: stats.value.grammar
    },
    {
      key: 'spelling',
      name: '拼写错误',
      englishName: 'Spelling',
      icon: 'Ab',
      colorClass: 'yellow',
      borderClass: 'error-card-spelling',
      bgClass: 'bg-yellow-500/20',
      count: stats.value.spelling.length,
      errors: stats.value.spelling
    },
    {
      key: 'tense',
      name: '时态错误',
      englishName: 'Tense',
      icon: '↻',
      colorClass: 'orange',
      borderClass: 'error-card-tense',
      bgClass: 'bg-orange-500/20',
      count: stats.value.tense.length,
      errors: stats.value.tense
    },
    {
      key: 'wordChoice',
      name: '单词选择',
      englishName: 'Word Choice',
      icon: 'Aa',
      colorClass: 'purple',
      borderClass: 'error-card-word',
      bgClass: 'bg-purple-500/20',
      count: stats.value.wordChoice.length,
      errors: stats.value.wordChoice
    },
    {
      key: 'punctuation',
      name: '标点符号',
      englishName: 'Punctuation',
      icon: '.,',
      colorClass: 'gray',
      borderClass: 'error-card-punctuation',
      bgClass: 'bg-gray-500/20',
      count: stats.value.punctuation.length,
      errors: stats.value.punctuation
    },
    {
      key: 'style',
      name: '风格建议',
      englishName: 'Style',
      icon: '✨',
      colorClass: 'emerald',
      borderClass: 'error-card-style',
      bgClass: 'bg-emerald-500/20',
      count: stats.value.style.length,
      errors: stats.value.style
    },
    {
      key: 'mixed',
      name: '中英混用',
      englishName: 'Mixed Language',
      icon: '文',
      colorClass: 'pink',
      borderClass: 'error-card-mixed',
      bgClass: 'bg-pink-500/20',
      count: stats.value.mixed.length,
      errors: stats.value.mixed
    }
  ].filter(cat => cat.count > 0)
})
</script>

<template>
  <div class="bg-[rgba(30,58,95,0.35)] backdrop-blur-md border border-white/10 rounded-xl overflow-hidden h-full">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
      <h2 class="font-semibold text-white">错误分析</h2>
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
          <div class="text-4xl mb-4">📊</div>
          <p class="text-lg font-medium text-slate-300">暂无分析结果</p>
          <p class="text-sm text-slate-500 mt-2">分析完成后这里会显示详细错误</p>
        </div>
      </div>

      <div v-else class="flex-1 flex flex-col h-full">
        <!-- 搜索和筛选 -->
        <div class="flex gap-2 mb-4">
          <input
            type="text"
            placeholder="搜索错误..."
            class="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/10 transition-all"
          >
          <button class="px-3 py-2 rounded-lg bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all">
            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
            </svg>
          </button>
        </div>

        <!-- 错误卡片列表 -->
        <div class="flex-1 overflow-y-auto space-y-3 pr-2 mb-4 custom-scrollbar">
          <div
            v-for="category in errorCategories"
            :key="category.key"
            class="bg-[rgba(30,58,95,0.4)] border border-white/8 rounded-lg p-4 hover:bg-[rgba(30,58,95,0.5)] hover:border-blue-500/30 transition-all"
            :class="category.borderClass"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <div :class="`w-8 h-8 rounded-lg ${category.bgClass} flex items-center justify-center`">
                  <span class="text-xs text-slate-400">{{ category.icon }}</span>
                </div>
                <div>
                  <div class="font-medium text-white text-sm">{{ category.name }}</div>
                  <div class="text-xs text-slate-500">{{ category.englishName }}</div>
                </div>
              </div>
              <span :class="`px-2 py-1 ${category.bgClass} rounded text-xs font-semibold text-${category.colorClass}-400`">
                {{ category.count }}
              </span>
            </div>

            <div class="space-y-2">
              <div
                v-for="(error, index) in category.errors.slice(0, 3)"
                :key="index"
                class="bg-slate-900/50 rounded p-3"
              >
                <p class="text-sm text-slate-300 mb-1">
                  <span :class="`text-${category.colorClass}-400`">{{ error.originalText }}</span> →
                  <span class="text-green-400">{{ error.correctedText }}</span>
                </p>
                <p class="text-xs text-slate-500">{{ error.message }}</p>
              </div>

              <div v-if="category.errors.length > 3" class="text-xs text-slate-500 text-center py-2">
                还有 {{ category.errors.length - 3 }} 个类似错误...
              </div>
            </div>
          </div>
        </div>

        <!-- 学习建议 -->
        <div class="pt-4 border-t border-slate-700/50">
          <div class="bg-[rgba(59,130,246,0.08)] backdrop-blur-sm border border-blue-500/15 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              <span class="text-sm font-medium text-white">学习建议</span>
            </div>
            <p class="text-xs text-slate-400 mb-2">你最容易犯时态错误（43%）</p>
            <p class="text-xs text-slate-500 mb-3">建议重点复习不规则动词表和过去时态用法</p>
            <button class="w-full py-2 rounded-lg text-sm font-medium bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white transition-all hover:-translate-y-px hover:shadow-lg hover:shadow-blue-500/30">
              开始练习 →
            </button>
          </div>
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

.error-card-grammar { border-left: 3px solid rgb(248, 113, 113); }
.error-card-tense { border-left: 3px solid rgb(251, 146, 60); }
.error-card-word { border-left: 3px solid rgb(167, 139, 250); }
.error-card-mixed { border-left: 3px solid rgb(244, 114, 182); }
.error-card-spelling { border-left: 3px solid rgb(234, 179, 8); }
.error-card-punctuation { border-left: 3px solid rgb(107, 114, 128); }
.error-card-style { border-left: 3px solid rgb(16, 185, 129); }
</style>
