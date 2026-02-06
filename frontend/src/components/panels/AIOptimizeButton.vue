<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'

const { ruleResult, llmResult, isOptimizing, optimizeWithLLM } = useAnalysis()

// Button states
const canOptimize = computed(() => ruleResult.value !== null && !llmResult.value && !isOptimizing.value)
const isLoading = computed(() => isOptimizing.value)
const isCompleted = computed(() => llmResult.value !== null)
const estimatedTokens = computed(() => ruleResult.value?.estimated_llm_tokens || 0)
const actualTokens = computed(() => llmResult.value?.token_usage || 0)

// Button click handler
const handleClick = () => {
  if (canOptimize.value && ruleResult.value?.analysis_id) {
    optimizeWithLLM(ruleResult.value.analysis_id)
  }
}
</script>

<template>
  <div
    class="ai-optimize-button"
    :class="{
      'disabled': !canOptimize,
      'loading': isLoading,
      'completed': isCompleted
    }"
  >
    <!-- 未启用状态（灰色） -->
    <button
      v-if="!canOptimize && !isCompleted && !isLoading"
      disabled
      class="optimize-btn btn-disabled"
    >
      <div class="btn-content">
        <div class="icon-wrapper">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <div class="text-content">
          <span class="title">AI 深度优化</span>
          <span class="subtitle">等待规则检测完成</span>
        </div>
      </div>
    </button>

    <!-- 可点击状态（蓝色渐变） -->
    <button
      v-else-if="canOptimize && !isLoading"
      @click="handleClick"
      class="optimize-btn btn-enabled"
    >
      <div class="btn-content">
        <div class="icon-wrapper">
          <svg class="w-6 h-6 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <div class="text-content">
          <span class="title">✨ AI 深度优化</span>
          <span class="subtitle">~{{ estimatedTokens }} tokens</span>
        </div>
      </div>

      <!-- 闪烁提示效果 -->
      <div class="shine-effect"></div>
    </button>

    <!-- 加载中状态 -->
    <button
      v-else-if="isLoading"
      disabled
      class="optimize-btn btn-loading"
    >
      <div class="btn-content">
        <div class="icon-wrapper">
          <div class="spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring inner"></div>
          </div>
        </div>
        <div class="text-content">
          <span class="title">优化中...</span>
          <span class="subtitle">AI 正在分析</span>
        </div>
      </div>
    </button>

    <!-- 完成状态（绿色） -->
    <button
      v-else-if="isCompleted"
      disabled
      class="optimize-btn btn-completed"
    >
      <div class="btn-content">
        <div class="icon-wrapper">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <div class="text-content">
          <span class="title">✓ 优化完成</span>
          <span class="subtitle">{{ actualTokens }} tokens</span>
        </div>
      </div>

      <!-- 成功粒子效果 -->
      <div class="success-particles">
        <div class="particle particle-1"></div>
        <div class="particle particle-2"></div>
        <div class="particle particle-3"></div>
      </div>
    </button>
  </div>
</template>

<style scoped>
.ai-optimize-button {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 50;
}

.optimize-btn {
  position: relative;
  min-width: 180px;
  padding: 16px 24px;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 2;
}

.icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.text-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.title {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
}

.subtitle {
  font-size: 11px;
  font-weight: 400;
  opacity: 0.8;
}

/* 禁用状态 */
.btn-disabled {
  background: rgba(71, 85, 105, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.4);
  cursor: not-allowed;
}

.btn-disabled .icon-wrapper {
  background: rgba(255, 255, 255, 0.05);
}

/* 可点击状态 */
.btn-enabled {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  box-shadow:
    0 10px 40px rgba(102, 126, 234, 0.4),
    0 0 0 0 rgba(102, 126, 234, 0.4);
  animation: pulse-glow 2s infinite;
}

.btn-enabled:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow:
    0 15px 50px rgba(102, 126, 234, 0.5),
    0 0 0 10px rgba(102, 126, 234, 0.2);
}

.btn-enabled .icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
}

/* 闪烁效果 */
.shine-effect {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 70%
  );
  transform: translateX(-100%);
  animation: shine 3s infinite;
}

@keyframes shine {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow:
      0 10px 40px rgba(102, 126, 234, 0.4),
      0 0 0 0 rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow:
      0 10px 40px rgba(102, 126, 234, 0.4),
      0 0 0 15px rgba(102, 126, 234, 0.2);
  }
}

/* 加载状态 */
.btn-loading {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: wait;
}

.btn-loading .icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
}

.spinner {
  position: relative;
  width: 24px;
  height: 24px;
}

.spinner-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

.spinner-ring.inner {
  inset: 4px;
  animation-duration: 0.6s;
  animation-direction: reverse;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 完成状态 */
.btn-completed {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  cursor: default;
  box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
}

.btn-completed .icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
}

/* 成功粒子 */
.success-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  opacity: 0;
}

.btn-completed .particle {
  animation: particle-burst 1s ease-out forwards;
}

.particle-1 {
  top: 50%;
  left: 30%;
  animation-delay: 0s;
}

.particle-2 {
  top: 30%;
  left: 50%;
  animation-delay: 0.1s;
}

.particle-3 {
  top: 70%;
  left: 50%;
  animation-delay: 0.2s;
}

@keyframes particle-burst {
  0% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--tx), var(--ty)) scale(0);
  }
}

.particle-1 {
  --tx: -20px;
  --ty: -30px;
}

.particle-2 {
  --tx: 0;
  --ty: -40px;
}

.particle-3 {
  --tx: 0;
  --ty: 40px;
}

/* 响应式调整 */
@media (max-width: 1280px) {
  .optimize-btn {
    min-width: 160px;
    padding: 14px 20px;
  }

  .title {
    font-size: 13px;
  }

  .subtitle {
    font-size: 10px;
  }

  .icon-wrapper {
    width: 36px;
    height: 36px;
  }
}
</style>
