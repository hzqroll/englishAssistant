# English Transfer Assistant - 技术实现方案

**基于 UI 设计的完整实现方案**

**文档版本**: v1.0
**创建日期**: 2026-01-19
**状态**: 设计中

---

## 目录
1. [API 端点设计](#api-端点设计)
2. [前端组件架构](#前端组件架构)
3. [状态管理方案](#状态管理方案)
4. [智谱 AI 集成](#智谱-ai-集成)
5. [LanguageTool 集成](#languagetool-集成)
6. [数据流设计](#数据流设计)
7. [实现待办清单](#实现待办清单)

---

## API 端点设计

### 基础结构
- **Base URL**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON
- **错误码规范**: HTTP 状态码 + 业务错误码

### 核心 API 端点

#### 1. 认证模块

**POST** `/auth/register`
- **描述**: 用户注册
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "password": "hashed_password"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "user_id": "uuid",
      "email": "user@example.com",
      "access_token": "jwt_token",
      "refresh_token": "refresh_token"
    }
  }
  ```

**POST** `/auth/login`
- **描述**: 用户登录
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "password": "hashed_password"
  }
  ```
- **响应**: 同注册

**POST** `/auth/refresh`
- **描述**: 刷新 access token
- **请求体**:
  ```json
  {
    "refresh_token": "refresh_token"
  }
  ```

#### 2. 文本纠错模块

**POST** `/analyze`
- **描述**: 分析并纠正文本
- **认证**: 需要（支持匿名但有限流）
- **请求体**:
  ```json
  {
    "text": "I go to park yesterday.",
    "mode": "accuracy",  // "accuracy" | "natural"
    "options": {
      "detect_speakers": true,
      "detect_chinese": true
    }
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "analysis_id": "uuid",
      "original_text": "I go to park yesterday.",
      "corrected_text": "I went to the park yesterday.",
      "text_type": "sentence",  // "dialogue" | "email" | "essay" | "sentence"
      "tone": "informal",  // "formal" | "informal" | "academic" | "business"
      "speakers_detected": null,
      "errors": [
        {
          "error_id": "uuid",
          "type": "tense",  // "grammar" | "tense" | "word_choice" | "mixed_language"
          "subtype": "past_tense",
          "original": "go",
          "correction": "went",
          "position": {
            "start": 2,
            "end": 4
          },
          "explanation": "过去时应该用 went，不是 go",
          "rule": "不规则动词 go 的过去式是 went",
          "severity": "medium"  // "low" | "medium" | "high"
        }
      ],
      "statistics": {
        "total_errors": 3,
        "by_type": {
          "grammar": 1,
          "tense": 1,
          "word_choice": 1,
          "mixed_language": 0
        }
      },
      "learning_tips": [
        "你最容易犯时态错误（33%）",
        "建议复习不规则动词表"
      ]
    }
  }
  ```

#### 3. 历史记录模块

**GET** `/history`
- **描述**: 获取用户历史记录
- **认证**: 需要
- **查询参数**:
  - `page`: 页码（默认 1）
  - `limit`: 每页数量（默认 10）
  - `type`: 文本类型筛选（可选）
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "total": 45,
      "page": 1,
      "limit": 10,
      "records": [
        {
          "analysis_id": "uuid",
          "original_text": "I go to park...",
          "corrected_text": "I went to the park...",
          "created_at": "2025-01-19T10:30:00Z",
          "text_type": "dialogue",
          "error_count": 3
        }
      ]
    }
  }
  ```

**GET** `/history/{analysis_id}`
- **描述**: 获取单条历史记录详情
- **认证**: 需要
- **响应**: 完整的分析结果（同 `/analyze` 响应）

**DELETE** `/history/{analysis_id}`
- **描述**: 删除单条历史记录
- **认证**: 需要

#### 4. 统计分析模块

**GET** `/statistics/overview`
- **描述**: 获取用户错误统计概览
- **认证**: 需要
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "total_analyses": 127,
      "total_errors": 453,
      "error_distribution": {
        "grammar": 180,
        "tense": 195,
        "word_choice": 58,
        "mixed_language": 20
      },
      "top_errors": [
        {
          "type": "tense",
          "subtype": "past_tense",
          "count": 89,
          "percentage": 19.6
        }
      ],
      "improvement_trend": {
        "this_week": 34,
        "last_week": 42,
        "change": -19.0
      }
    }
  }
  ```

#### 5. 导出模块

**POST** `/export`
- **描述**: 导出分析结果
- **认证**: 需要
- **请求体**:
  ```json
  {
    "analysis_ids": ["uuid1", "uuid2"],
    "format": "markdown"  // "json" | "markdown" | "pdf"
  }
  ```
- **响应**: 文件流（根据 format 返回不同格式）

#### 6. 用户设置模块

**GET** `/settings`
- **描述**: 获取用户设置
- **认证**: 需要
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "default_mode": "accuracy",
      "auto_save": true,
      "theme": "dark"
    }
  }
  ```

**PUT** `/settings`
- **描述**: 更新用户设置
- **认证**: 需要
- **请求体**:
  ```json
  {
    "default_mode": "natural",
    "auto_save": true
  }
  ```

### 错误码规范

| HTTP 状态码 | 业务错误码 | 描述 |
|------------|-----------|------|
| 400 | INVALID_INPUT | 输入无效 |
| 400 | TEXT_TOO_LONG | 文本超出长度限制 |
| 400 | UNSUPPORTED_LANGUAGE | 不支持的语言 |
| 401 | UNAUTHORIZED | 未授权 |
| 401 | TOKEN_EXPIRED | Token 过期 |
| 429 | RATE_LIMIT_EXCEEDED | 超出限流 |
| 500 | ANALYSIS_FAILED | 分析失败 |
| 500 | LLM_ERROR | LLM 服务错误 |
| 500 | GRAMMAR_TOOL_ERROR | 语法检查工具错误 |

---

## 前端组件架构

### 组件树结构

```
App.vue
├── Navbar.vue (导航栏)
│   ├── Logo.vue
│   ├── NavLinks.vue
│   └── UserMenu.vue
│
├── MainLayout.vue (主布局)
│   ├── InputPanel.vue (输入区)
│   │   ├── ModeSwitch.vue (纠正模式切换)
│   │   ├── TextInput.vue (智能文本框)
│   │   ├── CharCounter.vue (字符计数)
│   │   └── ActionButtons.vue (操作按钮)
│   │
│   ├── ComparePanel.vue (对照区)
│   │   ├── ViewToggle.vue (视图切换)
│   │   ├── ErrorStatistics.vue (错误统计)
│   │   ├── SideBySideView.vue (并排视图)
│   │   ├── OriginalOnlyView.vue (仅原文视图)
│   │   ├── CorrectedOnlyView.vue (仅纠正后视图)
│   │   └── ResultActions.vue (结果操作按钮)
│   │
│   └── AnalysisPanel.vue (分析区)
│       ├── SearchAndFilter.vue (搜索和筛选)
│       ├── ErrorCard.vue (错误卡片)
│       │   ├── ErrorHeader.vue
│       │   ├── ErrorDetails.vue
│       │   └── GrammarRule.vue (语法规则)
│       └── LearningTips.vue (学习建议)
│
├── LayoutControls.vue (布局快速切换按钮)
├── Footer.vue (页脚)
└── Toast.vue (全局提示)
```

### 核心组件设计

#### 1. InputPanel.vue
**职责**: 输入区域的容器组件
**Props**: 无
**State**:
- `mode`: 'accuracy' | 'natural'
- `text`: string
- `charCount`: number
- `isAnalyzing`: boolean

**Methods**:
- `handleAnalyze()`: 触发分析
- `handleClear()`: 清空输入
- `handleImport()`: 导入文件

#### 2. ComparePanel.vue
**职责**: 对照区域的容器组件
**Props**:
- `originalText`: string
- `correctedText`: string
- `errors`: Error[]
- `statistics`: Statistics

**State**:
- `currentView`: 'sidebyside' | 'original' | 'corrected'

**Methods**:
- `setView(view)`: 切换视图
- `highlightError(error)`: 高亮错误

#### 3. AnalysisPanel.vue
**职责**: 分析区域的容器组件
**Props**:
- `errors`: Error[]
- `learningTips`: string[]

**State**:
- `searchQuery`: string
- `selectedType`: string | null
- `expandedCards`: Set<string>

**Methods**:
- `filterErrors()`: 筛选错误
- `toggleCard(errorId)`: 展开/折叠卡片

#### 4. ErrorCard.vue
**职责**: 单个错误卡片
**Props**:
- `error`: Error
- `expanded`: boolean

**Events**:
- `@toggle`: 展开/折叠
- `@hover`: 鼠标悬停（联动高亮）

### 组件通信方式

1. **Props Down, Events Up**: 父子组件通信
2. **Pinia Store**: 跨组件状态共享
3. **Event Bus**: 兄弟组件通信（如：点击错误卡片联动高亮）

---

## 状态管理方案

### Store 结构

```typescript
// stores/analysisStore.ts
interface AnalysisState {
  // 当前分析状态
  isAnalyzing: boolean
  currentAnalysis: AnalysisResult | null

  // 输入状态
  inputText: string
  correctionMode: 'accuracy' | 'natural'

  // 视图状态
  currentView: 'sidebyside' | 'original' | 'corrected'
  layoutMode: 'three' | 'input-compare' | 'input-analysis' | 'compare-full'

  // 面板状态
  collapsedPanels: {
    input: boolean
    compare: boolean
    analysis: boolean
  }

  // 错误状态
  selectedErrorId: string | null
  expandedErrorCards: Set<string>
  filterType: string | null
}

// stores/historyStore.ts
interface HistoryState {
  records: HistoryRecord[]
  total: number
  page: number
  loading: boolean
}

// stores/userStore.ts
interface UserState {
  user: User | null
  isAuthenticated: boolean
  settings: UserSettings
  token: string | null
}
```

### 核心 Store 实现

#### Analysis Store
```typescript
// stores/analysisStore.ts
import { defineStore } from 'pinia'
import { analyzeText } from '@/api/analysis'

export const useAnalysisStore = defineStore('analysis', {
  state: (): AnalysisState => ({
    isAnalyzing: false,
    currentAnalysis: null,
    inputText: '',
    correctionMode: 'accuracy',
    currentView: 'sidebyside',
    layoutMode: 'three',
    collapsedPanels: {
      input: false,
      compare: false,
      analysis: false
    },
    selectedErrorId: null,
    expandedErrorCards: new Set(),
    filterType: null
  }),

  actions: {
    async analyzeText(text: string, mode: CorrectionMode) {
      this.isAnalyzing = true
      this.inputText = text
      this.correctionMode = mode

      try {
        const result = await analyzeText({ text, mode })
        this.currentAnalysis = result
        return result
      } catch (error) {
        console.error('Analysis failed:', error)
        throw error
      } finally {
        this.isAnalyzing = false
      }
    },

    setView(view: ViewMode) {
      this.currentView = view
    },

    setLayout(layout: LayoutMode) {
      this.layoutMode = layout
    },

    togglePanel(panel: 'input' | 'compare' | 'analysis') {
      this.collapsedPanels[panel] = !this.collapsedPanels[panel]
    },

    selectError(errorId: string) {
      this.selectedErrorId = errorId
    },

    toggleErrorCard(errorId: string) {
      if (this.expandedErrorCards.has(errorId)) {
        this.expandedErrorCards.delete(errorId)
      } else {
        this.expandedErrorCards.add(errorId)
      }
    },

    setFilterType(type: string | null) {
      this.filterType = type
    },

    clearAnalysis() {
      this.currentAnalysis = null
      this.inputText = ''
      this.selectedErrorId = null
      this.expandedErrorCards.clear()
    }
  }
})
```

---

## 智谱 AI 集成

### API 集成方案

**SDK**: zhipuai (Python)
**API 版本**: v4
**模型**: GLM-4-Flash（快速响应）

### 核心功能实现

#### 1. 文本意图识别

```python
# services/zhipu_service.py
from zhipuai import ZhipuAI

class ZhipuService:
    def __init__(self, api_key: str):
        self.client = ZhipuAI(api_key=api_key)

    async def detect_intent(self, text: str) -> IntentResult:
        """检测文本意图"""
        prompt = f"""
分析以下英文文本的特征，返回 JSON 格式：

文本：{text}

请识别：
1. text_type: 文本类型（dialogue/email/essay/sentence/mixed）
2. tone: 语气（formal/informal/academic/business）
3. speakers: 说话人数量（如果是对话）
4. has_chinese: 是否包含中文（true/false）

只返回 JSON，不要其他内容。
"""

        response = await self.client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": "你是一个文本分析专家"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return IntentResult(**result)
```

#### 2. 自然度优化

```python
async def optimize_naturalness(self, text: str, intent: IntentResult) -> str:
    """优化文本自然度"""
    prompt = f"""
优化以下英文文本的表达，使其更地道、更自然。

文本类型：{intent.text_type}
语气：{intent.tone}

原文：{text}

要求：
1. 保持原文的语气和风格
2. 修正语法错误
3. 优化不自然的表达
4. 只返回优化后的文本，不要解释
"""

    response = await self.client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是一个英语写作专家"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
```

#### 3. 中英混用纠正

```python
async def suggest_english_alternative(self, chinese_word: str, context: str) -> str:
    """为中文词汇建议英文替代"""
    prompt = f"""
上下文：{context}
中文词汇：{chinese_word}

请提供最合适的英文替代词（只返回单词，不要解释）。
"""

    response = await self.client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是一个英汉翻译专家"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content.strip()
```

### 成本优化策略

1. **使用 Flash 模型**: GLM-4-Flash 比 GLM-4 便宜 10 倍
2. **批量处理**: 一次 API 调用处理多个句子
3. **缓存机制**: 相同文本 24 小时内不重复调用
4. **降级策略**: API 失败时使用规则引擎兜底

---

## LanguageTool 集成

### Python 集成

```python
# services/language_tool_service.py
import language_tool_python
from typing import List

class LanguageToolService:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')

    async def check_grammar(self, text: str) -> List[GrammarError]:
        """检查语法错误"""
        matches = self.tool.check(text)

        errors = []
        for match in matches:
            error = GrammarError(
                type=self._classify_error(match),
                subtype=match.ruleId,
                original=text[match.offset:match.offset + match.errorLength],
                suggestion=match.replacements[0] if match.replacements else "",
                position={
                    "start": match.offset,
                    "end": match.offset + match.errorLength
                },
                message=match.message,
                rule_id=match.ruleId
            )
            errors.append(error)

        return errors

    def _classify_error(self, match) -> str:
        """分类错误类型"""
        category = match.category
        rule_id = match.ruleId

        if "TENSE" in category or "TENSE" in rule_id:
            return "tense"
        elif "GRAMMAR" in category:
            return "grammar"
        elif "WORD" in category or "TYPOS" in category:
            return "word_choice"
        else:
            return "grammar"
```

### 错误映射到 UI 分类

```python
ERROR_TYPE_MAPPING = {
    # LanguageTool 分类 -> UI 分类
    "tense": {
        "main_type": "tense",
        "subtype": "past_tense",
        "color": "orange",
        "icon": "↻"
    },
    "grammar": {
        "main_type": "grammar",
        "subtype": "subject_verb_agreement",
        "color": "red",
        "icon": "━━"
    },
    "word_choice": {
        "main_type": "word_choice",
        "subtype": "confused_words",
        "color": "purple",
        "icon": "Aa"
    }
}
```

---

## 数据流设计

### 分析流程数据流

```
用户输入文本
    ↓
InputPanel.vue (输入)
    ↓
analysisStore.analyzeText()
    ↓
POST /api/v1/analyze
    ↓
后端 FastAPI
    ↓
┌─────────────────────────────┐
│  Pipeline (4 阶段流水线)     │
│                             │
│ 1. 预处理                   │
│    - 分句                   │
│    - 说话人识别              │
│    - 中文检测                │
│                             │
│ 2. 规则纠错 (LanguageTool)  │
│    - 语法检查               │
│    - 拼写检查               │
│    - 时态检查               │
│                             │
│ 3. LLM 优化 (智谱 AI)       │
│    - 意图识别               │
│    - 自然度优化             │
│    - 中英混用纠正           │
│                             │
│ 4. 后处理                   │
│    - 合并结果               │
│    - 格式化输出             │
│    - 生成错误报告           │
└─────────────────────────────┘
    ↓
返回 JSON 响应
    ↓
analysisStore 保存结果
    ↓
ComparePanel + AnalysisPanel 更新 UI
```

### 错误高亮联动数据流

```
用户在 AnalysisPanel 点击错误卡片
    ↓
analysisStore.selectError(errorId)
    ↓
Pinia store 状态更新
    ↓
ComparePanel 监听 selectedErrorId
    ↓
高亮对应的错误位置
    ↓
滚动到错误位置
```

---

## 实现待办清单

### Phase 2.5: 技术设计完善

- [x] 创建技术实现方案文档
- [ ] 完成 API 端点详细设计
- [ ] 完成前端组件详细设计
- [ ] 完成状态管理详细设计
- [ ] 完成 Pipeline 流水线详细设计
- [ ] 完成数据库表结构调整（基于新需求）
- [ ] 完成智谱 AI 集成详细设计
- [ ] 完成 LanguageTool 集成详细设计

### Phase 3: Implementation

#### 3.1 项目初始化
- [ ] 创建后端项目结构
  - [ ] 初始化 FastAPI 项目
  - [ ] 配置 Poetry 依赖管理
  - [ ] 配置 Pytest 测试框架
  - [ ] 配置 Black + Ruff 格式化
- [ ] 创建前端项目结构
  - [ ] 初始化 Vue 3 + Vite 项目
  - [ ] 配置 TypeScript
  - [ ] 安装 Tailwind CSS
  - [ ] 配置 ESLint + Prettier
- [ ] 配置开发环境
  - [ ] Docker Compose（PostgreSQL + Redis）
  - [ ] 环境变量配置
  - [ ] Git hooks（pre-commit）

#### 3.2 后端实现

**基础框架**
- [ ] FastAPI 应用初始化
- [ ] CORS 中间件配置
- [ ] JWT 认证中间件
- [ ] 限流中间件（Redis）
- [ ] 错误处理中间件
- [ ] 请求日志中间件

**数据库层**
- [ ] SQLAlchemy 模型定义
  - [ ] User 模型
  - [ ] Analysis 模型（重命名自 Conversation）
  - [ ] ErrorDetail 模型
  - [ ] RequestLog 模型
- [ ] Alembic 数据库迁移
- [ ] 数据库索引优化
- [ ] 数据仓库层（Repository）

**认证模块**
- [ ] JWT Token 生成和验证
- [ ] 用户注册 API
- [ ] 用户登录 API
- [ ] Token 刷新 API
- [ ] 密码哈希（bcrypt）

**流水线核心**
- [ ] Pipeline 阶段 1：预处理
  - [ ] 句子分割器
  - [ ] 说话人识别器
  - [ ] 中文检测器
- [ ] Pipeline 阶段 2：规则纠错
  - [ ] LanguageTool 服务
  - [ ] 错误分类器
  - [ ] 错误严重程度评估
- [ ] Pipeline 阶段 3：LLM 优化
  - [ ] 智谱 AI 服务
  - [ ] 意图识别
  - [ ] 自然度优化
  - [ ] 中英混用纠正
- [ ] Pipeline 阶段 4：后处理
  - [ ] 结果合并器
  - [ ] 错误报告生成器
  - [ ] 学习建议生成器

**API 端点**
- [ ] POST /api/v1/analyze
- [ ] GET /api/v1/history
- [ ] GET /api/v1/history/{id}
- [ ] DELETE /api/v1/history/{id}
- [ ] GET /api/v1/statistics/overview
- [ ] POST /api/v1/export
- [ ] GET /api/v1/settings
- [ ] PUT /api/v1/settings

**外部服务集成**
- [ ] 智谱 AI 客户端封装
- [ ] LanguageTool 客户端封装
- [ ] Redis 客户端（限流）
- [ ] 错误重试机制
- [ ] 降级策略

#### 3.3 前端实现

**基础框架**
- [ ] Vue Router 配置
- [ ] Pinia Store 配置
- [ ] Axios HTTP 客户端
- [ ] 全局样式（Tailwind）
- [ ] 响应式布局

**核心组件**
- [ ] Navbar.vue
- [ ] InputPanel.vue
  - [ ] ModeSwitch.vue
  - [ ] TextInput.vue
  - [ ] CharCounter.vue
  - [ ] ActionButtons.vue
- [ ] ComparePanel.vue
  - [ ] ViewToggle.vue
  - [ ] ErrorStatistics.vue
  - [ ] SideBySideView.vue
  - [ ] OriginalOnlyView.vue
  - [ ] CorrectedOnlyView.vue
  - [ ] ResultActions.vue
- [ ] AnalysisPanel.vue
  - [ ] SearchAndFilter.vue
  - [ ] ErrorCard.vue
  - [ ] LearningTips.vue
- [ ] LayoutControls.vue
- [ ] Footer.vue
- [ ] Toast.vue

**Pinia Stores**
- [ ] analysisStore.ts
- [ ] historyStore.ts
- [ ] userStore.ts
- [ ] uiStore.ts

**API 客户端**
- [ ] API 基础配置
- [ ] 认证拦截器
- [ ] 错误处理拦截器
- [ ] API 方法封装
  - [ ] authApi
  - [ ] analysisApi
  - [ ] historyApi
  - [ ] statisticsApi
  - [ ] exportApi
  - [ ] settingsApi

**交互逻辑**
- [ ] 错误卡片点击联动高亮
- [ ] 区域折叠动画
- [ ] 布局切换逻辑
- [ ] 视图切换逻辑
- [ ] 加载状态处理
- [ ] 错误提示处理

#### 3.4 测试

**后端测试**
- [ ] Pipeline 各阶段单元测试
- [ ] API 端点集成测试
- [ ] 智谱 AI 服务 Mock 测试
- [ ] LanguageTool 服务 Mock 测试
- [ ] 限流中间件测试
- [ ] JWT 认证测试

**前端测试**
- [ ] 组件单元测试（Vitest）
- [ ] Store 单元测试
- [ ] API 客户端测试
- [ ] E2E 测试（Playwright）

**性能测试**
- [ ] API 并发测试
- [ ] Pipeline 处理时间测试
- [ ] 前端渲染性能测试

#### 3.5 部署准备

- [ ] Docker 镜像构建
  - [ ] 后端 Dockerfile
  - [ ] 前端 Dockerfile
  - [ ] Nginx 配置
- [ ] Docker Compose 编排
- [ ] 环境变量文档
- [ ] 部署脚本
- [ ] 监控配置（日志）

---

## 优先级排序

### P0 (MVP 必需)
1. 后端：Pipeline 基础流程
2. 后端：核心 API（analyze, history）
3. 前端：三栏布局基础组件
4. 前端：分析结果显示
5. 集成：智谱 AI + LanguageTool

### P1 (重要但不阻塞 MVP)
1. 后端：认证模块
2. 后端：统计模块
3. 前端：历史记录功能
4. 前端：区域折叠功能
5. 前端：布局切换功能

### P2 (增强功能)
1. 后端：导出模块
2. 前端：视图切换（仅原文/仅纠正后）
3. 前端：搜索和筛选功能
4. 前端：学习建议展示
5. 优化：错误卡片展开动画

---

## 技术风险与应对

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 智谱 AI API 不稳定 | 高 | 中 | 降级到纯规则引擎 |
| LanguageTool 性能问题 | 中 | 中 | 异步处理 + 缓存 |
| 前端状态管理复杂 | 中 | 高 | 使用 Pinia，简化状态流 |
| Pipeline 处理时间长 | 高 | 中 | 流式返回结果 + 进度提示 |
| 成本超预算 | 高 | 中 | 严格限流 + Flash 模型 |

---

**文档状态**: ✅ 完成
**下一步**: 开始 Phase 3.1 - 项目初始化
