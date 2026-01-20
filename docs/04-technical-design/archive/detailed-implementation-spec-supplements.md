# English Transfer Assistant - 技术方案补充文档

**文档版本**: v2.1
**补充内容**: Token 监控、前端 Store 设计、测试用例示例
**最后更新**: 2026-01-20

本文档是对 `detailed-implementation-spec-v2.md` 的重要补充，涵盖成本监控、前端状态管理和测试基准。

---

## 目录

1. [Token 消耗监控](#1-token-消耗监控-token-usage-monitoring)
2. [前端 Store 状态设计](#2-前端-store-状态设计-frontend-store-schema)
3. [Merger 测试用例示例](#3-merger-测试用例示例-merger-test-cases)

---

## 1. Token 消耗监控 (Token Usage Monitoring)

### 1.1 数据库模型更新

#### 修改 `models/analysis.py`

```python
from sqlalchemy import Column, String, Text, Integer, String, ForeignKey, JSONB, Index, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid
from .base import Base, TimestampMixin, SoftDeleteMixin

class Analysis(Base, TimestampMixin, SoftDeleteMixin):
    """文本分析记录"""
    __tablename__ = "analyses"

    # 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 用户关联
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # 文本内容
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)

    # 分析参数
    mode = Column(String(50), nullable=False)  # accuracy, natural
    text_type = Column(String(50), default="unknown")

    # 统计信息
    statistics = Column(JSONB, default=dict, nullable=False)

    # 性能指标
    processing_time_ms = Column(Integer, default=0)
    is_cached = Column(Boolean, default=False)

    # ✅ 新增：Token 使用统计
    token_usage = Column(JSONB, nullable=False, default=dict)
    # 格式: {
    #   "input_tokens": 150,
    #   "output_tokens": 300,
    #   "total_tokens": 450,
    #   "estimated_cost": 0.0009,  # 单位：元（根据智谱 AI 定价）
    #   "model": "glm-4-flash",
    #   "cache_hit": false
    # }

    # 关系
    user = relationship("User", back_populates="analyses")
    errors = relationship("ErrorDetail", back_populates="analysis", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('ix_analysis_user_date', 'user_id', 'created_at'),
        Index('ix_analysis_user_deleted', 'user_id', 'is_deleted', 'created_at'),
        Index('ix_analysis_mode_type', 'mode', 'text_type'),
        Index('ix_analysis_cache', 'is_cached', 'created_at'),
    )

    @property
    def token_count(self) -> dict:
        """便捷方法：获取 token 统计"""
        return self.token_usage or {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }
```

#### 修改 `models/user.py` - 添加配额使用统计

```python
class APICredit(Base):
    """API 配额管理"""
    __tablename__ = "api_credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    quota_type = Column(String(50), nullable=False)  # daily, monthly
    quota = Column(Integer, nullable=False)
    used = Column(Integer, default=0, nullable=False)

    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # ✅ 新增：Token 使用追踪
    total_tokens_used = Column(Integer, default=0)  # 本周期累计 tokens
    estimated_cost = Column(Float, default=0.0)  # 本周期预估成本（元）

    metadata = Column(JSONB, default=dict)

    @property
    def remaining(self) -> int:
        return max(0, self.quota - self.used)

    @property
    def token_usage_efficiency(self) -> float:
        """Token 使用效率（请求数 / Token 数）"""
        if self.total_tokens_used == 0:
            return 0.0
        return self.used / self.total_tokens_used
```

### 1.2 Token 计数服务

```python
# services/token_counter.py
from typing import Dict
import tiktoken  # OpenAI 的 tokenizer，兼容智谱 AI

class TokenCounter:
    """Token 计数器"""

    # 智谱 AI GLM-4-Flash 定价（2026年1月）
    # 参考: https://open.bigmodel.cn/pricing
    PRICING = {
        "glm-4-flash": {
            "input": 0.0001,   # 0.1 元 / 1M tokens
            "output": 0.0001   # 0.1 元 / 1M tokens
        },
        "glm-4": {
            "input": 0.001,    # 1 元 / 1M tokens
            "output": 0.002    # 2 元 / 1M tokens
        }
    }

    def __init__(self, model: str = "glm-4-flash"):
        self.model = model
        # 使用 cl100k_base 编码器（与 GPT-4 兼容，接近 GLM-4）
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量"""
        return len(self.encoding.encode(text))

    def calculate_usage(
        self,
        input_text: str,
        output_text: str,
        model: str = None
    ) -> Dict:
        """计算 Token 使用和成本"""

        model = model or self.model
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        total_tokens = input_tokens + output_tokens

        # 计算成本
        pricing = self.PRICING.get(model, self.PRICING["glm-4-flash"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": round(total_cost, 6),  # 保留 6 位小数
            "model": model,
            "cost_breakdown": {
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6)
            }
        }
```

### 1.3 Pipeline 集成 Token 追踪

```python
# pipeline/pipeline.py (更新部分)

from services.token_counter import TokenCounter

class AnalysisPipeline:
    """文本分析流水线"""

    def __init__(
        self,
        zhipu_api_key: str,
        cache_service: CacheService
    ):
        self.preprocessor = Preprocessor()
        self.rule_engine = RuleEngine()
        self.llm_engine = LLMEngine(zhipu_api_key)
        self.merger = Merger()
        self.cache = cache_service
        self.token_counter = TokenCounter()  # ✅ 新增

    async def process(
        self,
        text: str,
        mode: str,
        user_id: str = None
    ) -> dict:
        """处理文本分析"""

        start_time = time.time()

        # ✅ 计算输入 tokens
        input_tokens = self.token_counter.count_tokens(text)

        try:
            # 1. 预处理
            preprocessed = await self.preprocessor.process(text)

            # 2. 规则检查
            rule_errors = await self.rule_engine.check(preprocessed.cleaned)

            # 3. LLM 优化（追踪实际使用）
            llm_response = None
            llm_result = None
            llm_input_tokens = 0
            llm_output_tokens = 0

            try:
                # 调用 LLM（需要返回 token 使用信息）
                llm_result, llm_usage = await self.llm_engine.optimize_with_usage(
                    preprocessed.cleaned,
                    mode,
                    preprocessed.has_chinese
                )
                llm_input_tokens = llm_usage.get("input_tokens", 0)
                llm_output_tokens = llm_usage.get("output_tokens", 0)

            except LLMError as e:
                logging.warning(f"LLM failed, using rule engine only: {e}")
                llm_result = self._create_fallback_llm_result(
                    preprocessed.cleaned, rule_errors
                )

            # 4. 结果合并
            result = await self.merger.merge(
                preprocessed.cleaned,
                rule_errors,
                llm_result,
                mode
            )

            # 5. 计算 token 使用
            corrected_text = result['corrected_text']
            output_tokens = self.token_counter.count_tokens(corrected_text)

            token_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "estimated_cost": self.token_counter.calculate_usage(
                    text, corrected_text
                )["estimated_cost"],
                "model": "glm-4-flash",
                "cache_hit": False,  # 后面会更新
                "llm_tokens": {
                    "input": llm_input_tokens,
                    "output": llm_output_tokens,
                    "total": llm_input_tokens + llm_output_tokens
                }
            }

            # 6. 添加元数据
            result['processing_time_ms'] = int(
                (time.time() - start_time) * 1000
            )
            result['original_text'] = text
            result['token_usage'] = token_usage

            # 7. 生成学习建议
            result['learning_tips'] = self._generate_learning_tips(
                result['errors'],
                result['statistics']
            )

            # 8. 缓存结果
            await self.cache.cache_analysis(text, mode, result)

            return result

        except Exception as e:
            logging.error(f"Pipeline processing failed: {e}")
            raise
```

### 1.4 LLM Engine 返回 Token 使用

```python
# pipeline/llm_engine.py (更新部分)

class LLMEngine:
    """LLM 引擎"""

    async def optimize_with_usage(
        self,
        text: str,
        mode: str,
        has_chinese: bool = False
    ) -> tuple[LLMResult, dict]:
        """使用 LLM 优化文本，并返回 token 使用"""

        prompt = self._build_prompt(text, mode, has_chinese)

        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert English writing assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # ✅ 提取 token 使用信息
            usage = response.usage  # 智谱 AI 返回的 usage 对象
            token_info = {
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }

            # 解析响应
            content = response.choices[0].message.content
            result_data = json.loads(content)

            self._validate_result(result_data)

            llm_result = LLMResult(
                corrected_text=result_data['corrected_text'],
                text_type=result_data.get('text_type', 'unknown'),
                tone=result_data.get('tone', 'neutral'),
                changes=result_data.get('changes', [])
            )

            return llm_result, token_info

        except Exception as e:
            raise LLMError(f"LLM processing failed: {str(e)}")
```

### 1.5 API 响应包含 Token 信息

```python
# api/analyze.py (更新部分)

@router.post("/analyze")
async def analyze_text(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """分析文本"""

    # ... 处理逻辑 ...

    result = await pipeline.process(request.text, request.mode, current_user.id)

    # ✅ 返回响应包含 token 使用
    return {
        "success": True,
        "data": {
            "id": result.get("id"),
            "original_text": result["original_text"],
            "corrected_text": result["corrected_text"],
            "text_type": result["text_type"],
            "statistics": result["statistics"],
            "errors": result["errors"],
            "learning_tips": result["learning_tips"],
            "token_usage": {  # ✅ 新增
                "input_tokens": result["token_usage"]["input_tokens"],
                "output_tokens": result["token_usage"]["output_tokens"],
                "total_tokens": result["token_usage"]["total_tokens"],
                "estimated_cost": result["token_usage"]["estimated_cost"],
                "model": result["token_usage"]["model"],
                "llm_tokens": result["token_usage"]["llm_tokens"]
            },
            "processing_time_ms": result["processing_time_ms"],
            "is_cached": result["is_cached"],
            "created_at": datetime.utcnow().isoformat()
        }
    }
```

### 1.6 用户 Token 统计 API

#### GET /statistics/tokens - Token 使用统计

```http
GET /api/v1/statistics/tokens?period=30d
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "period": "30d",
    "summary": {
      "total_requests": 150,
      "total_tokens": 45000,
      "average_tokens_per_request": 300,
      "total_cost": 0.045,
      "average_cost_per_request": 0.0003
    },
    "by_mode": {
      "accuracy": {
        "requests": 100,
        "tokens": 25000,
        "cost": 0.025
      },
      "natural": {
        "requests": 50,
        "tokens": 20000,
        "cost": 0.02
      }
    },
    "daily_usage": [
      {
        "date": "2026-01-14",
        "requests": 10,
        "tokens": 3000,
        "cost": 0.003
      },
      {
        "date": "2026-01-15",
        "requests": 15,
        "tokens": 4500,
        "cost": 0.0045
      }
    ],
    "cost_forecast": {
      "projected_monthly_cost": 0.09,
      "based_on_last_7_days": true
    }
  }
}
```

---

## 2. 前端 Store 状态设计 (Frontend Store Schema)

### 2.1 整体状态架构

```
stores/
├── index.ts                    # 导出所有 stores
├── authStore.ts                # 认证状态
├── analysisStore.ts            # 分析状态（核心）
├── historyStore.ts             # 历史记录状态
├── statisticsStore.ts          # 统计数据状态
├── uiStore.ts                  # UI 状态
└── types.ts                    # TypeScript 类型定义
```

### 2.2 类型定义

```typescript
// stores/types.ts

/** 认证状态 */
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  tokenExpiresAt: Date | null;
  isLoading: boolean;
  error: string | null;
}

/** 用户信息 */
export interface User {
  id: string;
  email: string;
  tier: 'anonymous' | 'free' | 'pro' | 'enterprise';
  is_verified: boolean;
  created_at: string;
  settings: UserSettings;
  credits: UserCredits;
}

/** 用户设置 */
export interface UserSettings {
  default_mode: 'accuracy' | 'natural';
  theme: 'light' | 'dark' | 'auto';
  auto_save: boolean;
  preferences: Record<string, any>;
}

/** 用户配额 */
export interface UserCredits {
  daily: {
    quota: number;
    used: number;
    remaining: number;
    resets_at: string;
  };
  hourly?: {
    quota: number;
    used: number;
    remaining: number;
    resets_in: number;
  };
}

/** 分析状态 */
export interface AnalysisState {
  // 当前输入
  inputText: string;
  correctionMode: 'accuracy' | 'natural';

  // 处理状态
  isAnalyzing: boolean;
  isCached: boolean;
  processingProgress: number;  // 0-100 (如果支持进度)

  // 当前结果
  currentResult: AnalysisResult | null;

  // 错误处理
  error: AnalysisError | null;

  // 视图状态
  viewMode: 'sidebyside' | 'original' | 'corrected';
  selectedErrorId: string | null;
  expandedErrorIds: Set<string>;
  filterType: string | null;  // 过滤错误类型
}

/** 分析结果 */
export interface AnalysisResult {
  id: string;
  original_text: string;
  corrected_text: string;
  text_type: string;
  mode: string;
  statistics: {
    total: number;
    by_type: Record<string, number>;
  };
  errors: ErrorDetail[];
  learning_tips: string[];
  token_usage: TokenUsage;
  processing_time_ms: number;
  is_cached: boolean;
  created_at: string;
}

/** 错误详情 */
export interface ErrorDetail {
  id: string;
  type: string;
  subtype: string;
  original: string;
  correction: string;
  position: {
    start: number;
    end: number;
  };
  explanation: string;
  severity: 'low' | 'medium' | 'high';
}

/** Token 使用 */
export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  model: string;
  llm_tokens: {
    input: number;
    output: number;
    total: number;
  };
}

/** 分析错误 */
export interface AnalysisError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

/** 历史记录状态 */
export interface HistoryState {
  records: AnalysisResult[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  isLoading: boolean;
  error: string | null;
  filter: {
    mode?: string;
    text_type?: string;
  };
}

/** 统计状态 */
export interface StatisticsState {
  overview: StatisticsOverview | null;
  tokenStats: TokenStatistics | null;
  isLoading: boolean;
  error: string | null;
  selectedPeriod: '1d' | '7d' | '30d' | 'all';
}

/** 统计概览 */
export interface StatisticsOverview {
  period: string;
  total_analyses: number;
  total_errors: number;
  error_distribution: Record<string, number>;
  top_errors: Array<{
    type: string;
    subtype: string;
    count: number;
    percentage: number;
  }>;
  improvement_trend: {
    this_week: { total_analyses: number; total_errors: number };
    last_week: { total_analyses: number; total_errors: number };
    improvement_rate: number;
  };
}

/** Token 统计 */
export interface TokenStatistics {
  period: string;
  summary: {
    total_requests: number;
    total_tokens: number;
    average_tokens_per_request: number;
    total_cost: number;
    average_cost_per_request: number;
  };
  by_mode: Record<string, {
    requests: number;
    tokens: number;
    cost: number;
  }>;
  daily_usage: Array<{
    date: string;
    requests: number;
    tokens: number;
    cost: number;
  }>;
  cost_forecast: {
    projected_monthly_cost: number;
    based_on_last_7_days: boolean;
  };
}

/** UI 状态 */
export interface UIState {
  // 布局模式
  layoutMode: 'three' | 'input-compare' | 'input-analysis' | 'compare-full';

  // 面板折叠状态
  collapsedPanels: {
    input: boolean;
    compare: boolean;
    analysis: boolean;
  };

  // 主题
  theme: 'light' | 'dark' | 'auto';

  // 全局提示
  toasts: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }>;

  // 加载状态
  globalLoading: boolean;
}
```

### 2.3 Auth Store 实现

```typescript
// stores/authStore.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '@/api/auth';
import type { AuthState, User } from './types';

export const useAuthStore = defineStore('auth', () => {
  // State
  const isAuthenticated = ref(false);
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'));
  const tokenExpiresAt = ref<Date | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isAnonymous = computed(() => user.value?.tier === 'anonymous');
  const isLoggedIn = computed(() => isAuthenticated.value && !isAnonymous.value);
  const hasQuota = computed(() => {
    if (!user.value) return false;
    return (user.value.credits.daily?.remaining ?? 0) > 0;
  });

  // Actions
  async function login(email: string, password: string) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await authApi.login({ email, password });

      token.value = response.access_token;
      refreshToken.value = response.refresh_token;
      user.value = response.user;
      isAuthenticated.value = true;
      tokenExpiresAt.value = new Date(Date.now() + response.expires_in * 1000);

      // 保存到 localStorage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);

      return response;
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(email: string, password: string) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await authApi.register({ email, password });

      token.value = response.access_token;
      refreshToken.value = response.refresh_token;
      user.value = response.user;
      isAuthenticated.value = true;

      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);

      return response;
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Registration failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return;

    isLoading.value = true;
    try {
      const response = await authApi.getCurrentUser();
      user.value = response.user;
      isAuthenticated.value = true;
    } catch (err) {
      // Token 可能过期，尝试刷新
      await refreshAccessToken();
    } finally {
      isLoading.value = false;
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      logout();
      return;
    }

    try {
      const response = await authApi.refresh({ refresh_token: refreshToken.value });
      token.value = response.access_token;
      tokenExpiresAt.value = new Date(Date.now() + response.expires_in * 1000);

      localStorage.setItem('access_token', response.access_token);
    } catch (err) {
      // Refresh token 也过期了，退出登录
      logout();
    }
  }

  function logout() {
    isAuthenticated.value = false;
    user.value = null;
    token.value = null;
    refreshToken.value = null;
    tokenExpiresAt.value = null;

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  return {
    // State
    isAuthenticated,
    user,
    token,
    refreshToken,
    tokenExpiresAt,
    isLoading,
    error,

    // Computed
    isAnonymous,
    isLoggedIn,
    hasQuota,

    // Actions
    login,
    register,
    fetchCurrentUser,
    refreshAccessToken,
    logout
  };
});
```

### 2.4 Analysis Store 实现（核心）

```typescript
// stores/analysisStore.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { analysisApi } from '@/api/analysis';
import type { AnalysisState, AnalysisResult, ErrorDetail } from './types';

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const inputText = ref('');
  const correctionMode = ref<'accuracy' | 'natural'>('accuracy');

  const isAnalyzing = ref(false);
  const isCached = ref(false);
  const processingProgress = ref(0);  // 如果支持进度回调

  const currentResult = ref<AnalysisResult | null>(null);

  const error = ref<AnalysisError | null>(null);

  const viewMode = ref<'sidebyside' | 'original' | 'corrected'>('sidebyside');
  const selectedErrorId = ref<string | null>(null);
  const expandedErrorIds = ref<Set<string>>(new Set());
  const filterType = ref<string | null>(null);

  // Computed
  const hasResult = computed(() => currentResult.value !== null);
  const errorCount = computed(() => currentResult.value?.statistics.total || 0);
  const errorTypes = computed(() => {
    if (!currentResult.value) return [];
    return Object.entries(currentResult.value.statistics.by_type)
      .map(([type, count]) => ({ type, count }));
  });

  const filteredErrors = computed(() => {
    if (!currentResult.value) return [];
    const errors = currentResult.value.errors;

    if (!filterType.value) return errors;

    return errors.filter(err => err.type === filterType.value);
  });

  const selectedError = computed(() => {
    if (!currentResult.value || !selectedErrorId.value) return null;
    return currentResult.value.errors.find(err => err.id === selectedErrorId.value);
  });

  // Actions
  async function analyzeText(text?: string, mode?: 'accuracy' | 'natural') {
    const textToAnalyze = text || inputText.value;
    const modeToUse = mode || correctionMode.value;

    if (!textToAnalyze.trim()) {
      error.value = {
        code: 'INVALID_INPUT',
        message: 'Text cannot be empty'
      };
      return;
    }

    isAnalyzing.value = true;
    error.value = null;
    processingProgress.value = 0;

    try {
      const response = await analysisApi.analyze({
        text: textToAnalyze,
        mode: modeToUse,
        options: {
          detect_chinese: true,
          preserve_proper_nouns: true
        }
      });

      currentResult.value = response;
      isCached.value = response.is_cached;
      inputText.value = textToAnalyze;
      correctionMode.value = modeToUse;

      // 自动展开第一个错误
      if (response.errors.length > 0) {
        expandedErrorIds.value.clear();
        expandedErrorIds.value.add(response.errors[0].id);
      }

      return response;
    } catch (err: any) {
      error.value = {
        code: err.response?.data?.error?.code || 'ANALYSIS_FAILED',
        message: err.response?.data?.error?.message || 'Analysis failed',
        details: err.response?.data?.error?.details
      };
      throw err;
    } finally {
      isAnalyzing.value = false;
      processingProgress.value = 0;
    }
  }

  function setViewMode(mode: 'sidebyside' | 'original' | 'corrected') {
    viewMode.value = mode;
  }

  function selectError(errorId: string | null) {
    selectedErrorId.value = errorId;
  }

  function toggleErrorCard(errorId: string) {
    if (expandedErrorIds.value.has(errorId)) {
      expandedErrorIds.value.delete(errorId);
    } else {
      expandedErrorIds.value.add(errorId);
    }
  }

  function setFilterType(type: string | null) {
    filterType.value = type;
  }

  function clearResult() {
    currentResult.value = null;
    inputText.value = '';
    error.value = null;
    selectedErrorId.value = null;
    expandedErrorIds.value.clear();
    filterType.value = null;
  }

  function clearError() {
    error.value = null;
  }

  return {
    // State
    inputText,
    correctionMode,
    isAnalyzing,
    isCached,
    processingProgress,
    currentResult,
    error,
    viewMode,
    selectedErrorId,
    expandedErrorIds,
    filterType,

    // Computed
    hasResult,
    errorCount,
    errorTypes,
    filteredErrors,
    selectedError,

    // Actions
    analyzeText,
    setViewMode,
    selectError,
    toggleErrorCard,
    setFilterType,
    clearResult,
    clearError
  };
});
```

### 2.5 UI Store 实现

```typescript
// stores/uiStore.ts

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { UIState } from './types';

export const useUIStore = defineStore('ui', () => {
  // State
  const layoutMode = ref<UIState['layoutMode']>('three');
  const collapsedPanels = ref<UIState['collapsedPanels']>({
    input: false,
    compare: false,
    analysis: false
  });
  const theme = ref<UIState['theme']>('light');
  const toasts = ref<UIState['toasts']>([]);
  const globalLoading = ref(false);

  // Actions
  function setLayoutMode(mode: UIState['layoutMode']) {
    layoutMode.value = mode;

    // 自动调整面板可见性
    switch (mode) {
      case 'input-compare':
        collapsedPanels.value.analysis = true;
        collapsedPanels.value.input = false;
        collapsedPanels.value.compare = false;
        break;
      case 'input-analysis':
        collapsedPanels.value.compare = true;
        collapsedPanels.value.input = false;
        collapsedPanels.value.analysis = false;
        break;
      case 'compare-full':
        collapsedPanels.value.input = true;
        collapsedPanels.value.analysis = true;
        collapsedPanels.value.compare = false;
        break;
      default:  // 'three'
        collapsedPanels.value.input = false;
        collapsedPanels.value.compare = false;
        collapsedPanels.value.analysis = false;
    }
  }

  function togglePanel(panel: 'input' | 'compare' | 'analysis') {
    collapsedPanels.value[panel] = !collapsedPanels.value[panel];
  }

  function setTheme(theme: UIState['theme']) {
    theme.value = theme;
    // 应用到 document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  function showToast(
    type: UIState['toasts'][0]['type'],
    message: string,
    duration = 3000
  ) {
    const id = Date.now().toString();
    toasts.value.push({ id, type, message, duration });

    setTimeout(() => {
      removeToast(id);
    }, duration);
  }

  function removeToast(id: string) {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  }

  function setGlobalLoading(loading: boolean) {
    globalLoading.value = loading;
  }

  return {
    // State
    layoutMode,
    collapsedPanels,
    theme,
    toasts,
    globalLoading,

    // Actions
    setLayoutMode,
    togglePanel,
    setTheme,
    showToast,
    removeToast,
    setGlobalLoading
  };
});
```

### 2.6 Store 使用示例

```vue
<!-- InputPanel.vue -->
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAnalysisStore } from '@/stores/analysisStore';
import { useUIStore } from '@/stores/uiStore';

const analysisStore = useAnalysisStore();
const uiStore = useUIStore();

const {
  inputText,
  correctionMode,
  isAnalyzing,
  error
} = storeToRefs(analysisStore);

const { collapsedPanels } = storeToRefs(uiStore);

async function handleAnalyze() {
  try {
    await analysisStore.analyzeText();
    uiStore.showToast('success', 'Analysis completed!');
  } catch (err) {
    uiStore.showToast('error', error.value?.message || 'Analysis failed');
  }
}
</script>

<template>
  <div v-if="!collapsedPanels.input" class="input-panel">
    <textarea
      v-model="inputText"
      placeholder="Enter your English text here..."
      :disabled="isAnalyzing"
    />

    <div class="mode-switch">
      <button
        :class="{ active: correctionMode === 'accuracy' }"
        @click="correctionMode = 'accuracy'"
      >
        Accuracy First
      </button>
      <button
        :class="{ active: correctionMode === 'natural' }"
        @click="correctionMode = 'natural'"
      >
        Naturalness First
      </button>
    </div>

    <button
      @click="handleAnalyze"
      :disabled="isAnalyzing || !inputText.trim()"
    >
      <span v-if="isAnalyzing">Analyzing...</span>
      <span v-else>Analyze Text</span>
    </button>
  </div>
</template>
```

---

## 3. Merger 测试用例示例 (Merger Test Cases)

### 3.1 测试用例 1: Accuracy 模式 - 简单时态错误

**输入**:
```python
original_text = "I go to school yesterday."
mode = "accuracy"
```

**规则引擎输出** (LanguageTool):
```python
rule_errors = [
    GrammarError(
        rule_id="VERB_TENSE",
        message="This sentence requires the past tense.",
        category="tense",
        original="go",
        suggestions=["went"],
        start=2,
        end=4,
        severity="high"
    )
]
```

**LLM 输出** (ZhipuAI):
```python
llm_result = LLMResult(
    corrected_text="I went to school yesterday.",
    text_type="sentence",
    tone="neutral",
    changes=[
        {
            "original": "go",
            "corrected": "went",
            "explanation": "Past tense should be used for past actions.",
            "type": "tense",
            "severity": "high"
        }
    ]
)
```

**期望的合并结果**:
```python
expected_result = {
    "corrected_text": "I went to school yesterday.",
    "errors": [
        {
            "id": "err_0",
            "type": "tense",
            "subtype": "VERB_TENSE",
            "original": "go",
            "correction": "went",
            "position": {"start": 2, "end": 4},
            "explanation": "This sentence requires the past tense.",
            "severity": "high"
        }
    ],
    "statistics": {
        "total": 1,
        "by_type": {"tense": 1}
    }
}
```

**断言**:
```python
assert result["corrected_text"] == "I went to school yesterday."
assert len(result["errors"]) == 1
assert result["errors"][0]["type"] == "tense"
assert result["errors"][0]["original"] == "go"
assert result["errors"][0]["correction"] == "went"
```

---

### 3.2 测试用例 2: Natural 模式 - Chinglish 表达

**输入**:
```python
original_text = "I very like English."
mode = "natural"
```

**规则引擎输出**:
```python
rule_errors = [
    GrammarError(
        rule_id="VERY_ADJECTIVE",
        message="The adverb 'very' cannot be used before the verb 'like'.",
        category="grammar",
        original="very like",
        suggestions=["really like", "like ... very much"],
        start=2,
        end=11,
        severity="medium"
    )
]
```

**LLM 输出**:
```python
llm_result = LLMResult(
    corrected_text="I really enjoy English.",
    text_type="sentence",
    tone="informal",
    changes=[
        {
            "original": "very like",
            "corrected": "really enjoy",
            "explanation": "'Very like' is a Chinglish expression. Native speakers say 'really enjoy' or 'really like'.",
            "type": "chinglish",
            "severity": "medium"
        }
    ]
)
```

**期望的合并结果**:
```python
expected_result = {
    "corrected_text": "I really enjoy English.",
    "errors": [
        {
            "id": "llm_0",
            "type": "chinglish",
            "subtype": "literal_translation",
            "original": "very like",
            "correction": "really enjoy",
            "position": {"start": 2, "end": 11},
            "explanation": "'Very like' is a Chinglish expression. Native speakers say 'really enjoy' or 'really like'.",
            "severity": "medium"
        }
    ],
    "statistics": {
        "total": 1,
        "by_type": {"chinglish": 1}
    }
}
```

**断言**:
```python
assert result["corrected_text"] == "I really enjoy English."
assert len(result["errors"]) == 1
# Natural 模式以 LLM 为主，所以位置基于原文查找
assert result["errors"][0]["type"] == "chinglish"
```

---

### 3.3 测试用例 3: Accuracy 模式 - 多个错误，包含重叠

**输入**:
```python
original_text = "I very like going to school. The teacher teach us math."
mode = "accuracy"
```

**规则引擎输出**:
```python
rule_errors = [
    GrammarError(
        rule_id="VERY_ADJECTIVE",
        message="The adverb 'very' cannot be used before the verb 'like'.",
        category="grammar",
        original="very like",
        suggestions=["really like"],
        start=2,
        end=11,
        severity="medium"
    ),
    GrammarError(
        rule_id="SUBJECT_VERB_AGREEMENT",
        message="The subject 'teacher' is singular, so the verb should be 'teaches'.",
        category="grammar",
        original="teach",
        suggestions=["teaches"],
        start=38,
        end=43,
        severity="high"
    )
]
```

**LLM 输出**:
```python
llm_result = LLMResult(
    corrected_text="I really like going to school. The teacher teaches us math.",
    text_type="sentence",
    tone="neutral",
    changes=[
        {
            "original": "very like",
            "corrected": "really like",
            "explanation": "Use 'really' instead of 'very' before verbs.",
            "type": "grammar",
            "severity": "medium"
        },
        {
            "original": "teach",
            "corrected": "teaches",
            "explanation": "Subject-verb agreement: 'teacher' (singular) requires 'teaches'.",
            "type": "grammar",
            "severity": "high"
        }
    ]
)
```

**期望的合并结果**:
```python
expected_result = {
    "corrected_text": "I really like going to school. The teacher teaches us math.",
    "errors": [
        {
            "id": "err_0",
            "type": "grammar",
            "subtype": "VERY_ADJECTIVE",
            "original": "very like",
            "correction": "really like",
            "position": {"start": 2, "end": 11},
            "explanation": "The adverb 'very' cannot be used before the verb 'like'.",
            "severity": "medium"
        },
        {
            "id": "err_1",
            "type": "grammar",
            "subtype": "SUBJECT_VERB_AGREEMENT",
            "original": "teach",
            "correction": "teaches",
            "position": {"start": 38, "end": 43},
            "explanation": "The subject 'teacher' is singular, so the verb should be 'teaches'.",
            "severity": "high"
        }
    ],
    "statistics": {
        "total": 2,
        "by_type": {"grammar": 2}
    }
}
```

**断言**:
```python
assert len(result["errors"]) == 2
# 验证位置不重叠
errors = sorted(result["errors"], key=lambda e: e["position"]["start"])
for i in range(len(errors) - 1):
    assert errors[i]["position"]["end"] <= errors[i+1]["position"]["start"]
```

---

### 3.4 测试用例 4: 重叠错误处理

**输入**:
```python
original_text = "I very very like it."
mode = "accuracy"
```

**规则引擎输出**:
```python
rule_errors = [
    GrammarError(
        rule_id="VERY_ADJECTIVE",
        original="very very like",
        suggestions=["really like"],
        start=2,
        end=16,
        severity="medium"
    ),
    GrammarError(
        rule_id="DUPLICATE_WORD",
        original="very very",
        suggestions=["very"],
        start=2,
        end=11,
        severity="low"
    )
]
```

**期望的合并结果**:
```python
expected_result = {
    "corrected_text": "I really like it.",
    "errors": [
        # 应该只保留范围更大的错误
        {
            "id": "err_0",
            "type": "grammar",
            "subtype": "VERY_ADJECTIVE",
            "original": "very very like",
            "correction": "really like",
            "position": {"start": 2, "end": 16},
            "explanation": "The adverb 'very' cannot be used before the verb 'like'.",
            "severity": "medium"
        }
    ],
    "statistics": {
        "total": 1,
        "by_type": {"grammar": 1}
    }
}
```

**断言**:
```python
assert len(result["errors"]) == 1
assert result["errors"][0]["original"] == "very very like"
assert result["errors"][0]["position"]["start"] == 2
assert result["errors"][0]["position"]["end"] == 16
```

---

### 3.5 测试用例 5: Natural 模式 - 大幅重写

**输入**:
```python
original_text = "Yesterday I go park and play ball with friend. We have fun time."
mode = "natural"
```

**规则引擎输出**:
```python
rule_errors = [
    GrammarError(
        rule_id="VERB_TENSE",
        original="go",
        suggestions=["went"],
        start=9,
        end=11,
        severity="high"
    ),
    GrammarError(
        rule_id="MISSING_ARTICLE",
        original="park",
        suggestions=["the park", "a park"],
        start=12,
        end=16,
        severity="medium"
    ),
    GrammarError(
        rule_id="VERB_TENSE",
        original="have",
        suggestions=["had"],
        start=41,
        end=45,
        severity="high"
    )
]
```

**LLM 输出**:
```python
llm_result = LLMResult(
    corrected_text="Yesterday, I went to the park and played ball with my friend. We had a great time.",
    text_type="sentence",
    tone="informal",
    changes=[
        {
            "original": "go park and play ball",
            "corrected": "went to the park and played ball",
            "explanation": "Use past tense for past actions and add articles.",
            "type": "grammar",
            "severity": "high"
        },
        {
            "original": "friend",
            "corrected": "my friend",
            "explanation": "Add possessive 'my' for clarity.",
            "type": "style",
            "severity": "low"
        },
        {
            "original": "have fun time",
            "corrected": "had a great time",
            "explanation": "Use past tense and more natural expression.",
            "type": "style",
            "severity": "medium"
        }
    ]
)
```

**期望的合并结果**:
```python
expected_result = {
    "corrected_text": "Yesterday, I went to the park and played ball with my friend. We had a great time.",
    "errors": [
        {
            "id": "llm_0",
            "type": "grammar",
            "subtype": "llm_suggested",
            "original": "go park and play ball",
            "correction": "went to the park and played ball",
            "position": {"start": 9, "end": 34},
            "explanation": "Use past tense for past actions and add articles.",
            "severity": "high"
        },
        {
            "id": "llm_1",
            "type": "style",
            "subtype": "llm_suggested",
            "original": "friend",
            "correction": "my friend",
            "position": {"start": 49, "end": 55},
            "explanation": "Add possessive 'my' for clarity.",
            "severity": "low"
        },
        {
            "id": "llm_2",
            "type": "style",
            "subtype": "llm_suggested",
            "original": "have fun time",
            "correction": "had a great time",
            "position": {"start": 41, "end": 54},
            "explanation": "Use past tense and more natural expression.",
            "severity": "medium"
        }
    ],
    "statistics": {
        "total": 3,
        "by_type": {"grammar": 1, "style": 2}
    }
}
```

**断言**:
```python
assert len(result["errors"]) == 3
assert result["corrected_text"] == llm_result.corrected_text
# 验证无重叠
positions = [(e["position"]["start"], e["position"]["end"]) for e in result["errors"]]
for i in range(len(positions) - 1):
    assert positions[i][1] <= positions[i+1][0], f"Overlap detected: {positions[i]} vs {positions[i+1]}"
```

---

### 3.6 测试用例 6: 中英混合文本

**输入**:
```python
original_text = "I like 吃饭. It is very good."
mode = "accuracy"
```

**预处理输出**:
```python
preprocessed = PreprocessedText(
    cleaned="I like 吃饭. It is very good.",
    has_chinese=True,
    chinese_ratio=0.15
)
```

**规则引擎输出**:
```python
rule_errors = [
    GrammarError(
        rule_id="VERY_ADJECTIVE",
        original="very good",
        suggestions=["really good", "excellent"],
        start=21,
        end=30,
        severity="low"
    )
]
```

**LLM 输出**:
```python
llm_result = LLMResult(
    corrected_text="I like eating. It is really good.",
    text_type="mixed",
    tone="informal",
    changes=[
        {
            "original": "吃饭",
            "corrected": "eating",
            "explanation": "'吃饭' means 'to eat' or 'eating' in this context.",
            "type": "mixed_language",
            "severity": "medium"
        },
        {
            "original": "very good",
            "corrected": "really good",
            "explanation": "Use 'really' instead of 'very' for stronger emphasis.",
            "type": "word_choice",
            "severity": "low"
        }
    ]
)
```

**期望的合并结果**:
```python
expected_result = {
    "corrected_text": "I like eating. It is really good.",
    "errors": [
        {
            "id": "llm_0",
            "type": "mixed_language",
            "subtype": "llm_suggested",
            "original": "吃饭",
            "correction": "eating",
            "position": {"start": 7, "end": 9},  # 中文在原文的位置
            "explanation": "'吃饭' means 'to eat' or 'eating' in this context.",
            "severity": "medium"
        },
        {
            "id": "err_0",
            "type": "word_choice",
            "subtype": "VERY_ADJECTIVE",
            "original": "very good",
            "correction": "really good",
            "position": {"start": 21, "end": 30},
            "explanation": "The adverb 'very' cannot be used before the adjective 'good'.",
            "severity": "low"
        }
    ],
    "statistics": {
        "total": 2,
        "by_type": {"mixed_language": 1, "word_choice": 1}
    }
}
```

---

### 3.7 单元测试实现示例

```python
# tests/test_merger.py

import pytest
from pipeline.merger import Merger
from pipeline.llm_engine import LLMResult
from pipeline.rule_engine import GrammarError

class TestMerger:
    """Merger 单元测试"""

    @pytest.fixture
    def merger(self):
        return Merger()

    @pytest.mark.asyncio
    async def test_accuracy_mode_simple_tense_error(self, merger):
        """测试 Accuracy 模式 - 简单时态错误"""
        original_text = "I go to school yesterday."

        rule_errors = [
            GrammarError(
                rule_id="VERB_TENSE",
                message="This sentence requires the past tense.",
                category="tense",
                original="go",
                suggestions=["went"],
                start=2,
                end=4,
                severity="high"
            )
        ]

        llm_result = LLMResult(
            corrected_text="I went to school yesterday.",
            text_type="sentence",
            tone="neutral",
            changes=[
                {
                    "original": "go",
                    "corrected": "went",
                    "explanation": "Past tense should be used.",
                    "type": "tense",
                    "severity": "high"
                }
            ]
        )

        result = await merger.merge(original_text, rule_errors, llm_result, "accuracy")

        assert result["corrected_text"] == "I went to school yesterday."
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "tense"
        assert result["errors"][0]["original"] == "go"
        assert result["errors"][0]["correction"] == "went"
        assert result["statistics"]["total"] == 1

    @pytest.mark.asyncio
    async def test_overlapping_errors_resolution(self, merger):
        """测试重叠错误处理"""
        original_text = "I very very like it."

        rule_errors = [
            GrammarError(
                rule_id="VERY_ADJECTIVE",
                message="Cannot use 'very' before 'like'.",
                category="grammar",
                original="very very like",
                suggestions=["really like"],
                start=2,
                end=16,
                severity="medium"
            ),
            GrammarError(
                rule_id="DUPLICATE_WORD",
                message="Duplicate word 'very'.",
                category="style",
                original="very very",
                suggestions=["very"],
                start=2,
                end=11,
                severity="low"
            )
        ]

        llm_result = LLMResult(
            corrected_text="I really like it.",
            text_type="sentence",
            tone="neutral",
            changes=[]
        )

        result = await merger.merge(original_text, rule_errors, llm_result, "accuracy")

        # 应该只保留范围更大的错误
        assert len(result["errors"]) == 1
        assert result["errors"][0]["original"] == "very very like"
        assert result["errors"][0]["position"]["start"] == 2
        assert result["errors"][0]["position"]["end"] == 16

    @pytest.mark.asyncio
    async def test_natural_mode_major_rewrite(self, merger):
        """测试 Natural 模式 - 大幅重写"""
        original_text = "Yesterday I go park and play ball with friend. We have fun time."

        rule_errors = [
            GrammarError(
                rule_id="VERB_TENSE",
                message="Use past tense.",
                category="tense",
                original="go",
                suggestions=["went"],
                start=9,
                end=11,
                severity="high"
            )
            # ... 其他错误
        ]

        llm_result = LLMResult(
            corrected_text="Yesterday, I went to the park and played ball with my friend. We had a great time.",
            text_type="sentence",
            tone="informal",
            changes=[
                {
                    "original": "go park and play ball",
                    "corrected": "went to the park and played ball",
                    "explanation": "Use past tense.",
                    "type": "grammar",
                    "severity": "high"
                }
                # ... 其他 changes
            ]
        )

        result = await merger.merge(original_text, rule_errors, llm_result, "natural")

        assert result["corrected_text"] == llm_result.corrected_text
        assert len(result["errors"]) >= 1

        # 验证无重叠
        errors = sorted(result["errors"], key=lambda e: e["position"]["start"])
        for i in range(len(errors) - 1):
            assert errors[i]["position"]["end"] <= errors[i+1]["position"]["start"]
```

---

## 总结

本补充文档涵盖了三个关键补充：

1. **Token 消耗监控** - 完整的成本追踪和统计
2. **前端 Store 设计** - Pinia 状态管理架构
3. **Merger 测试用例** - 详细的测试基准

这些补充确保了：
- ✅ 成本可控和可追踪
- ✅ 前后端数据结构无缝对接
- ✅ 复杂逻辑有测试基准

**文档版本**: v2.1
**最后更新**: 2026-01-20
