# English Transfer Assistant - 实施待办清单

**基于技术实现方案的详细任务列表**

**创建日期**: 2026-01-19
**预计开始**: 待定
**预计完成**: 待定

---

## 📊 总体进度

- **Phase 1**: ✅ Requirements & Discovery (100%)
- **Phase 2**: ✅ Planning & Structure (100%)
  - ✅ 产品能力设计
  - ✅ UI 设计
  - ✅ 技术实现方案
- **Phase 3**: 🔄 Implementation (35%)
  - ✅ 项目框架搭建 (100%)
  - ✅ Pipeline框架实现 (80%)
  - 🔄 业务逻辑实现 (30%)
  - ⏳ 前后端集成 (10%)
- **Phase 4**: ⏳ Testing (0%)
- **Phase 5**: ⏳ Deployment (0%)

**最新更新**: 2026-01-27
**当前分支**: feature/mvp_v1
**最新提交**: 30aaca5 - feat(frontend): 实现前端组件重构和错误高亮功能

---

## 🎯 Phase 2.5: 技术设计完善

### API 设计
- [x] API 端点定义
- [x] 请求/响应格式
- [x] 错误码规范
- [ ] API 文档生成方案
- [ ] API 版本管理策略

### 前端架构设计
- [x] 组件树结构
- [x] 组件通信方案
- [x] Props 和 Events 定义
- [ ] 组件测试策略
- [ ] 组件性能优化方案

### 状态管理设计
- [x] Store 结构定义
- [x] State 接口定义
- [x] Actions 定义
- [ ] 持久化策略（localStorage）
- [ ] 状态回滚机制

### Pipeline 设计
- [ ] 阶段间数据格式定义
- [ ] 错误处理策略
- [ ] 超时处理机制
- [ ] 降级策略
- [ ] 缓存策略

---

## 🚀 Phase 3: Implementation

### 3.1 项目初始化 ✅ 已完成

#### 后端项目 ✅
- [x] 创建项目目录结构 (44个Python文件)
- [x] 初始化 Poetry 项目 (75个依赖包)
- [x] 配置依赖
  - [x] fastapi, uvicorn
  - [x] sqlalchemy, alembic
  - [x] pydantic v2
  - [x] python-jose, passlib
  - [x] language-tool-python
  - [x] zhipuai (SDK)
- [x] 配置 Pytest
  - [x] pytest.ini 配置
  - [x] conftest.py (fixtures)
- [x] 配置代码格式化
  - [x] black 配置 (line-length=100)
  - [x] ruff 配置
  - [ ] pre-commit hook

#### 前端项目 ✅
- [x] 创建 Vite + Vue 3 项目
- [x] 安装依赖
  - [x] vue 3.5.13
  - [x] vue-router 4.5.0
  - [x] pinia 2.2.8
  - [x] axios 1.7.9
  - [x] tailwindcss 3.4.17
- [x] 配置 TypeScript (strict mode)
- [x] 配置 Tailwind CSS
- [x] 配置 ESLint + Prettier
- [x] 创建目录结构

#### 开发环境 ✅
- [x] Docker Compose 配置
  - [x] PostgreSQL 16 服务
  - [x] ~~Redis 服务~~ (V1改为内存缓存)
  - [ ] 后端服务 (dockerfile待创建)
  - [ ] 前端服务 (dockerfile待创建)
- [x] 环境变量配置 (.env.example已创建)
- [x] Git 配置 (.gitignore已配置)
- [x] 开发脚本 (dev.sh, verify.sh, test.sh)

---

### 3.2 后端实现 🔄 进行中 (50%)

#### 基础框架 ✅
- [x] FastAPI 应用初始化 (main.py)
- [x] CORS 中间件配置
- [ ] 全局异常处理器 (已定义但未集成)
- [ ] 请求日志中间件 (未实现)
- [x] 健康检查端点 `GET /health`

#### 数据库层 ✅ 模型完成，迁移待配置
- [x] SQLAlchemy 配置 (models/session.py)
- [x] Session 管理 (get_db依赖)
- [x] 模型定义 (9个模型类)
  - [x] User, UserSettings, APICredit
  - [x] Analysis, ErrorDetail
  - [x] Tag, AnalysisTag, AnalysisCache
  - [x] TimestampMixin, SoftDeleteMixin
- [ ] Alembic 配置 ❌ **待完成**
  - [ ] alembic.ini 初始化
  - [ ] env.py 配置
  - [ ] 初始迁移脚本
- [ ] 数据库索引
  - [ ] 在迁移脚本中定义索引
  - [ ] 外键索引
  - [ ] 复合索引

#### 认证模块 ⏳ 骨架完成，业务逻辑待实现
- [x] JWT 工具类 (core/security.py - 部分实现)
- [x] 密码哈希工具 (services/password_service.py)
- [ ] 认证依赖 (core/security.py - 未完整实现)
- [ ] 认证 API 端点 (api/v1/auth.py - TODO标记21个)
  - [ ] POST /api/v1/auth/register
  - [ ] POST /api/v1/auth/login
  - [ ] POST /api/v1/auth/refresh
  - [ ] GET /api/v1/auth/me

#### Pipeline 核心 ✅ 框架完成，集成待测试 (80%)
- [x] Pipeline 基础框架 (pipeline/pipeline.py)
  - [x] AnalysisPipeline.analyze()
  - [x] PipelineResult 数据类
  - [x] 各阶段计时功能
- [x] 阶段 1：预处理 ✅
  - [x] Preprocessor.preprocess() (pipeline/preprocessor.py)
  - [x] 句子分割 (SentenceSplitter)
  - [x] 说话人识别 (SpeakerDetector)
  - [x] 中文检测 (ChineseDetector)
- [x] 阶段 2：规则纠错 ✅
  - [x] RuleEngine.check() (pipeline/rule_engine.py)
  - [x] LanguageTool 集成
  - [x] 错误分类 (ErrorClassifier)
  - [x] 严重程度评估 (SeverityEvaluator)
- [x] 阶段 3：LLM 优化 ✅
  - [x] LLMEngine.optimize() (pipeline/llm_engine.py)
  - [x] 智谱 AI 服务封装
  - [x] 意图识别
  - [x] 自然度优化
  - [x] 中英混用纠正
  - [x] 错误处理和重试机制
- [x] 阶段 4：后处理 ✅
  - [x] Merger.merge() (pipeline/merger.py)
  - [x] 结果合并逻辑
  - [x] 冲突解决策略
- [ ] Pipeline 集成测试 ⏳ **待完成**

#### API 端点 ⏳ 骨架完成，业务逻辑待实现 (30%)
- [ ] POST /api/v1/analyze (api/v1/analysis.py - TODO)
  - [x] 路由定义和Pydantic schema
  - [ ] 请求验证
  - [ ] 限流检查 (已有RateLimitService)
  - [ ] 调用 Pipeline (pipeline已实现)
  - [ ] 保存到数据库
  - [ ] 返回结果
- [ ] GET /api/v1/history (api/v1/history.py - TODO)
- [ ] GET /api/v1/history/{id} (api/v1/history.py - TODO)
- [ ] DELETE /api/v1/history/{id} (api/v1/history.py - TODO)
- [ ] GET /api/v1/statistics/overview (api/v1/statistics.py - TODO)
- [ ] GET /api/v1/statistics/tokens (api/v1/statistics.py - TODO)
- [ ] POST /api/v1/export (api/v1/export.py - TODO)
- [ ] GET /api/v1/settings (api/v1/settings.py - TODO)
- [ ] PUT /api/v1/settings (api/v1/settings.py - TODO)

**重要**: 所有API路由已创建但未集成到main.py（被注释掉）

#### 外部服务集成 ✅ 服务已实现，待集成测试
- [x] ~~Redis 客户端~~ (V1改为内存缓存)
  - [x] CacheService (services/cache_service.py - 内存实现)
  - [x] 24小时TTL配置
  - [x] LRU淘汰策略
- [x] 限流服务 ✅
  - [x] RateLimitService (services/rate_limit_service.py)
  - [x] 内存计数实现
  - [x] 分层限额（匿名/免费/付费）
  - [ ] 中间件集成 (未实现)
- [x] 智谱 AI 错误处理 ✅
  - [x] 重试机制 (llm_engine.py)
  - [x] 降级策略 (失败时返回LanguageTool结果)
- [x] LanguageTool 错误处理 ✅
  - [x] 连接池管理 (rule_engine.py)
  - [x] 超时处理 (30秒)

---

### 3.3 前端实现 🔄 进行中 (70%)

#### 基础框架 ✅
- [x] Vue Router 配置 (router/index.ts)
  - [x] 5个路由定义（/, /auth, /history, /statistics, /settings）
  - [x] 路由守卫（认证检查）
  - [x] 自动重定向逻辑
- [x] 全局样式 ✅
  - [x] Tailwind 基础配置
  - [x] 自定义颜色主题
  - [x] Glassmorphism 效果
- [x] Axios 配置 (api/index.ts)
  - [x] baseURL 配置
  - [x] 请求拦截器（token注入）
  - [x] 响应拦截器（token刷新）

#### Pinia Stores ✅ 结构完成，部分逻辑待完善
- [x] analysisStore.ts ✅
  - [x] state定义
  - [x] analyzeText() 基础逻辑
  - [ ] 错误处理完善
- [x] authStore.ts ✅
  - [x] 认证状态管理
  - [ ] Token刷新逻辑
- [x] historyStore.ts ✅
  - [x] 历史记录state
  - [ ] 分页逻辑待实现
- [x] uiStore.ts ✅
  - [x] collapsedPanels
  - [x] layoutMode
  - [x] toast通知

#### 核心组件 ✅ 大部分完成 (80%)

**布局组件** ✅
- [x] Navbar.vue
- [x] MainLayout.vue
- [x] LayoutControls.vue (4种布局切换)
- [x] Footer.vue

**输入面板** ✅
- [x] InputPanel.vue
- [x] 模式切换功能
- [x] 字符计数
- [x] 输入验证 (最大5000字符)
- [x] 进度指示器
- [ ] 文件导入功能

**比较面板** ✅ (最新完成 - commit 30aaca5)
- [x] ComparePanel.vue (三视图模式)
- [x] 视图切换（并排/原文/纠正后）
- [x] 错误统计卡片
- [x] 错误高亮显示
- [x] 错误位置定位
- [x] 复制功能

**分析面板** ✅
- [x] AnalysisPanel.vue
- [x] ErrorCard.vue (展开/折叠)
- [x] ErrorHighlight.vue (可视化高亮)
- [x] 错误详情展示
- [ ] 搜索和筛选功能

**通用组件** ✅
- [x] Toast.vue (全局提示)
- [x] LoadingSpinner.vue
- [x] ErrorDisplay.vue
- [x] LoginForm.vue
- [x] RegisterForm.vue

**组件完成度**: 14个核心组件已实现，部分功能待完善

#### API 客户端 ✅
- [x] API 基础配置 (api/index.ts)
  - [x] axios实例配置
  - [x] 6个模块 (auth, analysis, history, statistics, export, settings)
- [x] 认证拦截器
- [x] 错误处理拦截器
- [x] 类型定义
  - [x] AnalysisResult, Error等核心类型
  - [x] stores/types.ts 统一管理

#### 交互逻辑 ✅ 基础完成，优化进行中 (70%)
- [x] 错误卡片点击联动 ✅
  - [x] 点击卡片 → 高亮文中错误
  - [x] 滚动到错误位置
- [x] 区域折叠 ✅
  - [x] 折叠动画
  - [x] 状态记忆
- [x] 布局切换 ✅
  - [x] 4种布局模式
  - [x] 响应式适配
- [x] 视图切换 ✅
  - [x] 并排/原文/纠正后
  - [x] 过渡动画
- [x] 加载状态 ✅
  - [x] 分析中动画
  - [x] 进度提示
- [x] 错误提示 ✅
  - [x] Toast通知组件
  - [x] API错误显示
  - [x] 表单验证提示

---

### 3.4 测试 (预计 5-7 天)

#### 后端测试
- [ ] Pipeline 单元测试
  - [ ] test_sentence_splitter.py
  - [ ] test_speaker_detector.py
  - [ ] test_chinese_detector.py
  - [ ] test_language_tool_service.py
  - [ ] test_zhipu_service.py (mock)
  - [ ] test_result_merger.py
- [ ] API 集成测试
  - [ ] test_auth_endpoints.py
  - [ ] test_analyze_endpoint.py
  - [ ] test_history_endpoints.py
  - [ ] test_statistics_endpoint.py
- [ ] 限流测试
  - [ ] test_rate_limiting.py
- [ ] 认证测试
  - [ ] test_jwt_manager.py
  - [ ] test_password_manager.py

#### 前端测试
- [ ] 组件单元测试
  ```typescript
  describe('InputPanel', () => {
    it('renders correctly', () => { ... })
    it('handles analyze button', () => { ... })
  })
  ```
- [ ] Store 测试
  ```typescript
  describe('analysisStore', () => {
    it('analyzes text', () => { ... })
  })
  ```
- [ ] API 客户端测试
  ```typescript
  describe('analysisApi', () => {
    it('sends correct request', () => { ... })
  })
  ```
- [ ] E2E 测试
  ```typescript
  test('user can analyze text', async ({ page }) => {
    await page.goto('/')
    await page.fill('textarea', 'I go to park.')
    await page.click('button:has-text("分析文本")')
    await expect(page.locator('.error-card')).toBeVisible()
  })
  ```

#### 性能测试
- [ ] API 并发测试
  - [ ] 10 并发请求
  - [ ] 100 并发请求
- [ ] Pipeline 处理时间
  - [ ] 短文本（< 100 词）
  - [ ] 中文本（100-500 词）
  - [ ] 长文本（500-1000 词）
- [ ] 前端渲染性能
  - [ ] 错误卡片数量测试
  - [ ] 长文本渲染

---

### 3.5 部署准备 (预计 2-3 天)

#### Docker 配置
- [ ] 后端 Dockerfile
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY pyproject.toml poetry.lock ./
  RUN poetry install
  COPY . .
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
  ```
- [ ] 前端 Dockerfile
  ```dockerfile
  FROM node:20-alpine
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  RUN npm run build
  FROM nginx:alpine
  COPY --from=0 /app/dist /usr/share/nginx/html
  ```
- [ ] Nginx 配置
  ```nginx
  server {
    listen 80;
    location /api {
      proxy_pass http://backend:8000;
    }
    location / {
      root /usr/share/nginx/html;
    }
  }
  ```
- [ ] docker-compose.yml
  ```yaml
  services:
    postgres:
      image: postgres:16
    redis:
      image: redis:7
    backend:
      build: ./backend
    frontend:
      build: ./frontend
    nginx:
      image: nginx:alpine
  ```

#### 部署脚本
- [ ] build.sh
- [ ] deploy.sh
- [ ] 环境变量检查脚本

#### 监控配置
- [ ] 日志配置
  - [ ] 后端日志格式
  - [ ] 前端错误日志
- [ ] 健康检查
- [ ] 性能监控

---

## 📝 文档任务

- [x] API 文档
  - [x] Swagger/OpenAPI 配置 (FastAPI自动生成)
  - [ ] 接口示例（待补充）
  - [ ] 错误码说明
- [x] 部署文档
  - [x] 环境要求 (README.md)
  - [x] 部署步骤 (docs/FRAMEWORK_SETUP.md)
  - [ ] 故障排查 (scripts/README.md部分覆盖)
- [x] 开发文档 ✅
  - [x] CLAUDE.md (AI开发指南)
  - [x] AGENTS.md (开发规范)
  - [x] scripts/README.md (脚本文档)
- [ ] 用户文档
  - [ ] 功能说明
  - [ ] 使用教程
  - [ ] FAQ

---

## 🎯 里程碑

### ✅ Milestone 1: 项目初始化完成 (已完成)
**完成日期**: 2026-01-22
**标志**:
- [x] 后端项目可运行 (Poetry + FastAPI)
- [x] 前端项目可运行 (Vite + Vue 3)
- [x] Docker Compose 可启动PostgreSQL

### 🔄 Milestone 2: 核心 Pipeline 可用 (80%)
**当前状态**: Pipeline框架完成，集成测试进行中
**标志**:
- [x] 4阶段Pipeline实现完成
- [x] LanguageTool集成
- [x] 智谱AI集成
- [ ] 端到端测试
- [ ] 前端完整显示分析结果

### ⏳ Milestone 3: MVP 功能完整 (50%)
**预计完成**: 2026-02-15
**标志**:
- [ ] 所有核心 API 可用 (30% - 骨架完成)
- [x] 所有核心组件实现 (80% - 主要功能完成)
- [ ] 前后端完整集成
- [ ] 基本的错误处理完成

### ⏳ Milestone 4: 测试通过 (0%)
**预计完成**: 2026-02-22
**标志**:
- [ ] 单元测试覆盖率 > 70%
- [ ] 集成测试通过
- [ ] E2E 测试通过

### ⏳ Milestone 5: 部署就绪 (0%)
**预计完成**: 2026-02-28
**标志**:
- [ ] Docker 镜像构建成功
- [ ] 可在本地通过 Docker Compose 启动完整系统
- [ ] 文档齐全

---

## 🔖 标签说明

- **P0**: MVP 必需，阻塞发布
- **P1**: 重要，影响用户体验
- **P2**: 增强功能，可延后
- **Backend**: 后端任务
- **Frontend**: 前端任务
- **DevOps**: 部署/运维任务
- **Docs**: 文档任务

---

## 📊 工作量估算（更新）

| 阶段 | 状态 | 实际工时 | 预计工时 | 完成度 |
|------|------|---------|---------|--------|
| Phase 2.5 | ✅ 完成 | ~16小时 | 2-3 天 | 100% |
| 3.1 项目初始化 | ✅ 完成 | ~24小时 | 2-3 天 | 100% |
| 3.2 后端实现 | 🔄 进行中 | ~60小时 | 40-50 小时 | 50% |
| 3.3 前端实现 | 🔄 进行中 | ~50小时 | 40-50 小时 | 70% |
| 3.4 测试 | ⏳ 待开始 | 0小时 | 20-30 小时 | 0% |
| 3.5 部署准备 | ⏳ 待开始 | 0小时 | 10-15 小时 | 0% |
| **总计** | - | **~150小时** | **114-171 小时** | **35%** |

**预计剩余工作量**: 约60-80小时（1.5-2周）

---

## 🔥 当前优先级任务（Top 5）

### P0 - 阻塞MVP发布
1. **配置Alembic数据库迁移** (后端)
   - 初始化alembic
   - 创建初始迁移脚本
   - 测试数据库升级/降级

2. **实现API端点业务逻辑** (后端)
   - 完成api/v1/analysis.py (21个TODO)
   - 完成api/v1/auth.py (认证逻辑)
   - 将路由集成到main.py

3. **前后端集成测试** (全栈)
   - 测试完整的分析流程
   - 测试认证流程
   - 修复集成问题

### P1 - 重要功能
4. **完善错误处理** (全栈)
   - 统一错误码
   - 前端错误提示优化
   - 后端异常处理完善

5. **编写核心功能测试** (测试)
   - Pipeline单元测试
   - API集成测试
   - 前端组件测试

---

**最后更新**: 2026-01-27
**更新人**: AI Assistant
**当前分支**: feature/mvp_v1
**最新提交**: 30aaca5
