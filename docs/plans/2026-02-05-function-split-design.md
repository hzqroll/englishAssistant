# 功能拆分设计：LanguageTool 与 LLM 分离展示

**版本**: v1.0
**日期**: 2026-02-05
**状态**: 设计完成，待实施

---

## 1. 背景与目标

### 问题

初期版本功能过于复杂，LanguageTool 和 LLM 配合解析存在以下问题：
- 解析速度慢（用户需等待两个引擎都完成）
- 解析结果类似（无法区分哪些来自规则引擎，哪些来自 AI）
- 用户无法选择性使用（LLM 消耗 Token，不应强制使用）

### 目标

1. **功能拆分**：将 LanguageTool（规则引擎）和 LLM（AI 优化）拆分为独立功能
2. **左右栏展示**：在一个页面中左右栏分别展示两种分析结果
3. **性能优化**：
   - 规则检测快速返回（~2-4秒）
   - LLM 可选执行（用户决定是否消耗 Token）
4. **学习价值**：增加智能学习建议，基于错误模式提供个性化学习路径

---

## 2. 功能定位

### LanguageTool（规则检测）

**擅长领域**：
- ✅ 拼写错误（TYPOS）
- ✅ 语法错误（GRAMMAR）
- ✅ 标点符号（PUNCTUATION）
- ✅ 大小写（CASING）
- ✅ 冗余表达（REDUNDANCY）

**特点**：
- 速度快（2-4 秒）
- 100% 确定性
- 免费
- 提供具体语法规则（Rule ID）

**不擅长**：
- ❌ 深层语义理解
- ❌ 风格优化
- ❌ 句式重写
- ❌ 中英混用处理

### LLM（AI 深度优化）

**擅长领域**：
- ✅ 语境理解
- ✅ 句式重写
- ✅ 流畅度优化
- ✅ 中英混用纠正
- ✅ 风格建议（正式/口语）
- ✅ 学习建议生成

**特点**：
- 理解深层语义
- 提供多种风格选项
- 个性化学习分析
- 消耗 Token（成本考量）

**不擅长**：
- ⚠️ 可能产生幻觉
- ⚠️ 速度相对慢（3-5 秒）
- ⚠️ 有时过度修改

---

## 3. 用户流程设计

### Sequential Analysis Flow

```
用户输入文本
    ↓
点击"分析"按钮
    ↓
[Stage 1] LanguageTool 分析（2-4秒）
    ↓
左侧面板显示规则检测结果
    ↓
右侧面板显示"AI 优化"选项（未执行状态）
    ↓
用户评估：LanguageTool 结果是否满足需求？
    ├─ 满足 → 完成，无需 LLM
    └─ 不满足 → 点击"✨ AI 深度优化"按钮
        ↓
        [Stage 2] LLM 分析（3-5秒，消耗 Token）
        ↓
        右侧面板显示优化结果 + 学习建议
        ↓
        完成
```

### 状态管理

**State 1: 初始状态**
```
左侧面板：显示"等待分析..."占位符
右侧面板：显示"等待规则检测完成"占位符
AI 优化按钮：禁用（灰色）
```

**State 2: LanguageTool 分析中**
```
左侧面板：加载动画 "规则检测中..."
右侧面板：等待状态
AI 优化按钮：禁用
```

**State 3: LanguageTool 完成**
```
左侧面板：显示错误分类、统计、详细错误列表
右侧面板：显示空状态 "点击 AI 优化按钮进行深度分析"
AI 优化按钮：启用（蓝色）+ 显示预估 Token 消耗
```

**State 4: LLM 分析中**
```
左侧面板：稍微变暗（dim）
右侧面板：加载动画 "AI 正在分析上下文..."
AI 优化按钮：加载中（spinner）"优化中..."
```

**State 5: LLM 完成**
```
左侧面板：正常显示
右侧面板：显示优化建议、学习分析、进步趋势
AI 优化按钮：绿色勾选 "优化完成" + 显示实际 Token 消耗
```

---

## 4. 前端组件设计

### 4.1 新增组件

#### RuleEnginePanel.vue
**职责**：显示 LanguageTool 分析结果

**UI 结构**：
```
┌─────────────────────────────────────┐
│ 规则检测 (LanguageTool)             │
│ ⚡ 2.3秒 | 发现 5 个错误            │
├─────────────────────────────────────┤
│ [错误统计]                          │
│ 🔴 语法错误 (3)                     │
│ 🟡 拼写错误 (2)                     │
│ 🟠 时态错误 (1)                     │
│                                     │
│ [错误详情列表]                      │
│ ┌─────────────────────────────────┐ │
│ │ 🔴 语法错误                      │ │
│ │ She dont like → doesn't        │ │
│ │ Rule: HE_DONT                  │ │
│ │ 解释: 主谓一致，第三人称单数     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**数据结构**：
```typescript
interface RuleBasedResult {
  analysis_id: string
  errors: Array<{
    rule_id: string        // HE_DONT
    category: string       // GRAMMAR, TYPOS, etc.
    severity: string       // ERROR, WARNING
    position: { start: number; end: number }
    original_text: string
    replacements: string[]
    message: string
    context: string
  }>
  corrected_text: string
  statistics: {
    total_errors: number
    by_category: Record<string, number>
  }
  processing_time_ms: number
  estimated_llm_tokens: number
}
```

#### LLMPanel.vue
**职责**：显示 LLM 优化结果 + 学习建议

**UI 结构**：
```
┌─────────────────────────────────────┐
│ AI 深度优化 (LLM)                   │
│ ✨ 12 tokens | 3 条建议             │
├─────────────────────────────────────┤
│ [句子级优化]                        │
│ 原文: She dont like pizza           │
│ LT: She doesn't like pizza         │
│ AI: She doesn't really like pizza  │
│ 💡 添加 "really" 增强口语自然度     │
│                                     │
│ [学习建议]                          │
│ 📊 你的错误分布                     │
│ 主谓一致    ████░ 43% 🔴           │
│ 第三人称单数 ███░░ 28% 🟡          │
│                                     │
│ 🎯 优先学习：主谓一致规则           │
│ 问题：第三人称单数动词变化不正确    │
│ 资源：语法规则 + 专项练习           │
│ 预计：30 分钟                       │
│                                     │
│ 📈 进步趋势                         │
│ ✅ 较上周：-12% 错误率              │
│ ⭐ 最大进步：时态错误               │
└─────────────────────────────────────┘
```

**数据结构**：
```typescript
interface LLMResult {
  optimized_text: string
  suggestions: Array<{
    type: string  // naturalness, style_variant, etc.
    sentence_index: number
    original: string
    suggestion: string
    explanation: string
    confidence: number
  }>
  chinese_corrections: Array<{
    original: string
    corrected: string
  }>
  learning_analysis: {
    error_patterns: Array<{
      pattern_name: string
      frequency: string      // "43%"
      examples: Array<{original: string, corrected: string}>
      severity: string       // high, medium, low
    }>
    learning_recommendations: Array<{
      priority: number
      topic: string
      description: string
      resources: Array<{
        type: string        // grammar_rule, practice_exercise
        title: string
        content?: string
      }>
      estimated_study_time: string
    }>
    historical_trend?: {
      comparison: string     // improving, stable, worsening
      since_last_week: string
      most_improved: string
      needs_attention: string
    }
    personalized_tips: string[]
  }
  token_usage: number
}
```

#### AIOptimizeButton.vue
**职责**：触发 LLM 分析的浮动按钮

**位置**：绝对定位在两个面板之间

**状态**：
- **Disabled**（灰色）: 等待 LanguageTool 完成
- **Enabled**（蓝色）: 可点击，显示预估 Token
- **Loading**（蓝色 + spinner）: "优化中..."
- **Completed**（绿色 + 勾选）: "优化完成 (12 tokens)"

**UI**：
```
    ┌─────────────────┐
    │  ✨ AI深度优化   │
    │  ~15 tokens     │
    └─────────────────┘
```

### 4.2 布局调整

**更新 MainLayout.vue**：

```vue
<template>
  <div class="flex gap-4 h-[calc(100vh-200px)]">
    <!-- 左侧：输入面板 (30%) -->
    <div class="w-[30%]">
      <InputPanel />
    </div>

    <!-- 中间：LanguageTool 结果 (35%) -->
    <div class="w-[35%] relative">
      <RuleEnginePanel />
    </div>

    <!-- 右侧：LLM 结果 (35%) -->
    <div class="w-[35%]">
      <LLMPanel />
    </div>

    <!-- 浮动按钮：AI 优化触发器 -->
    <AIOptimizeButton class="absolute left-[65%] top-1/2" />
  </div>
</template>
```

---

## 5. 后端设计

### 5.1 Pipeline 重构

**现有架构**：
```python
AnalysisPipeline.analyze(text, mode)
  ├─ Stage 1: Preprocessing
  ├─ Stage 2: Rule-based (LanguageTool)
  ├─ Stage 3: LLM Optimization
  └─ Stage 4: Merging
```

**新架构**：
```python
AnalysisPipeline
  ├─ analyze_rules_only(text, mode)  # 新增：仅规则检测
  │   ├─ Stage 1: Preprocessing
  │   └─ Stage 2: Rule-based
  │
  └─ optimize_with_llm(analysis_id)  # 新增：LLM 优化
      ├─ Stage 3: LLM Optimization
      ├─ Stage 4: Merging
      └─ Stage 5: Learning Analysis (新增)
```

### 5.2 新增方法

#### analyze_rules_only()

```python
async def analyze_rules_only(
    self,
    text: str,
    mode: CorrectionMode,
    user_id: Optional[str] = None
) -> RuleBasedResult:
    """
    快速分析路径：仅使用 LanguageTool

    Returns:
        - analysis_id: 用于后续 LLM 优化
        - errors: 错误详情列表
        - corrected_text: 修正后文本
        - estimated_llm_tokens: 预估 LLM 消耗
    """
    # Stage 1: Preprocessing
    preprocessed = await self.preprocessor.preprocess(text)

    # Stage 2: LanguageTool
    rule_result = await self.rule_engine.check(preprocessed, mode)

    # 保存到数据库（状态: rule_only）
    analysis = await self._save_analysis(
        user_id=user_id,
        original_text=text,
        rule_result=rule_result,
        status='rule_only'
    )

    # 预估 LLM Token 消耗
    estimated_tokens = self._estimate_llm_tokens(text)

    return RuleBasedResult(
        analysis_id=analysis.id,
        errors=rule_result.errors,
        corrected_text=rule_result.corrected_text,
        statistics=self._calculate_statistics(rule_result.errors),
        processing_time_ms=rule_result.processing_time,
        estimated_llm_tokens=estimated_tokens
    )
```

#### optimize_with_llm()

```python
async def optimize_with_llm(
    self,
    analysis_id: str,
    user_id: Optional[str] = None
) -> LLMResult:
    """
    在现有分析基础上运行 LLM 优化

    包含：
    1. 句子优化建议
    2. 中英混用纠正
    3. 学习建议生成
    """
    # 加载已有分析
    analysis = await self.db.get_analysis(analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    # 检查用户 Token 额度
    await self._check_llm_quota(user_id)

    # Stage 3: LLM Optimization
    llm_result = await self.llm_engine.optimize(
        original_text=analysis.original_text,
        rule_corrections=analysis.rule_corrections
    )

    # Stage 4: Merging
    merged = await self.merger.merge(
        rule_result=analysis.rule_corrections,
        llm_result=llm_result
    )

    # Stage 5: Learning Analysis (新增)
    learning_analysis = await self.llm_engine.generate_learning_insights(
        lt_errors=analysis.rule_corrections.errors,
        user_history=await self._get_user_error_history(user_id, days=30)
    )

    # 保存学习建议到数据库
    await self._save_learning_recommendations(
        user_id=user_id,
        analysis_id=analysis_id,
        learning_analysis=learning_analysis
    )

    # 更新分析状态
    await self.db.update_analysis(
        analysis_id=analysis_id,
        llm_result=merged,
        token_usage=llm_result.token_count,
        status='completed'
    )

    # 扣除用户 Token
    await self.credit_service.deduct(user_id, llm_result.token_count)

    return LLMResult(
        optimized_text=merged.final_text,
        suggestions=llm_result.suggestions,
        chinese_corrections=llm_result.chinese_corrections,
        learning_analysis=learning_analysis,
        token_usage=llm_result.token_count
    )
```

### 5.3 LLM Prompt 设计

#### 学习建议生成 Prompt

```python
async def generate_learning_insights(
    self,
    lt_errors: List[GrammarError],
    user_history: Optional[List[ErrorDetail]] = None
) -> LearningAnalysis:
    """
    基于 LanguageTool 错误生成个性化学习建议
    """
    # 分析错误模式
    error_patterns = self._extract_patterns(lt_errors)

    # 构建历史上下文
    historical_context = ""
    if user_history:
        trends = self._analyze_trends(user_history)
        historical_context = f"""

用户历史错误趋势（最近30天）：
- 总分析次数: {trends['total_analyses']}
- 总错误数: {trends['total_errors']}
- Top 3 错误类型:
  1. {trends['top_patterns'][0]['name']}: {trends['top_patterns'][0]['count']} 次
  2. {trends['top_patterns'][1]['name']}: {trends['top_patterns'][1]['count']} 次
  3. {trends['top_patterns'][2]['name']}: {trends['top_patterns'][2]['count']} 次
- 进步趋势: {trends['overall_trend']}
        """

    prompt = f"""
你是一位专业的英语教师，擅长分析学生的语法错误并提供个性化学习建议。

当前分析的错误：
{self._format_error_patterns(error_patterns)}
{historical_context}

请完成以下任务：

1. **错误模式识别**：
   - 找出 3-5 个主要错误模式
   - 计算每种模式的频率占比
   - 评估严重程度（high/medium/low）

2. **学习建议生成**：
   - 对每个模式提供具体的语法解释
   - 推荐学习资源（语法规则、练习题）
   - 估算学习时间

3. **进步分析**（如有历史数据）：
   - 对比本次与历史表现
   - 指出进步最明显的领域
   - 标注需要重点关注的薄弱环节

4. **个性化建议**：
   - 给出 2-3 条实用学习技巧
   - 推荐具体书籍章节或在线资源

请以 JSON 格式返回：
{{
  "error_patterns": [
    {{
      "pattern_name": "主谓一致错误",
      "frequency": "43%",
      "examples": [
        {{"original": "She dont", "corrected": "She doesn't"}},
        {{"original": "He go", "corrected": "He goes"}}
      ],
      "severity": "high"
    }}
  ],
  "learning_recommendations": [
    {{
      "priority": 1,
      "topic": "主谓一致规则",
      "description": "你的主要问题在于第三人称单数动词变化",
      "resources": [
        {{
          "type": "grammar_rule",
          "title": "第三人称单数动词变化规则",
          "content": "在一般现在时中，当主语是第三人称单数..."
        }},
        {{
          "type": "practice_exercise",
          "title": "专项练习：主谓一致",
          "difficulty": "intermediate"
        }}
      ],
      "estimated_study_time": "30分钟"
    }}
  ],
  "historical_trend": {{
    "comparison": "improving",
    "since_last_week": "-12% 错误率",
    "most_improved": "时态错误",
    "needs_attention": "主谓一致"
  }},
  "personalized_tips": [
    "建议在写作时特别注意检查第三人称单数动词",
    "可以使用主谓一致检查工具辅助练习",
    "推荐阅读：English Grammar in Use - Unit 12"
  ]
}}
"""

    response = await self.llm_client.generate(prompt)
    return self._parse_learning_response(response)
```

### 5.4 API 端点

#### POST /api/v1/analyze/rules-only

**请求**：
```json
{
  "text": "She dont like pizza",
  "language": "en-US",
  "mode": "accuracy"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "errors": [
      {
        "rule_id": "HE_DONT",
        "category": "GRAMMAR",
        "severity": "ERROR",
        "position": {"start": 4, "end": 8},
        "original_text": "dont",
        "replacements": ["doesn't", "does"],
        "message": "Did you mean 'doesn't'?",
        "context": "She dont like pizza"
      }
    ],
    "corrected_text": "She doesn't like pizza",
    "statistics": {
      "total_errors": 1,
      "by_category": {
        "GRAMMAR": 1
      }
    },
    "processing_time_ms": 2300,
    "estimated_llm_tokens": 15
  }
}
```

#### POST /api/v1/analyze/optimize-llm

**请求**：
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "optimized_text": "She doesn't really like pizza",
    "suggestions": [
      {
        "type": "naturalness",
        "sentence_index": 0,
        "original": "She doesn't like pizza",
        "suggestion": "She doesn't really like pizza",
        "explanation": "添加强调词 'really' 增强口语自然度",
        "confidence": 0.92
      }
    ],
    "chinese_corrections": [],
    "learning_analysis": {
      "error_patterns": [
        {
          "pattern_name": "主谓一致错误",
          "frequency": "100%",
          "examples": [
            {"original": "She dont", "corrected": "She doesn't"}
          ],
          "severity": "high"
        }
      ],
      "learning_recommendations": [
        {
          "priority": 1,
          "topic": "主谓一致规则",
          "description": "你的主要问题在于第三人称单数动词变化不正确",
          "resources": [
            {
              "type": "grammar_rule",
              "title": "第三人称单数动词变化规则",
              "content": "在一般现在时中，当主语是第三人称单数（he, she, it）时，动词需要加 -s 或 -es..."
            },
            {
              "type": "practice_exercise",
              "title": "专项练习：主谓一致 50 题",
              "difficulty": "intermediate"
            }
          ],
          "estimated_study_time": "30分钟"
        }
      ],
      "personalized_tips": [
        "建议在写作时特别注意检查第三人称单数动词形式",
        "可以使用主谓一致检查工具辅助练习",
        "推荐阅读：English Grammar in Use - Unit 12"
      ]
    },
    "token_usage": 25
  }
}
```

---

## 6. 数据库设计

### 6.1 表结构更新

#### analyses 表（更新）

```sql
ALTER TABLE analyses
ADD COLUMN status VARCHAR(20) DEFAULT 'rule_only',
ADD COLUMN llm_tokens_used INTEGER DEFAULT 0,
ADD COLUMN llm_cost_usd DECIMAL(10,4) DEFAULT 0;

-- status 可选值: 'rule_only', 'completed', 'failed'
```

#### error_details 表（增强）

```sql
CREATE TABLE error_details (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    rule_id VARCHAR(100),           -- LanguageTool rule_id
    category VARCHAR(50),            -- GRAMMAR, TYPOS, etc.
    severity VARCHAR(20),            -- ERROR, WARNING
    position_start INTEGER,
    position_end INTEGER,
    original_text TEXT,
    correction TEXT,
    message TEXT,
    context TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_error_details_rule ON error_details(rule_id);
CREATE INDEX idx_error_details_category ON error_details(category);
```

#### learning_recommendations 表（新增）

```sql
CREATE TABLE learning_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    pattern_name VARCHAR(200),       -- 错误模式名称
    frequency DECIMAL(5,2),          -- 错误频率（百分比）
    severity VARCHAR(20),            -- high, medium, low
    recommendation TEXT,             -- LLM 生成的学习建议
    resources JSONB,                 -- 学习资源（JSON 格式）
    priority INTEGER,                -- 优先级 1,2,3...
    estimated_study_time VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_learning_user_pattern ON learning_recommendations(user_id, pattern_name);
CREATE INDEX idx_learning_analysis ON learning_recommendations(analysis_id);
```

#### user_error_trends 表（新增）

```sql
CREATE TABLE user_error_trends (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pattern_name VARCHAR(200),
    error_count INTEGER DEFAULT 0,
    trend_direction VARCHAR(20),     -- improving, stable, worsening
    last_calculated TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, pattern_name)
);

CREATE INDEX idx_trends_user ON user_error_trends(user_id);
CREATE INDEX idx_trends_pattern ON user_error_trends(pattern_name);
```

### 6.2 数据流

```
用户提交文本
    ↓
POST /analyze/rules-only
    ↓
保存 analyses 记录（status='rule_only'）
保存 error_details 记录（所有 LT 错误）
    ↓
返回结果给前端
    ↓
用户点击 AI 优化
    ↓
POST /analyze/optimize-llm
    ↓
更新 analyses 记录（status='completed', llm_tokens_used）
保存 learning_recommendations 记录
更新 user_error_trends 记录
    ↓
返回结果给前端
```

---

## 7. 实现路线图

### Phase 1: MVP（核心功能）

**后端**：
- ✅ 拆分 Pipeline：`analyze_rules_only()` + `optimize_with_llm()`
- ✅ 新增 API 端点：`/analyze/rules-only`, `/analyze/optimize-llm`
- ✅ 数据库迁移：添加 `status`, `llm_tokens_used` 字段
- ✅ LLM Prompt 设计：学习建议生成

**前端**：
- ✅ 创建 `RuleEnginePanel.vue`
- ✅ 创建 `LLMPanel.vue`
- ✅ 创建 `AIOptimizeButton.vue`
- ✅ 更新 `MainLayout.vue`：3 栏布局
- ✅ Pinia Store 更新：`ruleResult`, `llmResult`, `isOptimizing`

**测试**：
- ✅ 单元测试：Pipeline 方法
- ✅ 集成测试：API 端点
- ✅ E2E 测试：完整用户流程

### Phase 2: 学习分析增强

**后端**：
- 📊 实现历史趋势分析
- 📈 实现进步追踪算法
- 🎯 优化学习建议质量

**前端**：
- 📊 学习建议卡片优化
- 📈 进步趋势可视化（图表）
- 🎯 错误模式分布图

**数据库**：
- 📊 `learning_recommendations` 表
- 📈 `user_error_trends` 表
- 🎯 历史数据聚合查询

### Phase 3: 高级特性

**功能**：
- 🏆 学习成就系统
- 📋 个性化学习路径
- 🤝 智能练习推荐
- 📊 错误统计仪表盘

**优化**：
- ⚡ LanguageTool 远程服务器模式
- 🚀 LLM 批量优化
- 💾 Redis 缓存优化

---

## 8. 成本优化策略

### Token 预估算法

```python
def _estimate_llm_tokens(text: str) -> int:
    """
    预估 LLM Token 消耗

    规则：
    - 英文: ~1 token = 4 字符
    - 中文: ~1 token = 1.5 字符
    - 系统 Prompt: ~500 tokens
    """
    char_count = len(text)
    base_tokens = char_count // 4
    system_tokens = 500
    return base_tokens + system_tokens
```

### 用户引导

**前端显示**：
- 显示预估 Token 消耗
- 显示用户剩余额度
- 如果 LanguageTool 结果已满足需求，提示用户无需 LLM

**示例**：
```
✨ AI 深度优化 (~15 tokens)
💡 提示: LanguageTool 已修复所有明显错误，
         AI 优化主要用于流畅度提升和学习建议
```

---

## 9. 关键设计决策

1. **Sequential vs Parallel**：选择顺序执行而非并行
   - 理由：成本控制 + 用户选择权

2. **LanguageTool 优先**：先执行快速、免费的规则检测
   - 理由：大部分用户可能只需要基础纠错

3. **学习建议由 LLM 生成**：不使用规则引擎
   - 理由：需要深层语义理解和个性化分析

4. **历史记录完整保存**：包括所有错误详情
   - 理由：支持趋势分析和个性化学习路径

5. **浮动按钮设计**：视觉化连接两个面板
   - 理由：明确展示两个工具的关系和流程

---

## 10. 风险与缓解

### 风险 1：用户不使用 LLM
**影响**：产品差异化不足
**缓解**：
- 在空状态明确展示 LLM 能力
- 提供免费试用额度
- 显示学习建议预览

### 风险 2：LanguageTool 速度慢
**影响**：用户体验差
**缓解**：
- 使用单例模式（已实现）
- 生产环境使用远程服务器
- 显示进度条

### 风险 3：学习建议质量不稳定
**影响**：用户信任度降低
**缓解**：
- 精心设计 Prompt
- 多轮测试优化
- 收集用户反馈持续改进

---

## 11. 成功指标

**功能指标**：
- ✅ LanguageTool 响应时间 < 5 秒
- ✅ LLM 响应时间 < 10 秒
- ✅ 错误检测准确率 > 95%

**用户行为指标**：
- 📊 LLM 使用率 > 40%（用户在 40% 的分析中使用 LLM）
- 📊 学习建议阅读率 > 60%
- 📊 用户留存率提升 20%

**成本指标**：
- 💰 平均每次分析 Token 消耗 < 50
- 💰 每月 LLM 成本可控

---

**设计完成日期**: 2026-02-05
**设计师**: Claude Sonnet 4.5
**状态**: ✅ 设计完成，待用户确认后进入实施阶段
