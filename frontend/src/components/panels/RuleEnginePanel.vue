<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'

const { ruleResult, isAnalyzing } = useAnalysis()

const searchQuery = ref('')
const selectedCategory = ref<string | null>(null)

const hasResult = computed(() => ruleResult.value !== null)
const isLoading = computed(() => isAnalyzing.value && !ruleResult.value)

const stats = computed(() => {
  if (!ruleResult.value) return null

  const errors = ruleResult.value.errors || []

  return {
    grammar: errors.filter((e: any) => e.category === 'GRAMMAR'),
    spelling: errors.filter((e: any) => e.category === 'TYPOS'),
    tense: errors.filter((e: any) => e.ruleId?.includes('TENSE') || e.message?.includes('tense')),
    wordChoice: errors.filter((e: any) => e.category === 'STYLE'),
    punctuation: errors.filter((e: any) => e.category === 'PUNCTUATION'),
    casing: errors.filter((e: any) => e.category === 'CASING'),
  }
})

const errorCategories = computed(() => {
  if (!stats.value) return []

  const categories = [
    {
      key: 'grammar',
      name: '语法错误',
      englishName: 'Grammar',
      icon: '━━',
      colorClass: 'red',
      borderClass: 'error-card-grammar',
      bgClass: 'bg-red-500/20',
      count: stats.value.grammar.length,
      errors: stats.value.grammar,
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
      errors: stats.value.spelling,
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
      errors: stats.value.tense,
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
      errors: stats.value.wordChoice,
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
      errors: stats.value.punctuation,
    },
    {
      key: 'casing',
      name: '大小写',
      englishName: 'Casing',
      icon: 'Aa',
      colorClass: 'blue',
      borderClass: 'error-card-casing',
      bgClass: 'bg-blue-500/20',
      count: stats.value.casing.length,
      errors: stats.value.casing,
    },
  ]

  return categories.filter(cat => cat.count > 0)
})
</script>

<template>
  <div class="bg-[rgba(30,58,95,0.35)] backdrop-blur-md border border-white/10 rounded-xl overflow-hidden h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-green-400 animate-pulse" v-if="isLoading"></div>
        <h2 class="font-semibold text-white">规则检测 (LanguageTool)</h2>
      </div>
      <div v-if="ruleResult" class="flex items-center gap-2 text-xs text-slate-400">
        <span class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ (ruleResult.processing_time_ms / 1000).toFixed(1) }}秒
        </span>
        <span class="text-slate-600">|</span>
        <span class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ ruleResult.statistics?.total_errors || 0 }} 个错误
        </span>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="flex-1 p-4 overflow-hidden flex flex-col">
      <!-- 空状态：等待分析 -->
      <div v-if="!hasResult && !isLoading" class="flex-1 flex items-center justify-center text-slate-400">
        <div class="text-center p-8">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-800/50 flex items-center justify-center">
            <svg class="w-8 h-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <p class="text-lg font-medium text-slate-300 mb-2">等待规则检测</p>
          <p class="text-sm text-slate-500 max-w-xs mx-auto">
            输入文本并点击分析按钮，LanguageTool 将快速检测语法、拼写和标点错误
          </p>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="isLoading" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="relative w-16 h-16 mx-auto mb-4">
            <div class="absolute inset-0 rounded-full border-4 border-slate-700"></div>
            <div class="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
          </div>
          <p class="text-lg font-medium text-slate-300 mb-2">规则检测中...</p>
          <p class="text-sm text-slate-500">LanguageTool 正在分析文本</p>
        </div>
      </div>

      <!-- 分析结果 -->
      <div v-else class="flex-1 flex flex-col h-full overflow-hidden">
        <!-- 搜索栏 -->
        <div class="flex gap-2 mb-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索错误类型或规则 ID..."
            class="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/10 transition-all"
          >
          <button
            class="px-3 py-2 rounded-lg bg-[rgba(71,85,105,0.5)] border border-white/10 hover:bg-[rgba(71,85,105,0.7)] hover:border-blue-500/30 transition-all"
            title="筛选"
          >
            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
            </svg>
          </button>
        </div>

        <!-- 错误分类卡片 -->
        <div class="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
          <div
            v-for="category in errorCategories"
            :key="category.key"
            class="bg-[rgba(30,58,95,0.4)] border border-white/8 rounded-lg overflow-hidden hover:bg-[rgba(30,58,95,0.5)] transition-all"
            :class="category.borderClass"
          >
            <!-- 分类头部 -->
            <button
              @click="selectedCategory = selectedCategory === category.key ? null : category.key"
              class="w-full px-4 py-3 flex items-center justify-between hover:bg-white/5 transition-colors"
            >
              <div class="flex items-center gap-2">
                <div :class="`w-8 h-8 rounded-lg ${category.bgClass} flex items-center justify-center`">
                  <span class="text-xs text-slate-400">{{ category.icon }}</span>
                </div>
                <div class="text-left">
                  <div class="font-medium text-white text-sm">{{ category.name }}</div>
                  <div class="text-xs text-slate-500">{{ category.englishName }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="`px-2 py-1 ${category.bgClass} rounded text-xs font-semibold text-${category.colorClass}-400`">
                  {{ category.count }}
                </span>
                <svg
                  class="w-4 h-4 text-slate-500 transition-transform"
                  :class="{ 'rotate-180': selectedCategory === category.key }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
            </button>

            <!-- 展开的错误详情 -->
            <div
              v-if="selectedCategory === category.key"
              class="border-t border-slate-700/50 bg-slate-900/30"
            >
              <div class="p-3 space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                <div
                  v-for="(error, index) in category.errors"
                  :key="index"
                  class="bg-slate-900/50 rounded-lg p-3 border border-slate-800 hover:border-slate-700 transition-colors"
                >
                  <div class="flex items-start justify-between gap-2 mb-2">
                    <div class="flex-1">
                      <p class="text-sm text-slate-300 mb-1">
                        <span :class="`text-${category.colorClass}-400 font-medium`">{{ error.original_text || error.context }}</span>
                        <svg class="w-4 h-4 inline mx-1 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                        </svg>
                        <span class="text-green-400 font-medium">{{ error.replacements?.[0] || '' }}</span>
                      </p>
                      <p class="text-xs text-slate-500">{{ error.message }}</p>
                    </div>
                    <span :class="`px-2 py-0.5 rounded text-xs font-medium ${category.bgClass} text-${category.colorClass}-400`">
                      {{ error.severity || 'ERROR' }}
                    </span>
                  </div>

                  <!-- 规则信息 -->
                  <div v-if="error.rule_id" class="flex items-center gap-2 text-xs text-slate-600 mt-2 pt-2 border-t border-slate-800">
                    <code class="px-1.5 py-0.5 bg-slate-800 rounded text-slate-500">{{ error.rule_id }}</code>
                    <span>•</span>
                    <span class="text-slate-600">{{ error.category }}</span>
                  </div>
                </div>

                <div v-if="category.errors.length === 0" class="text-center py-4 text-slate-500 text-sm">
                  该分类下没有错误
                </div>
              </div>
            </div>
          </div>

          <!-- 无错误提示 -->
          <div v-if="errorCategories.length === 0" class="text-center py-8">
            <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-green-500/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <p class="text-slate-300 font-medium">没有发现错误</p>
            <p class="text-sm text-slate-500 mt-1">LanguageTool 未检测到语法或拼写问题</p>
          </div>
        </div>

        <!-- 底部统计 -->
        <div v-if="ruleResult && errorCategories.length > 0" class="pt-4 border-t border-slate-700/50 mt-4">
          <div class="bg-[rgba(59,130,246,0.08)] backdrop-blur-sm border border-blue-500/15 rounded-lg p-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="text-sm text-slate-300">已完成规则检测</span>
              </div>
              <span class="text-xs text-slate-500">如需深度优化，可使用 AI 分析</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(30, 58, 95, 0.2);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.5);
}

.error-card-grammar { border-left: 3px solid rgb(248, 113, 113); }
.error-card-tense { border-left: 3px solid rgb(251, 146, 60); }
.error-card-word { border-left: 3px solid rgb(167, 139, 250); }
.error-card-spelling { border-left: 3px solid rgb(234, 179, 8); }
.error-card-punctuation { border-left: 3px solid rgb(107, 114, 128); }
.error-card-casing { border-left: 3px solid rgb(96, 165, 250); }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
