<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'

const { llmResult, isOptimizing, ruleResult } = useAnalysis()

const hasLLMResult = computed(() => llmResult.value !== null)
const canOptimize = computed(() => ruleResult.value !== null && !isOptimizing.value)
const isLoading = computed(() => isOptimizing.value)

// 学习建议数据
const learningAnalysis = computed(() => llmResult.value?.learning_analysis)
const errorPatterns = computed(() => learningAnalysis.value?.error_patterns || [])
const recommendations = computed(() => learningAnalysis.value?.learning_recommendations || [])
const personalizedTips = computed(() => learningAnalysis.value?.personalized_tips || [])
const historicalTrend = computed(() => learningAnalysis.value?.historical_trend)

// 优化建议
const suggestions = computed(() => llmResult.value?.suggestions || [])
const chineseCorrections = computed(() => llmResult.value?.chinese_corrections || [])
</script>

<template>
  <div class="bg-[rgba(30,58,95,0.35)] backdrop-blur-md border border-white/10 rounded-xl overflow-hidden h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-purple-400 animate-pulse" v-if="isLoading"></div>
        <h2 class="font-semibold text-white">AI 深度优化 (LLM)</h2>
      </div>
      <div v-if="hasLLMResult" class="flex items-center gap-2 text-xs text-slate-400">
        <span class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          {{ llmResult.token_usage }} tokens
        </span>
        <span class="text-slate-600">|</span>
        <span>{{ suggestions.length }} 条建议</span>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="flex-1 p-4 overflow-hidden flex flex-col">
      <!-- 空状态：等待规则检测完成 -->
      <div v-if="!canOptimize && !hasLLMResult && !isLoading" class="flex-1 flex items-center justify-center text-slate-400">
        <div class="text-center p-8">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center">
            <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
          <p class="text-lg font-medium text-slate-300 mb-2">等待规则检测完成</p>
          <p class="text-sm text-slate-500 max-w-xs mx-auto">
            完成 LanguageTool 检测后，可点击 AI 优化按钮进行深度分析
          </p>
        </div>
      </div>

      <!-- 空状态：可以开始优化 -->
      <div v-else-if="!hasLLMResult && !isLoading && canOptimize" class="flex-1 flex items-center justify-center text-slate-400">
        <div class="text-center p-8">
          <div class="w-20 h-20 mx-auto mb-6 relative">
            <div class="absolute inset-0 rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 animate-pulse"></div>
            <div class="absolute inset-2 rounded-full bg-slate-900/50 backdrop-blur-sm flex items-center justify-center">
              <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
          </div>
          <p class="text-lg font-medium text-slate-300 mb-3">准备进行 AI 优化</p>
          <p class="text-sm text-slate-500 max-w-xs mx-auto mb-6">
            点击中间的 "✨ AI 深度优化" 按钮，获取智能改写建议和个性化学习分析
          </p>
          <div class="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3 max-w-xs mx-auto">
            <div class="flex items-center gap-2 text-xs text-purple-300">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>预计消耗 {{ ruleResult?.estimated_llm_tokens || 15 }} tokens</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="isLoading" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="relative w-20 h-20 mx-auto mb-6">
            <div class="absolute inset-0 rounded-full border-4 border-slate-700"></div>
            <div class="absolute inset-0 rounded-full border-4 border-purple-500 border-t-transparent animate-spin"></div>
            <div class="absolute inset-2 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" style="animation-direction: reverse; animation-duration: 1s;"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
          </div>
          <p class="text-lg font-medium text-slate-300 mb-2">AI 正在分析上下文...</p>
          <p class="text-sm text-slate-500">生成个性化优化建议和学习分析</p>
        </div>
      </div>

      <!-- AI 优化结果 -->
      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <div class="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
          <!-- 句子级优化建议 -->
          <div v-if="suggestions.length > 0" class="space-y-3">
            <h3 class="text-sm font-semibold text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              优化建议
            </h3>
            <div
              v-for="(suggestion, index) in suggestions"
              :key="index"
              class="bg-[rgba(30,58,95,0.4)] border border-white/8 rounded-lg p-4"
            >
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span class="text-xs font-semibold text-purple-400">{{ index + 1 }}</span>
                </div>
                <div class="flex-1">
                  <div class="mb-3">
                    <p class="text-xs text-slate-500 mb-1">原文</p>
                    <p class="text-sm text-slate-400 font-mono">{{ suggestion.original }}</p>
                  </div>
                  <div class="mb-3">
                    <p class="text-xs text-slate-500 mb-1">AI 优化</p>
                    <p class="text-sm text-green-400 font-mono">{{ suggestion.suggestion }}</p>
                  </div>
                  <div class="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                    <div class="flex items-start gap-2">
                      <svg class="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                      </svg>
                      <div>
                        <p class="text-xs font-medium text-blue-300 mb-1">优化说明</p>
                        <p class="text-xs text-slate-400">{{ suggestion.explanation }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 中英混用纠正 -->
          <div v-if="chineseCorrections.length > 0" class="space-y-3">
            <h3 class="text-sm font-semibold text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/>
              </svg>
              中英混用纠正
            </h3>
            <div
              v-for="(correction, index) in chineseCorrections"
              :key="index"
              class="bg-pink-500/10 border border-pink-500/20 rounded-lg p-3"
            >
              <div class="flex items-center gap-2 text-sm">
                <span class="text-pink-400 font-mono">{{ correction.original }}</span>
                <svg class="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                </svg>
                <span class="text-green-400 font-mono">{{ correction.corrected }}</span>
              </div>
            </div>
          </div>

          <!-- 学习建议区域 -->
          <div v-if="learningAnalysis" class="space-y-4 pt-4 border-t border-slate-700/50">
            <h3 class="text-sm font-semibold text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              学习分析
            </h3>

            <!-- 错误模式分布 -->
            <div v-if="errorPatterns.length > 0" class="bg-[rgba(30,58,95,0.4)] border border-white/8 rounded-lg p-4">
              <h4 class="text-xs font-semibold text-slate-400 mb-3">📊 你的错误分布</h4>
              <div class="space-y-2">
                <div
                  v-for="pattern in errorPatterns"
                  :key="pattern.pattern_name"
                  class="flex items-center gap-3"
                >
                  <div class="flex-1">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs text-slate-300">{{ pattern.pattern_name }}</span>
                      <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-500">{{ pattern.frequency }}</span>
                        <span
                          class="w-4 h-4 rounded-full flex items-center justify-center text-xs"
                          :class="{
                            'bg-red-500/20 text-red-400': pattern.severity === 'high',
                            'bg-yellow-500/20 text-yellow-400': pattern.severity === 'medium',
                            'bg-green-500/20 text-green-400': pattern.severity === 'low'
                          }"
                        >
                          {{ pattern.severity === 'high' ? '🔴' : pattern.severity === 'medium' ? '🟡' : '🟢' }}
                        </span>
                      </div>
                    </div>
                    <div class="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all"
                        :class="{
                          'bg-red-500': pattern.severity === 'high',
                          'bg-yellow-500': pattern.severity === 'medium',
                          'bg-green-500': pattern.severity === 'low'
                        }"
                        :style="{ width: pattern.frequency }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 学习建议 -->
            <div v-if="recommendations.length > 0" class="space-y-3">
              <div
                v-for="rec in recommendations.slice(0, 2)"
                :key="rec.priority"
                class="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-lg p-4"
              >
                <div class="flex items-start gap-3 mb-3">
                  <div class="w-6 h-6 rounded-full bg-purple-500/30 flex items-center justify-center flex-shrink-0">
                    <span class="text-xs font-bold text-purple-300">{{ rec.priority }}</span>
                  </div>
                  <div class="flex-1">
                    <h4 class="text-sm font-semibold text-white mb-1">🎯 {{ rec.topic }}</h4>
                    <p class="text-xs text-slate-400">{{ rec.description }}</p>
                  </div>
                </div>

                <div v-if="rec.resources" class="space-y-2 mb-3">
                  <p class="text-xs font-medium text-slate-400">💡 学习资源</p>
                  <div
                    v-for="(resource, idx) in rec.resources.slice(0, 2)"
                    :key="idx"
                    class="text-xs text-slate-500 flex items-start gap-2"
                  >
                    <span class="text-blue-400">•</span>
                    <span>{{ resource.title }}</span>
                  </div>
                </div>

                <div class="flex items-center justify-between text-xs">
                  <span class="text-slate-500">预计学习时间</span>
                  <span class="text-purple-400 font-medium">{{ rec.estimated_study_time }}</span>
                </div>
              </div>
            </div>

            <!-- 进步趋势 -->
            <div v-if="historicalTrend" class="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
              <h4 class="text-xs font-semibold text-green-300 mb-3 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
                📈 进步趋势
              </h4>
              <div class="space-y-2 text-xs">
                <div class="flex items-center justify-between">
                  <span class="text-slate-400">较上周</span>
                  <span class="text-green-400 font-semibold">{{ historicalTrend.since_last_week }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-400">最大进步</span>
                  <span class="text-green-300">{{ historicalTrend.most_improved }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-400">需要关注</span>
                  <span class="text-yellow-300">{{ historicalTrend.needs_attention }}</span>
                </div>
              </div>
            </div>

            <!-- 个性化建议 -->
            <div v-if="personalizedTips.length > 0" class="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <h4 class="text-xs font-semibold text-blue-300 mb-3">💬 个性化建议</h4>
              <ul class="space-y-2">
                <li
                  v-for="(tip, index) in personalizedTips"
                  :key="index"
                  class="text-xs text-slate-400 flex items-start gap-2"
                >
                  <span class="text-blue-400 flex-shrink-0">•</span>
                  <span>{{ tip }}</span>
                </li>
              </ul>
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
  background: rgba(147, 51, 234, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(147, 51, 234, 0.5);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1.5s linear infinite;
}
</style>
