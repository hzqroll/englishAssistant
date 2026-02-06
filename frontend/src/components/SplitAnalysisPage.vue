<template>
  <div class="min-h-screen bg-stone-50 flex flex-col">
    <!-- Header -->
    <header class="h-16 border-b border-stone-200 bg-white flex items-center px-6 justify-between z-10 shadow-sm relative">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center text-white font-serif font-bold text-lg">E</div>
        <h1 class="text-xl font-semibold tracking-tight text-stone-900">English Transfer Assistant</h1>
        <span class="px-2 py-0.5 bg-stone-100 text-stone-600 text-xs rounded-full border border-stone-200 font-medium">Split Analysis</span>
      </div>
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2 text-sm text-stone-500">
          <i data-lucide="coins" class="w-4 h-4"></i>
          <span class="font-medium">{{ userCredits }} credits</span>
        </div>
        <div class="w-8 h-8 rounded-full bg-stone-200 border border-stone-300 overflow-hidden">
          <img :src="userAvatar" alt="User" class="w-full h-full object-cover">
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 flex overflow-hidden relative">
      <!-- Panel 1: Input (30%) -->
      <div class="w-[30%] panel bg-white flex flex-col z-10 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        <div class="p-5 border-b border-stone-100 flex justify-between items-center bg-white sticky top-0">
          <div class="flex items-center gap-2">
            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-stone-100 text-stone-600 text-xs font-bold font-mono">1</span>
            <h2 class="font-semibold text-stone-800">Original Text</h2>
          </div>
          <div class="flex gap-2">
            <button @click="clearText" class="p-1.5 text-stone-400 hover:text-stone-700 hover:bg-stone-50 rounded-md transition-colors" title="Clear">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
            <button @click="pasteText" class="p-1.5 text-stone-400 hover:text-stone-700 hover:bg-stone-50 rounded-md transition-colors" title="Paste">
              <i data-lucide="clipboard" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <div class="flex-1 p-6 relative">
          <textarea
            v-model="inputText"
            class="w-full h-full resize-none outline-none text-lg leading-relaxed text-stone-800 font-serif placeholder:text-stone-300"
            placeholder="Type or paste your English text here..."
            spellcheck="false"
            :disabled="isAnalyzing"
          ></textarea>

          <div class="absolute bottom-6 right-6 text-xs text-stone-400 font-mono">
            {{ wordCount }} words
          </div>
        </div>

        <div class="p-4 border-t border-stone-100 bg-stone-50/50">
          <button 
            @click="analyzeGrammar" 
            :disabled="!canAnalyze || isAnalyzing"
            class="w-full py-2.5 bg-stone-900 hover:bg-stone-800 disabled:bg-stone-300 text-white rounded-lg font-medium shadow-sm transition-all flex items-center justify-center gap-2 group"
          >
            <span>{{ isAnalyzing ? 'Analyzing...' : 'Analyze Grammar' }}</span>
            <i data-lucide="arrow-right" class="w-4 h-4 transition-transform group-hover:translate-x-1"></i>
          </button>
          <div class="mt-2 text-center text-xs text-stone-400 flex items-center justify-center gap-1">
            <i data-lucide="zap" class="w-3 h-3"></i>
            <span>Free & Fast (2-4s)</span>
          </div>
        </div>
      </div>

      <!-- Panel 2: Rule Engine Results (35%) -->
      <div class="w-[35%] panel bg-stone-50/30 flex flex-col z-0 relative">
        <div class="p-5 border-b border-stone-200/60 flex justify-between items-center bg-stone-50/80 backdrop-blur-sm sticky top-0 z-10">
          <div class="flex items-center gap-2">
            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold font-mono">2</span>
            <h2 class="font-semibold text-stone-800">Rule-Based Check</h2>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="ruleResult?.errors?.length" class="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full border border-red-200">
              {{ ruleResult.errors.length }} Error{{ ruleResult.errors.length !== 1 ? 's' : '' }}
            </span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <!-- Loading State -->
          <div v-if="isAnalyzing" class="flex items-center justify-center py-12">
            <div class="text-center">
              <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p class="text-sm text-stone-500">Analyzing grammar rules...</p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="ruleError" class="text-center py-12">
            <div class="text-red-500 mb-3">
              <i data-lucide="alert-circle" class="w-8 h-8 mx-auto"></i>
            </div>
            <p class="text-sm text-stone-600 mb-3">{{ ruleError }}</p>
            <button @click="analyzeGrammar" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
              Retry Analysis
            </button>
          </div>

          <!-- Results -->
          <template v-else-if="ruleResult">
            <!-- Annotated Text Display -->
            <div class="p-6 bg-white rounded-xl shadow-sm border border-stone-200 font-serif text-lg leading-relaxed text-stone-800">
              <div v-html="annotatedText" class="whitespace-pre-wrap"></div>
            </div>

            <!-- Error Cards List -->
            <div class="space-y-3">
              <h3 class="text-xs font-bold text-stone-400 uppercase tracking-wider font-mono mb-2">Detailed Findings</h3>

              <div 
                v-for="(error, index) in ruleResult.errors" 
                :key="index"
                @click="selectError(error)"
                class="error-card bg-white p-4 rounded-xl border border-stone-200 cursor-pointer relative overflow-hidden group hover:border-blue-300 transition-all"
                :class="{ 'border-blue-300 shadow-md': selectedError === error }"
              >
                <div class="absolute left-0 top-0 bottom-0 w-1 bg-red-500"></div>
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-center gap-2">
                    <span class="px-1.5 py-0.5 bg-red-50 text-red-600 text-[10px] font-bold uppercase tracking-wide rounded border border-red-100">
                      {{ error.category }}
                    </span>
                    <span class="text-xs font-mono text-stone-400">#{{ error.rule_id || 'LT-' + (index + 1) }}</span>
                  </div>
                  <i data-lucide="chevron-right" class="w-4 h-4 text-stone-300"></i>
                </div>
                <div class="flex items-baseline gap-2 mb-1">
                  <span class="text-red-600 line-through decoration-red-300 decoration-2">{{ error.original_text }}</span>
                  <i data-lucide="arrow-right" class="w-3 h-3 text-stone-400"></i>
                  <span class="text-green-600 font-medium bg-green-50 px-1 rounded">{{ error.replacements[0] }}</span>
                </div>
                <p class="text-sm text-stone-600 leading-relaxed">{{ error.message }}</p>
              </div>
            </div>
          </template>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <div class="text-stone-400 mb-3">
              <i data-lucide="file-text" class="w-12 h-12 mx-auto"></i>
            </div>
            <p class="text-sm text-stone-500">Run grammar analysis to see results</p>
          </div>
        </div>

        <!-- FLOATING AI TRIGGER BUTTON -->
        <button 
          v-if="canOptimize && !isOptimizing"
          @click="optimizeWithAI"
          class="ai-trigger glass flex items-center gap-3 pl-4 pr-5 py-3 rounded-full shadow-lg border-white/50 text-stone-800 hover:shadow-xl transition-all group"
          :class="{ 'active': isOptimizing }"
        >
          <div class="relative w-8 h-8">
            <div class="absolute inset-0 bg-blue-500 rounded-full opacity-20 animate-ping"></div>
            <div class="absolute inset-0 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-full flex items-center justify-center text-white shadow-inner">
              <i data-lucide="sparkles" class="w-4 h-4"></i>
            </div>
          </div>
          <div class="flex flex-col items-start">
            <span class="text-sm font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">AI Deep Optimize</span>
            <span class="text-[10px] text-stone-500 font-mono">~{{ estimatedTokens }} tokens</span>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-stone-400 group-hover:translate-x-1 transition-transform"></i>
        </button>
      </div>

      <!-- Panel 3: LLM Optimization (35%) -->
      <div class="w-[35%] panel bg-stone-50 bg-grid-pattern flex flex-col">
        <div class="p-5 border-b border-stone-200/60 flex justify-between items-center bg-white/80 backdrop-blur-sm sticky top-0 z-10">
          <div class="flex items-center gap-2">
            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-600 text-xs font-bold font-mono">3</span>
            <h2 class="font-semibold text-stone-800">AI Insights</h2>
          </div>
          <div class="px-2 py-1 bg-stone-100 text-stone-600 text-xs font-medium rounded flex items-center gap-1.5">
            <i data-lucide="zap" class="w-3 h-3 text-yellow-500 fill-current"></i>
            <span>Pro Mode</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-8">
          <!-- Loading State -->
          <div v-if="isOptimizing" class="flex items-center justify-center py-12">
            <div class="text-center">
              <div class="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p class="text-sm text-stone-500">AI is optimizing your text...</p>
              <p class="text-xs text-stone-400 mt-1">This may take 10-20 seconds</p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="llmError" class="text-center py-12">
            <div class="text-red-500 mb-3">
              <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto"></i>
            </div>
            <p class="text-sm text-stone-600 mb-3">{{ llmError }}</p>
            <button @click="optimizeWithAI" class="text-purple-600 hover:text-purple-700 text-sm font-medium">
              Retry Optimization
            </button>
          </div>

          <!-- Results -->
          <template v-else-if="llmResult">
            <!-- Optimized Rewrite -->
            <div class="space-y-3">
              <h3 class="text-xs font-bold text-stone-400 uppercase tracking-wider font-mono">Natural Rewrite</h3>
              <div class="p-6 bg-white rounded-xl shadow-sm border border-purple-100 relative overflow-hidden">
                <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-blue-500 to-purple-600"></div>
                <p class="font-serif text-lg leading-relaxed text-stone-800">{{ llmResult.optimized_text }}</p>
                <div class="mt-4 flex gap-2">
                  <button @click="copyOptimizedText" class="px-3 py-1.5 bg-stone-50 hover:bg-stone-100 rounded-md text-xs font-medium text-stone-600 flex items-center gap-1.5 border border-stone-200 transition-colors">
                    <i data-lucide="copy" class="w-3 h-3"></i> Copy
                  </button>
                  <button @click="rateOptimization(true)" class="px-3 py-1.5 bg-stone-50 hover:bg-stone-100 rounded-md text-xs font-medium text-stone-600 flex items-center gap-1.5 border border-stone-200 transition-colors">
                    <i data-lucide="thumbs-up" class="w-3 h-3"></i> Helpful
                  </button>
                </div>
              </div>
            </div>

            <!-- Learning Analysis -->
            <div v-if="llmResult.learning_analysis" class="space-y-4">
              <h3 class="text-xs font-bold text-stone-400 uppercase tracking-wider font-mono flex items-center gap-2">
                <span>Learning Analysis</span>
                <div class="h-px bg-stone-200 flex-1"></div>
              </h3>

              <!-- Error Patterns -->
              <div 
                v-for="(pattern, index) in llmResult.learning_analysis.error_patterns" 
                :key="index"
                class="bg-white rounded-lg p-4 border border-stone-200 shadow-sm"
              >
                <div class="flex items-center gap-2 mb-2">
                  <div class="p-1.5 bg-blue-50 text-blue-600 rounded-md">
                    <i data-lucide="trending-up" class="w-4 h-4"></i>
                  </div>
                  <span class="text-sm font-bold text-stone-800">{{ pattern.pattern_name }}</span>
                </div>
                <p class="text-sm text-stone-600 mb-3">{{ pattern.frequency }} frequency - {{ pattern.severity }} severity</p>

                <div v-if="pattern.examples?.length" class="bg-stone-50 rounded p-3 text-sm border border-stone-100">
                  <div v-for="(example, exIndex) in pattern.examples" :key="exIndex">
                    <div class="flex gap-4 mb-1">
                      <span class="text-red-500 w-4 h-4 flex items-center justify-center">✕</span>
                      <span class="text-stone-500 line-through">{{ example.original }}</span>
                    </div>
                    <div class="flex gap-4">
                      <span class="text-green-500 w-4 h-4 flex items-center justify-center">✓</span>
                      <span class="text-stone-800 font-medium">{{ example.corrected }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Learning Recommendations -->
              <div 
                v-for="(recommendation, index) in llmResult.learning_analysis.learning_recommendations" 
                :key="index"
                class="bg-white rounded-lg p-4 border border-stone-200 shadow-sm"
              >
                <div class="flex items-center gap-2 mb-2">
                  <div class="p-1.5 bg-purple-50 text-purple-600 rounded-md">
                    <i data-lucide="lightbulb" class="w-4 h-4"></i>
                  </div>
                  <span class="text-sm font-bold text-stone-800">{{ recommendation.topic }}</span>
                </div>
                <p class="text-sm text-stone-600 mb-3">{{ recommendation.description }}</p>
                <div v-if="recommendation.estimated_study_time" class="text-xs text-stone-500 font-mono">
                  Estimated study time: {{ recommendation.estimated_study_time }}
                </div>
              </div>
            </div>

            <!-- Personalized Tips -->
            <div v-if="llmResult.learning_analysis.personalized_tips?.length" class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-5 border border-blue-100 relative overflow-hidden">
              <i data-lucide="quote" class="absolute top-4 right-4 text-blue-200 w-12 h-12 opacity-50"></i>
              <h4 class="text-blue-900 font-serif font-bold mb-2 relative z-10">Pro Tip</h4>
              <p class="text-blue-800 text-sm leading-relaxed relative z-10">{{ llmResult.learning_analysis.personalized_tips[0] }}</p>
            </div>

            <!-- Token Usage -->
            <div class="bg-white rounded-lg p-4 border border-stone-200 text-xs text-stone-500">
              <div class="flex justify-between items-center">
                <span>Tokens used:</span>
                <span class="font-mono">{{ llmResult.token_usage || 0 }}</span>
              </div>
            </div>
          </template>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <div class="text-stone-400 mb-3">
              <i data-lucide="sparkles" class="w-12 h-12 mx-auto"></i>
            </div>
            <p class="text-sm text-stone-500 mb-2">AI optimization ready</p>
            <p class="text-xs text-stone-400">Click the AI button to start</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useAuthStore } from '@/stores/authStore'
import type { LTError } from '@/stores/types'

// Store
const analysisStore = useAnalysisStore()
const authStore = useAuthStore()

// State
const inputText = ref('I would like to discuss about the project plan for next week. Actually, I have already send the email to client yesterday but they didn\'t reply me yet.\n\nMaybe we can meeting together to figure out how to do.')
const selectedError = ref<LTError | null>(null)

// Computed
const wordCount = computed(() => {
  return inputText.value.trim().split(/\s+/).filter(word => word.length > 0).length
})

const canAnalyze = computed(() => {
  return inputText.value.trim().length > 0 && !analysisStore.isAnalyzing && !analysisStore.isOptimizing
})

const canOptimize = computed(() => {
  return !!analysisStore.ruleResult && !analysisStore.isOptimizing && authStore.isAuthenticated
})

const estimatedTokens = computed(() => {
  return Math.ceil(inputText.value.length / 4) // Rough estimation
})

const ruleResult = computed(() => {
  return analysisStore.ruleResult
})

const llmResult = computed(() => {
  return analysisStore.llmResult
})

const isAnalyzing = computed(() => {
  return analysisStore.isAnalyzing
})

const isOptimizing = computed(() => {
  return analysisStore.isOptimizing
})

const ruleError = computed(() => {
  return analysisStore.error
})

const llmError = computed(() => {
  return analysisStore.llmError
})

const userCredits = computed(() => {
  return 1240 // Mock value for now
})

const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=TestUser`
})

const annotatedText = computed(() => {
  if (!ruleResult.value) return ''
  
  let text = inputText.value
  const errors = ruleResult.value.errors
  
  // Sort by position in reverse order to maintain indices
  errors.sort((a, b) => b.position.start - a.position.start)
  
  errors.forEach(error => {
    const beforeText = text.slice(0, error.position.start)
    const errorText = text.slice(error.position.start, error.position.end)
    const afterText = text.slice(error.position.end)
    
    const highlightClass = 'highlight-grammar'
    
    text = `${beforeText}<span class="${highlightClass} relative group">${errorText}<span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-stone-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none font-sans">${error.category}</span></span>${afterText}`
  })
  
  return text.replace(/\n/g, '<br>')
})

// Methods
const analyzeGrammar = async () => {
  if (!canAnalyze.value) return
  
  try {
    await analysisStore.analyzeWithRules(inputText.value, 'accuracy')
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}

const optimizeWithAI = async () => {
  if (!canOptimize.value) return
  
  try {
    await analysisStore.optimizeWithLLM()
  } catch (error) {
    console.error('Optimization failed:', error)
  }
}

const selectError = (error: LTError) => {
  selectedError.value = selectedError.value === error ? null : error
}

const clearText = () => {
  inputText.value = ''
  analysisStore.resetAnalysis()
}

const pasteText = async () => {
  try {
    const text = await navigator.clipboard.readText()
    inputText.value = text
  } catch (error) {
    console.error('Failed to paste text:', error)
  }
}

const copyOptimizedText = async () => {
  if (!llmResult.value?.optimized_text) return
  
  try {
    await navigator.clipboard.writeText(llmResult.value.optimized_text)
    // Show success toast
  } catch (error) {
    console.error('Failed to copy text:', error)
  }
}

const rateOptimization = (helpful: boolean) => {
  // Implement rating logic
  console.log('Optimization rated as:', helpful ? 'helpful' : 'not helpful')
}

// Lifecycle
onMounted(() => {
  // Initialize Lucide icons
  if (typeof window !== 'undefined' && (window as any).lucide) {
    (window as any).lucide.createIcons()
  }
})
</script>

<style scoped>
/* Custom styles matching the mockup */
.panel {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  border-right: 1px solid var(--border-color);
  position: relative;
}

.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

/* Floating AI Button Animation */
@keyframes float {
  0% { transform: translateY(0px) translateX(-50%); }
  50% { transform: translateY(-6px) translateX(-50%); }
  100% { transform: translateY(0px) translateX(-50%); }
}

@keyframes pulse-glow {
  0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(37, 99, 235, 0); }
  100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
}

.ai-trigger {
  animation: float 4s ease-in-out infinite;
  position: absolute;
  right: -24px;
  top: 50%;
  z-index: 50;
  transform: translateX(-50%);
}

.ai-trigger:hover {
  animation-play-state: paused;
  transform: translateY(-2px) translateX(-50%) scale(1.05);
}

.ai-trigger.active {
  animation: pulse-glow 2s infinite;
}

/* Error Highlights */
:deep(.highlight-grammar) {
  text-decoration: underline;
  text-decoration-style: wavy;
  text-decoration-color: var(--error);
  text-decoration-thickness: 2px;
  background-color: rgba(220, 38, 38, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.highlight-grammar:hover) {
  background-color: rgba(220, 38, 38, 0.15);
}

:deep(.highlight-style) {
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-color: var(--warning);
  text-decoration-thickness: 2px;
  background-color: rgba(217, 119, 6, 0.05);
  cursor: pointer;
}

/* Card Hover Effects */
.error-card {
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}

.error-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
}

/* Pattern Background */
.bg-grid-pattern {
  background-image: radial-gradient(#E5E7EB 1px, transparent 1px);
  background-size: 24px 24px;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #D6D3D1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #A8A29E;
}

/* CSS Variables */
:root {
  --bg-color: #FAFAF9;
  --panel-bg: #FFFFFF;
  --accent-blue: #2563EB;
  --accent-soft: #DBEAFE;
  --text-primary: #1C1917;
  --text-secondary: #57534E;
  --border-color: #E7E5E4;
  --success: #059669;
  --warning: #D97706;
  --error: #DC2626;
}
</style>