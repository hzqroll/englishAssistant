<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useAuthStore } from '@/stores/authStore'
import type { LTError } from '@/stores/types'
import {
  PencilSquareIcon,
  TrashIcon,
  ClipboardIcon,
  PlayIcon,
  BoltIcon,
  ExclamationCircleIcon,
  SparklesIcon,
  ArrowPathIcon,
  DocumentDuplicateIcon,
  LightBulbIcon,
  ChartBarIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

// Store
const analysisStore = useAnalysisStore()
const authStore = useAuthStore()
const router = useRouter()

// State
const inputText = ref('I would like to discuss about the project plan for next week.\nActually, I have already send the email to client yesterday but they didn\'t reply me yet.\n\nMaybe we can meeting together to figure out how to do.')
const selectedError = ref<LTError | null>(null)

// Computed
const wordCount = computed(() => {
  return inputText.value.trim().split(/\s+/).filter(word => word.length > 0).length
})

const canAnalyze = computed(() => {
  return inputText.value.trim().length > 0 && !analysisStore.isAnalyzing && !analysisStore.isOptimizing
})

const canOptimize = computed(() => {
  return !!analysisStore.ruleResult && !analysisStore.isOptimizing
})

const estimatedTokens = computed(() => {
  if (!analysisStore.ruleResult) return Math.ceil(inputText.value.length / 4)
  return analysisStore.ruleResult.estimated_llm_tokens || Math.ceil(inputText.value.length / 4)
})

const annotatedText = computed(() => {
  if (!analysisStore.ruleResult) return inputText.value
  
  let text = inputText.value
  // Clone and sort errors by index descending to handle string splicing safely
  const errors = [...analysisStore.ruleResult.errors].sort((a, b) => b.start_index - a.start_index)
  
  let result = text
  for (const error of errors) {
    const start = error.start_index
    const end = error.end_index
    
    // Safety check
    if (start < 0 || end > result.length) continue

    const chunk = result.slice(start, end)
    const severityClass = error.severity === 'high' ? 'bg-red-100 decoration-red-500' : 'bg-yellow-100 decoration-yellow-500'
    
    // Create the span
    const span = `<span class="highlight-error ${severityClass} underline decoration-wavy decoration-2 cursor-pointer relative group" data-error-id="${error.rule_id}">
      ${chunk}
    </span>`
    
    result = result.slice(0, start) + span + result.slice(end)
  }
  
  return result.replace(/\n/g, '<br>')
})

// Actions
const analyzeGrammar = async () => {
  if (!canAnalyze.value) return
  selectedError.value = null
  await analysisStore.analyzeWithRules(inputText.value, 'accuracy')
}

const optimizeWithAI = async () => {
  if (!canOptimize.value) return
  
  if (!authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    // We can also save the current state or just let them navigate back
    if (confirm('AI Deep Optimization requires a Pro account. Would you like to log in now?')) {
      router.push({ name: 'Auth', query: { redirect: '/split' } })
    }
    return
  }

  await analysisStore.optimizeWithLLM()
}

const selectError = (error: LTError) => {
  selectedError.value = selectedError.value === error ? null : error
}

const clearText = () => {
  inputText.value = ''
  analysisStore.resetAnalysis()
  selectedError.value = null
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
  if (!analysisStore.llmResult?.optimized_text) return
  try {
    await navigator.clipboard.writeText(analysisStore.llmResult.optimized_text)
    // In a real app, show a toast here
  } catch (error) {
    console.error('Failed to copy text:', error)
  }
}

// Helpers
const getCategoryColor = (category: string | undefined) => {
  if (!category) return 'bg-gray-100 text-gray-600'
  const cat = category.toLowerCase()
  if (cat.includes('grammar')) return 'bg-red-100 text-red-700'
  if (cat.includes('style')) return 'bg-orange-100 text-orange-700'
  if (cat.includes('spelling')) return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-600'
}

onMounted(() => {
  analysisStore.resetAnalysis()
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden font-sans">
    <!-- Top Navigation Bar -->
    <header class="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 shrink-0 z-20">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-lg flex items-center justify-center shadow-sm">
          <span class="text-white font-bold text-lg">E</span>
        </div>
        <h1 class="text-gray-900 font-semibold text-sm">English Transfer Assistant</h1>
        <div class="h-4 w-px bg-gray-300 mx-1"></div>
        <span class="text-gray-500 text-xs font-medium px-2 py-0.5 bg-gray-100 rounded-full">Pro Analysis</span>
      </div>
      
      <div class="flex items-center gap-3">
        <button class="text-gray-400 hover:text-gray-600 transition-colors">
          <ChartBarIcon class="w-5 h-5" />
        </button>
        <div class="h-8 w-8 rounded-full bg-gray-200 border border-gray-300 overflow-hidden">
          <div class="w-full h-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-medium text-xs">US</div>
        </div>
      </div>
    </header>

    <!-- Main Content Grid -->
    <main class="flex-1 flex overflow-hidden">
      
      <!-- COLUMN 1: Input / Editor (30%) -->
      <div class="w-[30%] flex flex-col bg-white border-r border-gray-200 z-10">
        <div class="h-12 border-b border-gray-100 flex items-center justify-between px-4 bg-white">
          <div class="flex items-center gap-2 text-gray-700 font-medium text-sm">
            <PencilSquareIcon class="w-4 h-4 text-gray-400" />
            <span>Editor</span>
          </div>
          <div class="flex items-center gap-1">
            <button @click="clearText" class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors" title="Clear">
              <TrashIcon class="w-4 h-4" />
            </button>
            <button @click="pasteText" class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-50 rounded transition-colors" title="Paste">
              <ClipboardIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="flex-1 relative group">
          <textarea
            v-model="inputText"
            class="w-full h-full p-6 resize-none outline-none text-[15px] leading-7 text-gray-800 font-serif placeholder:text-gray-300 bg-transparent"
            placeholder="Type or paste your text here..."
            spellcheck="false"
            :disabled="analysisStore.isAnalyzing"
          ></textarea>
          
          <div class="absolute bottom-4 right-4 text-xs text-gray-300 font-mono pointer-events-none group-hover:text-gray-400 transition-colors">
            {{ wordCount }} words
          </div>
        </div>

        <div class="p-4 border-t border-gray-100 bg-gray-50">
          <button 
            @click="analyzeGrammar" 
            :disabled="!canAnalyze || analysisStore.isAnalyzing"
            class="w-full py-2.5 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium shadow-sm transition-all flex items-center justify-center gap-2 group"
          >
            <ArrowPathIcon v-if="analysisStore.isAnalyzing" class="w-4 h-4 animate-spin" />
            <PlayIcon v-else class="w-4 h-4" />
            <span>{{ analysisStore.isAnalyzing ? 'Analyzing...' : 'Check Grammar' }}</span>
          </button>
        </div>
      </div>

      <!-- COLUMN 2: Rule Findings (35%) -->
      <div class="w-[35%] flex flex-col bg-gray-50/50 border-r border-gray-200 relative">
        <div class="h-12 border-b border-gray-200/50 flex items-center justify-between px-4 bg-white/50 backdrop-blur-sm sticky top-0 z-10">
          <div class="flex items-center gap-2 text-gray-700 font-medium text-sm">
            <BoltIcon class="w-4 h-4 text-blue-500" />
            <span>Rule Analysis</span>
          </div>
          <span v-if="analysisStore.ruleResult" class="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-bold rounded-full">
            {{ analysisStore.ruleResult.errors.length }} Issues
          </span>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <!-- Empty State -->
          <div v-if="!analysisStore.ruleResult && !analysisStore.isAnalyzing" class="h-full flex flex-col items-center justify-center text-gray-400 pb-20">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <BoltIcon class="w-8 h-8 text-gray-300" />
            </div>
            <p class="text-sm">Run analysis to see grammar & style issues</p>
          </div>

          <!-- Loading -->
          <div v-if="analysisStore.isAnalyzing" class="h-full flex flex-col items-center justify-center text-gray-400 pb-20">
            <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-sm">Scanning text...</p>
          </div>

          <!-- Results -->
          <template v-if="analysisStore.ruleResult && !analysisStore.isAnalyzing">
            <!-- Annotated Preview -->
            <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-sm font-serif text-[15px] leading-7 text-gray-800">
              <div v-html="annotatedText"></div>
            </div>

            <!-- Error List -->
            <div class="space-y-3">
              <div 
                v-for="(error, index) in analysisStore.ruleResult.errors" 
                :key="index"
                @click="selectError(error)"
                class="bg-white p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md cursor-pointer transition-all relative overflow-hidden group"
                :class="{ 'ring-2 ring-blue-500 border-transparent': selectedError === error }"
              >
                <div class="flex items-start justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <span :class="['px-1.5 py-0.5 text-[10px] font-bold uppercase rounded', getCategoryColor(error.error_type)]">
                      {{ error.error_type }}
                    </span>
                    <span class="text-xs text-gray-400 font-mono" v-if="error.severity === 'high'">Critical</span>
                  </div>
                </div>
                
                <div class="flex items-baseline gap-2 mb-1 text-sm">
                  <span class="text-red-500 line-through decoration-red-200 decoration-1">{{ error.original_span }}</span>
                  <span class="text-gray-300">→</span>
                  <span class="text-green-600 font-medium">{{ error.corrected_span }}</span>
                </div>
                
                <p class="text-xs text-gray-600 mt-2 leading-relaxed">{{ error.explanation }}</p>
              </div>
            </div>
          </template>
        </div>

        <!-- AI Trigger Button (Floating) -->
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-20" v-if="canOptimize">
          <button 
            @click="optimizeWithAI"
            class="flex items-center gap-2 pl-4 pr-5 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white rounded-full shadow-lg shadow-indigo-200 hover:shadow-xl hover:-translate-y-0.5 transition-all group"
          >
            <SparklesIcon class="w-5 h-5 animate-pulse" />
            <div class="flex flex-col items-start leading-none">
              <span class="font-bold text-sm">
                {{ authStore.isAuthenticated ? 'AI Deep Optimize' : 'Login to Optimize' }}
              </span>
              <span class="text-[10px] opacity-80 mt-0.5">~{{ estimatedTokens }} tokens</span>
            </div>
            <ChevronRightIcon class="w-4 h-4 opacity-50 group-hover:translate-x-1 transition-transform ml-1" />
          </button>
        </div>
      </div>

      <!-- COLUMN 3: AI Results (35%) -->
      <div class="w-[35%] flex flex-col bg-white z-10">
        <div class="h-12 border-b border-gray-200 flex items-center justify-between px-4 bg-white sticky top-0">
          <div class="flex items-center gap-2 text-gray-700 font-medium text-sm">
            <SparklesIcon class="w-4 h-4 text-violet-500" />
            <span>AI Insights</span>
          </div>
          <div v-if="analysisStore.llmResult" class="flex items-center gap-2">
             <span class="text-[10px] text-gray-400 font-mono">Used {{ analysisStore.llmResult.token_usage }} tokens</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-6">
          <!-- Empty State -->
          <div v-if="!analysisStore.llmResult && !analysisStore.isOptimizing" class="h-full flex flex-col items-center justify-center text-gray-400 pb-20">
            <div class="w-16 h-16 bg-violet-50 rounded-full flex items-center justify-center mb-4">
              <SparklesIcon class="w-8 h-8 text-violet-300" />
            </div>
            <p class="text-sm text-center px-8">Deep optimization with LLM to improve naturalness and style</p>
          </div>

          <!-- Loading -->
          <div v-if="analysisStore.isOptimizing" class="h-full flex flex-col items-center justify-center text-gray-400 pb-20">
             <div class="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin mb-4"></div>
             <p class="text-sm">Rewriting text...</p>
          </div>

          <!-- Results -->
          <template v-if="analysisStore.llmResult && !analysisStore.isOptimizing">
            <!-- Debug Info -->
            <div v-if="false" class="bg-gray-100 p-2 text-xs mb-4 overflow-auto max-h-40">
              <pre>{{ JSON.stringify(analysisStore.llmResult, null, 2) }}</pre>
            </div>

            <!-- Rewritten Text -->
            <div class="space-y-2">
              <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Natural Rewrite</h3>
              <div class="bg-violet-50/50 rounded-xl border border-violet-100 p-5 relative group">
                <!-- Fallback for empty optimized_text -->
                <p class="font-serif text-[15px] leading-7 text-gray-800">
                  {{ analysisStore.llmResult.optimized_text || analysisStore.llmResult.corrected_text || 'No optimized text available.' }}
                </p>
                
                <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <button @click="copyOptimizedText" class="p-1.5 bg-white border border-violet-200 text-violet-600 rounded hover:bg-violet-50 transition-colors" title="Copy">
                    <DocumentDuplicateIcon class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Learning Analysis -->
            <div v-if="analysisStore.llmResult.learning_analysis" class="space-y-4">
              <div class="flex items-center gap-4">
                <div class="h-px bg-gray-200 flex-1"></div>
                <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Analysis</span>
                <div class="h-px bg-gray-200 flex-1"></div>
              </div>

              <!-- Error Patterns -->
              <div 
                v-for="(pattern, idx) in analysisStore.llmResult.learning_analysis.error_patterns" 
                :key="idx"
                class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm"
              >
                <div class="flex items-center gap-2 mb-2">
                  <ChartBarIcon class="w-4 h-4 text-blue-500" />
                  <span class="font-medium text-sm text-gray-900">{{ pattern.pattern_name }}</span>
                </div>
                <p class="text-xs text-gray-500 mb-3">Frequency: {{ pattern.frequency }}</p>
                
                <div class="bg-gray-50 rounded border border-gray-100 p-2 space-y-2">
                  <div v-for="(ex, i) in pattern.examples" :key="i" class="text-xs grid grid-cols-[1fr,auto,1fr] gap-2 items-center">
                    <span class="text-red-500 line-through text-right truncate">{{ ex.original }}</span>
                    <span class="text-gray-300">→</span>
                    <span class="text-green-600 font-medium truncate">{{ ex.corrected }}</span>
                  </div>
                </div>
              </div>

              <!-- Recommendations -->
              <div 
                v-for="(rec, idx) in analysisStore.llmResult.learning_analysis.learning_recommendations" 
                :key="idx"
                class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg border border-orange-100 p-4"
              >
                <div class="flex items-center gap-2 mb-2">
                  <LightBulbIcon class="w-4 h-4 text-orange-500" />
                  <span class="font-medium text-sm text-gray-900">{{ rec.topic }}</span>
                </div>
                <p class="text-xs text-gray-600 leading-relaxed">{{ rec.description }}</p>
                <div class="mt-2 text-[10px] text-orange-600/70 font-mono">Est. time: {{ rec.estimated_study_time }}</div>
              </div>
            </div>
          </template>

          <!-- Error State -->
          <div v-if="analysisStore.llmError" class="p-4 bg-red-50 border border-red-100 rounded-lg text-red-600 text-sm flex items-start gap-2">
            <ExclamationCircleIcon class="w-5 h-5 shrink-0" />
            <p>{{ analysisStore.llmError }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Additional specific styles if needed, mostly using Tailwind */
.highlight-error {
  padding-bottom: 2px;
}
</style>
