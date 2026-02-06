# Function Split Feature Implementation Plan

**Goal:** Implement sequential analysis with LanguageTool (fast, free) and optional LLM optimization (costly, AI-powered) with learning recommendations

**Architecture:** Split the current 4-stage pipeline into two sequential phases:
- Phase 1: Preprocessing + LanguageTool (rules-only) - returns in 2-4 seconds
- Phase 2: Optional LLM optimization + learning insights - triggered by user, costs tokens

**Tech Stack:** Python 3.11+, FastAPI, LanguageTool, Zhipu AI GLM-4, PostgreSQL, SQLAlchemy

---

## Plan (v2, Goal-First / End-to-End Accurate)

这份计划以“更准确完成目标”为第一优先级（即便重构量变大也接受），并以端到端可用为准绳。

### Target Outcomes（按目标验收）

1. **两阶段体验**
   - Phase 1（免费/快速）：只跑 Preprocess + LanguageTool，**2–4 秒**返回规则修正结果与错误列表。
   - Phase 2（可选/付费）：用户触发后，对 **Phase 1 的 analysis_id** 进行 LLM 优化，并返回学习建议/错误模式总结。

2. **一致性与可追溯**
   - Phase 2 使用与 Phase 1 同一条 Analysis 记录（同一个 analysis_id），并能避免重复优化（幂等/状态机）。
   - 能对 LLM 调用做配额/限流与成本记录（复用现有 RateLimitService 的体系）。

3. **学习建议**
   - LLM 输出包含可直接渲染的 learning_analysis（错误模式、学习建议、tips，可选历史趋势）。
   - LLM 异常时降级：仍返回 Phase 1 结果，并明确 learning_analysis 缺失或为空。

### Hard Decisions（为确保端到端可用必须明确）

1. **匿名用户策略（必须二选一）**
   - 方案 A（推荐，简单且安全）：Phase 2 **仅允许登录用户**（anonymous 只能 Phase 1）。
   - 方案 B：匿名也可 Phase 2，需要引入 `requester_id`（如 cookie/session id）并将其写入 Analysis，用于所有权校验与限流键。

2. **学习建议落库方式（建议分阶段）**
   - v1（推荐）：learning_analysis 作为 JSON 存入 `ea_analyses.statistics`（或新增 `learning_insights` JSONB 字段）。
   - v2：如需要做统计看板/长期趋势，再拆分独立表（避免一开始就做复杂 schema）。

### API Contract（建议保持与现有风格一致）

为避免与现有页面/接口约定产生冲突，需要明确区分两类接口：

1. **Legacy `/analyze`（旧页面/旧流程）**
   - 保持现状：直接返回 `AnalyzeResponse`（无 `success/data` 包装）。

2. **Split Analysis（新页面/新流程：`/analyze/rules-only` 与 `/analyze/optimize-llm`）**
   - 与前端现有 split 类型保持一致：HTTP 层仍采用 `{ success, data }` 包装
   - 同时在后端用 Pydantic 把 `data` 定义成强类型（避免 `Dict[str, Any]` 漫游导致 drift）
   - 具体做法：定义 `ApiResponse[T]`（Pydantic Generic）+ `RulesOnlyData/OptimizeLLMData` 两个强类型 data model

1. `POST /api/v1/analyze/rules-only`
   - Request: `text`, `mode`, 可选 `language`（用于 RuleEngine 初始化）
   - Response: `{ success: true, data: RulesOnlyData }`

2. `POST /api/v1/analyze/optimize-llm`
   - Request: `analysis_id`
   - Response: `{ success: true, data: OptimizeLLMData }`

### Data Model（最小改动但满足目标）

1. `ea_analyses`（Analysis）
   - 新增：`status`（`rule_only|llm_running|llm_completed|failed`）
   - 可选新增：`llm_cost_usd`（若不想只放 token_usage 里）
   - 建议：将 `estimated_llm_tokens`、`learning_analysis` 放进 `statistics`（JSONB）以减少字段爆炸
   - 若支持匿名 Phase 2：新增 `requester_id`（String，既可放 `anon:<id>` 也可放 `user:<uuid>`）

2. `ea_error_details`（ErrorDetail）
   - 扩展字段用于对齐 LanguageTool：`rule_id`, `category`, `message`, `context`
   - 原有字段继续作为主通道：`error_type/error_subtype/original_span/corrected_span/start_index/end_index/severity/...`

3. LLM 学习建议（Learning）
   - v1：不新增表，直接 JSON 落 `analysis.statistics["learning_analysis"]`

### Concrete Specs（字段定义 + 状态机 + 鉴权）

#### Decision Defaults（本计划默认采用）

1. **匿名策略：采用方案 A**
   - `POST /analyze/rules-only`：允许匿名（user_id=NULL）
   - `POST /analyze/optimize-llm`：仅允许登录用户（需要 current_user），匿名请求直接 401
   - 这能把“所有权校验 + 成本控制”做得最可靠，且避免引入 requester_id/cookie/session 的复杂度

2. **学习建议落库：采用 v1（JSON）**
   - 不新增 LearningRecommendation/UserErrorTrend 表
   - learning_analysis 存入 `ea_analyses.statistics["learning_analysis"]`

如果后续必须支持匿名 Phase 2，再追加方案 B（见本节末尾 “Anonymous Phase 2 (Optional)”）。

#### Analysis 字段定义（SQLAlchemy）

在 `backend/models/analysis.py` 的 `Analysis` 增加：

```python
status = Column(String(20), nullable=False, default="rule_only", index=True)
```

可选（仅当你想把成本从 token_usage 中拆出）：

```python
llm_cost_usd = Column(DECIMAL(10, 4), nullable=False, default=0)
```

建议以 JSON 的方式扩展统计（写入 `statistics` / `token_usage`），避免字段膨胀：

- `statistics["estimated_llm_tokens"]`: int
- `statistics["rule_only"]`: dict（例如 sentence_count、word_count、error_types）
- `statistics["learning_analysis"]`: dict（Phase 2 写入）
- `token_usage`: 保持现有结构，Phase 1 写 `{}` 或 `{total_tokens: 0, estimated_cost: 0.0}`；Phase 2 写入 LLMEngine 返回值

#### ErrorDetail 字段定义（SQLAlchemy）

在 `backend/models/analysis.py` 的 `ErrorDetail` 增加（均 nullable）：

```python
rule_id = Column(String(100), index=True)
category = Column(String(50), index=True)
message = Column(Text)
context = Column(Text)
```

映射规则（Phase 1 写入）：
- `rule_id` ← `GrammarError.metadata["rule_id"]`
- `category` ← `GrammarError.metadata["category"]`
- `message` ← `GrammarError.explanation`（LanguageTool 的 match.message）
- `context` ← `GrammarError.metadata["context"]`

#### Status Machine（幂等 + 并发保护）

建议状态枚举（字符串即可，不强制 Enum）：
- `rule_only`: Phase 1 已完成，等待可选 Phase 2
- `llm_running`: Phase 2 已开始（用于并发保护）
- `llm_completed`: Phase 2 已完成
- `failed`: Phase 2 失败（可允许重试或不允许，见下）

转移规则：
- Phase 1 完成：`None` → `rule_only`
- Phase 2 开始：`rule_only` → `llm_running`（先 commit，防止双击触发重复扣费）
- Phase 2 成功：`llm_running` → `llm_completed`
- Phase 2 失败：`llm_running` → `failed`（并写入 `statistics["llm_error"]` 或 `token_usage["error"]`）

重复调用处理（建议）：
- `llm_running`：返回 409（“正在优化中”）
- `llm_completed`：返回 409（“已优化，无需重复”）
- `failed`：允许重试则置回 `llm_running`；不允许则 409

#### Ownership & Auth（必须落到代码里）

默认方案 A（仅登录用户可 Phase 2）：
- `rules-only`：`current_user` 可选；Analysis.user_id 写入 user_id 或 NULL
- `optimize-llm`：必须 `current_user` 存在，否则 401
- `optimize-llm` 查到 Analysis 后必须满足：`analysis.user_id == current_user.id`，否则 403

#### Rate Limit（成本可控的最小实现）

复用现有 `RateLimitService`：
- Phase 1：可做轻量 daily quota（tokens_used=0，cost=0），重点防滥用
- Phase 2：以 `LLMResult.token_usage["total_tokens"]` 为 tokens_used，并 track_usage（estimated_cost 可按模型价格算或先置 0）

#### LLM 输出结构（Combined Prompt 一次性返回）

建议 LLM 在 `llm_engine._optimize_combined` 的 JSON 结构里新增：

```json
{
  "intent": { "...": "..." },
  "optimized_text": "...",
  "corrections": [{ "...": "..." }],
  "explanation": "...",
  "learning_analysis": {
    "error_patterns": [
      { "pattern_name": "...", "frequency": "43%", "examples": [{"original":"...","corrected":"..."}], "severity": "high" }
    ],
    "ea_learning_recommendations": [
      { "priority": 1, "topic": "...", "description": "...", "resources": [{"type":"grammar_rule","title":"...","content":"..."}], "estimated_study_time": "30 minutes" }
    ],
    "personalized_tips": ["..."]
  }
}
```

服务层写入：
- `analysis.corrected_text = optimized_text`（或按合并策略写）
- `analysis.token_usage = llm_result.token_usage`
- `analysis.statistics["learning_analysis"] = learning_analysis`

#### Anonymous Phase 2 (Optional, 方案 B)

只有当“匿名也必须 Phase 2”时才做：
- Analysis 增加 `requester_id = Column(String(100), nullable=False, index=True)`
- Phase 1 匿名请求：`requester_id = "anon:" + <stable_id>`（cookie 或签名 token）
- Phase 2：要求请求携带同一个 stable_id，校验 `analysis.requester_id` 相等，否则 403
- RateLimitService 的 user_id 改为 requester_id（避免只用 IP）

---

## Task List (v2, Replace Task 1-12)

### Task 1: Define Schemas & Contracts

**Goal:** 把 Phase 1/2 的输入输出定成“可测试/可演进”的强类型协议。

**Files:**
- Modify: `backend/schemas/analysis.py`（或新建 `backend/schemas/split_analysis.py`，二选一）

**Steps:**
1. 明确“新旧接口返回格式不同”（避免和旧页面冲突）：
   - 旧 `/analyze`：继续返回 `AnalyzeResponse`（无 envelope）
   - 新 split endpoints：返回 `ApiResponse[T]` envelope（与前端 split 类型保持一致）
2. 在 schema 中新增 `ApiResponse[T]`（Pydantic GenericModel）：
   - `success: bool`
   - `data: T`
   - 可选 `message: str | None`
3. 在 schema 中新增以下 Pydantic models（作为 `data` 的强类型；字段命名沿用后端 snake_case）：
   - `RulesOnlyRequest`
     - `text: str`（min_length=1, max_length=10000）
     - `mode: str`（默认 "accuracy"，与现有 `Analysis.validate_mode` 对齐）
     - `language: str | None`（默认 "en-US"，用于 RuleEngine 初始化；不传则使用默认）
   - `RulesOnlyData`
     - `analysis_id: str`
     - `original_text: str`
     - `corrected_text: str`
     - `mode: str`
     - `status: str`（"rule_only"）
     - `errors: list[ErrorDetailResponse]`（复用现有 ErrorDetailResponse）
     - `statistics: dict[str, Any]`（至少包含 `total_errors`, `error_types`, `estimated_llm_tokens`）
     - `processing_time_ms: int`
     - `stage_times: dict[str, int]`
     - `created_at: datetime`
   - `OptimizeLLMRequest`
     - `analysis_id: str`（UUID string）
   - `OptimizeLLMData`
     - `analysis_id: str`
     - `original_text: str`
     - `corrected_text: str`（Phase 2 后最终文本；可直接取 LLM optimized_text）
     - `mode: str`
     - `status: str`（"llm_completed"）
     - `token_usage: dict[str, Any]`（沿用 `AnalyzeResponse` 的 token_usage 结构）
     - `statistics: dict[str, Any]`（包含 `learning_analysis`）
     - `processing_time_ms: int`
     - `stage_times: dict[str, int]`
     - `created_at: datetime`
4. 新增 `LearningAnalysis` 的 schema（仅用于响应与 statistics 存储的结构约定）：
   - `error_patterns: list[...]`
   - `ea_learning_recommendations: list[...]`
   - `personalized_tips: list[str]`
   - 可选 `historical_trend`
5. 明确错误码与返回约定（写在 schema 附近或本节末）：
   - Phase 1：参数校验失败 422（FastAPI 自动）
   - Phase 2：未登录 401；不属于当前用户 403；analysis_id 不存在 404；状态不允许 409

**Acceptance:**
- split endpoints 的 HTTP 响应与前端现有 `{ success, data }` 定义一致，同时 `data` 具备强类型约束。
- 两个 split endpoint 的响应字段足以渲染 Rule 面板与 LLM 面板（errors + corrected_text + learning_analysis + token_usage）。

### Task 2: Extend DB Models + Migration

**Goal:** 支持状态机、LT 细节、（可选）学习建议持久化与匿名所有权。

**Files:**
- Modify: `backend/models/analysis.py`
- Create migration via Alembic

**Steps:**
1. 在 `Analysis` 增加字段：
   - `status: String(20)`（nullable=False，default="rule_only"，index=True）
   - 可选：`llm_cost_usd: DECIMAL(10, 4)`（nullable=False，default=0）
   - 若采用 Anonymous Phase 2（方案 B）：`requester_id: String(100)`（nullable=False，index=True）
2. 在 `ErrorDetail` 增加字段（nullable=True）：
   - `rule_id: String(100)`（index=True）
   - `category: String(50)`（index=True）
   - `message: Text`
   - `context: Text`
3. 生成并审阅 Alembic migration：
   - `ALTER TABLE ea_analyses ADD COLUMN status ...`
   - `ALTER TABLE ea_error_details ADD COLUMN rule_id/category/message/context ...`
   - 若引入 requester_id 或 llm_cost_usd：对应的 ALTER TABLE
4. 执行 upgrade/downgrade 验证 migration 可逆。

**Acceptance:**
- 新增列已在数据库中存在并能正常读写。
- 不破坏现有 `/analyze` 的落库逻辑（旧字段仍可用）。

### Task 3: Implement Phase 1 (Rules-Only) Service Method

**Goal:** 只跑 Preprocess + RuleEngine，落库并返回 UI 所需信息。

**Files:**
- Modify: `backend/services/analysis_service.py`
- (Optional) Modify: `backend/pipeline/pipeline.py`（补齐 rule-only result 的 TODO，以便统计结构稳定）

**Steps:**
1. 在 `AnalysisService` 新增方法 `analyze_rules_only(request, user, db)`（签名与现有 `analyze()` 类似）：
   - 取 `text/mode/language`
   - 记录 `stage_times`
2. Phase 1 执行流程（建议与现有 pipeline 对齐）：
   - Stage preprocessing：`Preprocessor().preprocess(text)`（可选；仅用于 stage_times/metadata）
   - Stage rule_engine：`RuleEngine(language=language).check(text)`
   - 生成 `corrected_text`：复用 `AnalysisPipeline._apply_rule_corrections(text, errors)`
3. 估算 tokens（写入 `statistics["estimated_llm_tokens"]`）：
   - 使用 LLMEngine 当前的 token 估算思路或简单规则（与 v2 Concrete Specs 一致即可）
4. 落库（同步 SQLAlchemy Session）：
   - 创建 `Analysis`：
     - `user_id = user.id if user else None`
     - `original_text = text`
     - `corrected_text = corrected_text`
     - `mode = request.mode`
     - `statistics` 至少包含：`total_errors`, `error_types`, `estimated_llm_tokens`
     - `token_usage = {}` 或 `{"total_tokens": 0, "estimated_cost": 0.0}`
     - `processing_time_ms`
     - `status = "rule_only"`
   - 循环写入 `ErrorDetail`：
     - 核心字段来自 `GrammarError.to_dict()` 与 `GrammarError.metadata`
     - `message` 建议取 `GrammarError.explanation`
5. 返回 `RulesOnlyResponse`（schema 由 Task 1 定义）：
   - `analysis_id=str(analysis.id)`，errors 使用现有 `ErrorDetailResponse`

**Acceptance:**
- rules-only 请求能在 2–4 秒内返回并落库（含 errors 与 status）。
- `ErrorDetail.rule_id/category/context/message` 能从 LanguageTool 信息正确填充（来源是 `GrammarError.metadata`）。

### Task 4: Implement Phase 2 (Optimize) Service Method

**Goal:** 根据 analysis_id 执行 LLM，并更新同一条 Analysis，写入 learning_analysis。

**Files:**
- Modify: `backend/services/analysis_service.py`
- Modify: `backend/pipeline/llm_engine.py`（让 LLM 返回 learning_analysis）
- Modify: `backend/pipeline/merger.py`（如需把 LLM corrections 更细粒度落地/展示）

**Steps:**
1. 在 `AnalysisService` 新增方法 `optimize_with_llm(request, user, db)`：
   - 输入：`analysis_id`（UUID string）
   - 默认方案 A：必须 `user` 存在（匿名直接拒绝）
2. 所有权与存在性校验：
   - 解析 UUID（非法 → 400）
   - 查询 Analysis（找不到 → 404）
   - 校验 `analysis.user_id == user.id`（不满足 → 403）
3. 状态机与幂等（并发保护）：
   - 若 `status == "llm_running"` → 409
   - 若 `status == "llm_completed"` → 409
   - 若 `status == "failed"`：
     - 允许重试：继续（并覆盖失败信息）
     - 不允许重试：409
   - 若 `status != "rule_only"` 且不属于上述 → 409
   - 将 `status` 置为 `"llm_running"` 并 `db.commit()`（防止双击重复扣费）
4. 调用 LLM（修改 `LLMEngine._optimize_combined` 输出结构；并明确输入是用户原始文本）：
   - **LLM 输入必须是 `analysis.original_text`（用户原始输入）**，不是 Phase 1 的 `corrected_text`
   - 可以把 Phase 1 的 rule_errors（或 error patterns）作为“辅助上下文”传入 prompt，但主文本仍是原始输入
   - prompt 要求输出 `learning_analysis`（见 v2 Concrete Specs 的 JSON 结构）
   - 解析 JSON 后把 `learning_analysis` 作为 dict 带回
   - 建议把 `learning_analysis` 放到 `LLMResult.metadata["learning_analysis"]`，或直接在 `LLMResult` dataclass 增加字段（二选一，保持最小侵入）
5. 更新 Analysis（同一条记录）：
   - `analysis.corrected_text = llm_result.optimized_text`
   - `analysis.token_usage = llm_result.token_usage`（保留 estimated_cost 可为 0，后续再接模型价格）
   - `analysis.statistics["learning_analysis"] = learning_analysis_dict`
   - `analysis.status = "llm_completed"`
   - 记录 Stage times（建议写入 `analysis.statistics["stage_times"]` 或直接返回给 API）
   - `db.commit()`
6. 异常处理与降级：
   - LLM 调用失败：`analysis.status = "failed"`，并写入 `analysis.statistics["llm_error"] = ...`，`db.commit()`，然后向 API 抛 500（或返回 200 + failed 状态，二选一；建议 500 并让前端提示“可重试”）

**Acceptance:**
- Phase 2 能基于 Phase 1 的 analysis_id 更新同一条 Analysis（状态变更、token_usage 写入、learning_analysis 写入）。
- 双击/并发请求不会触发两次扣费（llm_running 保护生效）。

### Task 5: API Endpoints + Rate Limit Integration

**Goal:** 把两阶段功能暴露为独立 endpoint，并保证成本可控。

**Files:**
- Modify: `backend/api/v1/analysis.py`
- (Optional) Modify: `backend/services/rate_limit_service.py`（若需要新增 quota type，例如 “optimize”）

**Steps:**
1. 新增 endpoint：`POST /analyze/rules-only`
   - `user: User | None = Depends(get_optional_user)`（允许匿名）
   - `db: Session = Depends(get_db)`
   - 调用 `AnalysisService.analyze_rules_only(...)`
   - 返回 `RulesOnlyResponse`
2. 新增 endpoint：`POST /analyze/optimize-llm`
   - `user: User = Depends(get_current_user)`（强制登录）
   - `db: Session = Depends(get_db)`
   - 调用 `AnalysisService.optimize_with_llm(...)`
   - 返回 `OptimizeLLMResponse`
3. 限流与记账（复用现有 `/analyze` 的逻辑）：
   - `RateLimitService.check_rate_limit(...)`
     - Phase 1：可以 tokens_used=0；主要用于匿名防滥用
     - Phase 2：在调用 LLM 前先做 quota check，完成后 `track_usage(user_id, tokens_used, estimated_cost, db)`
   - user_id 构造沿用 `/analyze`：登录用 `str(user.id)`，匿名用 `"anon:" + http_request.client.host`（或后续替换为 requester_id）
4. 状态码约定（API 层统一）：
   - 401/403/404/409/422/500（见 Task 1）

**Acceptance:**
- 前端可以分别调用两个 endpoint。
- Phase 2 的 LLM 成本会被正确记账与限制。

### Task 6: Tests (Unit + API + Integration)

**Goal:** 用测试锁定“阶段拆分/状态机/所有权/降级”这四类高风险点。

**Steps:**
1. Unit（service 层）：
   - rules-only：输入简单文本，断言返回包含 analysis_id、errors、status=rule_only，并验证 DB 中 Analysis/ErrorDetail 写入（含 rule_id/category/context/message 非空或可空的合理性）。
   - optimize：mock `LLMEngine.optimize` 返回固定 optimized_text + token_usage + learning_analysis，断言：
     - 状态机：rule_only → llm_running → llm_completed
     - 重复调用返回 409
     - learning_analysis 写入 statistics
2. API 测试（FastAPI TestClient）：
   - `/analyze/rules-only`：匿名 200；空文本 422
   - `/analyze/optimize-llm`：匿名 401；不属于当前用户 403；不存在 404；重复 409
3. Integration（可选真实 LLM，建议用 marker 控制）：
   - 完整链路：rules-only → optimize-llm
   - 验证 DB 最终状态为 llm_completed，token_usage.total_tokens > 0（真实 LLM）或 == mock 值（mock）

**Acceptance:**
- CI/本地能稳定跑过（mock LLM 为默认；真实 LLM 的测试可单独触发）。

### Task 7: Final Verification Checklist

**Goal:** 确保上线质量与回滚安全。

**Steps / Commands:**
1. 后端测试：
   - `cd backend && poetry run pytest`
2. 静态检查：
   - `cd backend && poetry run ruff check .`
   - `cd backend && poetry run mypy .`
3. 数据库迁移：
   - `cd backend && poetry run alembic upgrade head`
   - `cd backend && poetry run alembic downgrade -1`（验证可回滚）
4. 端到端人工验收（最少两条）：
   - rules-only：确认 UI 立即展示规则结果与按钮可用
   - optimize：确认按钮触发后展示 LLM 优化文本与学习建议

**Acceptance:**
- 所有检查通过且 migration 可回滚。

---

## Notion-Style UI/UX Spec (Split Analysis Page)

本节描述“新页面（Split Analysis）”的页面结构、组件契约与交互细则，目标是对齐 Notion 的简洁块（block）体验，同时不与旧页面 `/analyze` 的交互/返回格式混淆。

### Page Layout（3-column, Notion-like）

1. **Left Sidebar（可折叠）**
   - 最近分析（History）
   - 草稿（Drafts，本地）
   - 模板（Templates，可选）

2. **Center Page（编辑区）**
   - Page Title：`English Transfer Assistant`
   - InputBlock：唯一可编辑主块（用户输入）
   - Inline status row：Phase 1/2 运行中提示（不使用大弹窗打断）

3. **Right Panel（Insights，可折叠）**
   - RuleFindingsBlock（Phase 1）
   - OptimizeBlock（Phase 2 触发入口 + token 提示 + 状态）
   - LLMResultBlock（Phase 2 结果）
   - LearningBlock（学习建议）

### Component Mapping（复用现有组件）

目标是尽量复用现有组件结构，把 “Notion 风格”落在布局与交互而不是重写业务。

- `InputPanel.vue` → InputBlock（Center）
- `RuleEnginePanel.vue` → RuleFindingsBlock（Right）
- `LLMPanel.vue` → LLMResultBlock + LearningBlock（Right）
- `AIOptimizeButton.vue` → 合并进 OptimizeBlock（Right，块内按钮；不悬浮）

建议新增一个页面级容器组件（命名可自定，例如 SplitAnalysisPage），负责三栏布局与快捷键绑定；现有 panels 作为内容块。

### Store & Data Flow（Split Analysis 专用）

在 `analysisStore` 里“新 split 状态”已经存在（ruleResult/llmResult/isOptimizing/llmError），建议补齐并统一职责：

- `draftText: string`（输入框内容）
- `ruleResult: RuleBasedResult | null`（Phase 1 data）
- `llmResult: LLMResult | null`（Phase 2 data）
- `isAnalyzing: boolean`（Phase 1 running）
- `isOptimizing: boolean`（Phase 2 running）
- `error: string | null`（Phase 1 error）
- `llmError: string | null`（Phase 2 error）

数据流（Notion 风格强调“局部更新”）：
- Phase 1 只更新 RuleFindingsBlock 与 OptimizeBlock（可用性/预估 tokens）
- Phase 2 只更新 LLMResultBlock 与 LearningBlock（并更新页面状态徽标）

### API Response Contract（避免新旧页面混淆）

- 旧页面：`/analyze` 返回 `AnalyzeResponse`（无 envelope）
- 新页面（split endpoints）：`/analyze/rules-only` 与 `/analyze/optimize-llm` 返回 `{ success, data }`

前端调用约定：
- `response.data.success === true` 时取 `response.data.data` 作为块渲染数据
- `success === false` 或 http error：显示块内 error row（不弹窗阻断）

### Block Behaviors（每个块的交互细则）

#### InputBlock（InputPanel）

Props（示例，命名以现有组件为准）：
- `modelValue: string`
- `mode: CorrectionMode`
- `isAnalyzing: boolean`
- `canAnalyze: boolean`

Events：
- `@analyze-rules(text, mode)`：触发 Phase 1
- `@clear`
- `@update:modelValue`
- `@update:mode`

交互细节：
- `Cmd/Ctrl+Enter`：触发 Phase 1（仅当 canAnalyze）
- 粘贴超长：块内轻提示（toast 可选，但不强制）

#### RuleFindingsBlock（RuleEnginePanel）

Props：
- `ruleResult: RuleBasedResult | null`
- `isAnalyzing: boolean`
- `error: string | null`

Events（块内操作）：
- `@select-error(errorId)`：定位到输入文本相应区间并高亮
- `@apply-suggestion(errorId, replacementIndex?)`：可选（如实现“应用建议”）
- `@ignore-error(errorId)`：可选（前端局部忽略，不一定落库）

交互细节（Notion 味道核心）：
- 错误条目 hover 才显示操作柄：`Locate / Apply / Ignore / Copy`
- 错误条目 click：右侧聚焦 + 中间滚动定位
- 错误条目 Enter：应用默认替换（聚焦态）
- 右键菜单（ContextMenu）：
  - Apply suggestion (default)
  - Copy original span
  - Copy corrected span
  - Ignore / Unignore
  - Feedback: inaccurate (optional)

#### OptimizeBlock（AI Optimize）

Props：
- `analysisId: string | null`
- `estimatedTokens: number | null`
- `isOptimizing: boolean`
- `canOptimize: boolean`
- `llmError: string | null`

Events：
- `@optimize(analysisId)`：触发 Phase 2
- `@retry(analysisId)`

交互细节：
- 显示轻量 “Uses credits” 提示（小字）
- 点击后生成 `Optimizing…` 行内块（可取消可不做）
- Phase 2 失败：块内显示错误条 + Retry（不清空 Phase 1）

#### LLMResultBlock + LearningBlock（LLMPanel）

Props：
- `llmResult: LLMResult | null`
- `isOptimizing: boolean`

渲染结构建议：
- LLMResultBlock：optimized_text 摘要 + corrections 列表（可折叠）
- LearningBlock：Top 3 recommendations + tips（每条建议可展开例句/练习）

### Keyboard Shortcuts & Command Palette（最小集）

- `Cmd/Ctrl+Enter`：Analyze with Rules（Phase 1）
- `Cmd/Ctrl+K`：Command Palette（actions）
  - Analyze with Rules
  - Optimize with AI（当 canOptimize）
  - Export（可选）
  - Clear draft
- `Esc`：关闭命令面板/退出错误条目聚焦
- `↑/↓`：在错误条目间导航（右侧面板聚焦态）

### Error-to-Text定位与高亮（实现约束）

当前错误结构以 `start_index/end_index` 为定位依据（来自 LanguageTool 匹配）。为了保持 Notion 的“就地定位”体验：
- 点击错误条目：中间输入区滚动到大致位置，并在文本上做一次短暂高亮（1–2s）
- 若实现“应用替换”：建议以“重分析”为最终一致性手段（应用后自动触发 Phase 1），避免在前端做复杂字符串 diff 导致索引漂移

### Empty/Error/Loading Copy（块内提示，短句）

- Empty:
  - RuleFindingsBlock：`No results yet`
  - OptimizeBlock：`Run rules first`
- Loading:
  - Phase 1：`Analyzing…`
  - Phase 2：`Optimizing…`
- Error:
  - Phase 1：`Analysis failed. Retry`
  - Phase 2：`Optimization failed. Retry`

### Accessibility（最低要求）

- 所有可点击操作在 hover 外也可通过键盘触达（Tab/Enter）
- 右侧错误列表支持 aria-selected 与可见焦点样式
- 命令面板可 Esc 关闭，且不会造成焦点丢失

## Notes (Why v2 is more accurate)

- 以“端到端可跑通”为核心：明确匿名策略、所有权校验、状态机、限流与降级路径。
- 以“协议强类型”为核心：避免弱类型 `success/data` 造成前后端 drift。
- 以“先 JSON 后拆表”为核心：学习建议先能用，后续再做统计/趋势表结构。

## References

- `docs/plans/2026-02-05-function-split-design.md`
- `backend/pipeline/pipeline.py`
- `backend/pipeline/rule_engine.py`
- `backend/pipeline/llm_engine.py`
