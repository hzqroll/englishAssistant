# English Transfer Assistant - 实施待办清单

**基于技术实现方案的详细任务列表**

**创建日期**: 2026-01-19
**预计开始**: 待定
**预计完成**: 待定

---

## 📊 总体进度

- **Phase 1**: ✅ Requirements & Discovery (100%)
- **Phase 2**: 🔄 Planning & Structure (90%)
  - ✅ 产品能力设计
  - ✅ UI 设计
  - ⏳ 技术实现方案（进行中）
- **Phase 3**: ⏳ Implementation (0%)
- **Phase 4**: ⏳ Testing (0%)
- **Phase 5**: ⏳ Deployment (0%)

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

### 3.1 项目初始化 (预计 2-3 天)

#### 后端项目
- [ ] 创建项目目录结构
  ```
  backend/
  ├── api/
  ├── core/
  ├── models/
  ├── pipeline/
  ├── services/
  ├── tests/
  └── main.py
  ```
- [ ] 初始化 Poetry 项目
  ```bash
  poetry init
  poetry install
  ```
- [ ] 配置依赖
  - fastapi
  - uvicorn
  - sqlalchemy
  - alembic
  - pydantic
  - python-jose[cryptography]
  - passlib[bcrypt]
  - redis
  - language-tool-python
  - zhipuai
- [ ] 配置 Pytest
  - [ ] pytest.ini 配置
  - [ ] conftest.py（fixtures）
- [ ] 配置代码格式化
  - [ ] .black 配置
  - [ ] .ruff 配置
  - [ ] pre-commit hook

#### 前端项目
- [ ] 创建 Vite + Vue 3 项目
  ```bash
  npm create vite@latest frontend -- --template vue-ts
  ```
- [ ] 安装依赖
  - [ ] vue
  - [ ] vue-router
  - [ ] pinia
  - [ ] axios
  - [ ] tailwindcss
  - [ ] @headlessui/vue
- [ ] 配置 TypeScript
  - [ ] tsconfig.json
  - [ ] 类型定义文件
- [ ] 配置 Tailwind CSS
  - [ ] tailwind.config.js
  - [ ] postcss.config.js
- [ ] 配置 ESLint + Prettier
- [ ] 创建目录结构
  ```
  frontend/src/
  ├── api/
  ├── components/
  ├── stores/
  ├── router/
  ├── types/
  ├── utils/
  └── styles/
  ```

#### 开发环境
- [ ] Docker Compose 配置
  - [ ] PostgreSQL 服务
  - [ ] Redis 服务
  - [ ] 后端服务
  - [ ] 前端服务
- [ ] 环境变量配置
  - [ ] .env.example
  - [ ] .env.local（gitignore）
- [ ] Git 配置
  - [ ] .gitignore
  - [ ] pre-commit hooks

---

### 3.2 后端实现 (预计 10-14 天)

#### 基础框架 (1 天)
- [ ] FastAPI 应用初始化
  ```python
  # backend/main.py
  app = FastAPI(title="English Transfer Assistant")
  ```
- [ ] CORS 中间件配置
- [ ] 全局异常处理器
- [ ] 请求日志中间件
- [ ] 健康检查端点 `GET /health`

#### 数据库层 (2 天)
- [ ] SQLAlchemy 配置
  - [ ] Database 类
  - [ ] Session 管理
- [ ] 模型定义
  - [ ] User 模型
    ```python
    class User(Base):
        id: UUID
        email: str
        password_hash: str
        tier: str  # anonymous/free/paid
        settings: JSON
        created_at: datetime
    ```
  - [ ] Analysis 模型
    ```python
    class Analysis(Base):
        id: UUID
        user_id: UUID
        original_text: str
        corrected_text: str
        text_type: str
        tone: str
        mode: str
        error_count: int
        created_at: datetime
    ```
  - [ ] ErrorDetail 模型
    ```python
    class ErrorDetail(Base):
        id: UUID
        analysis_id: UUID
        type: str
        subtype: str
        original: str
        correction: str
        position: JSON
        explanation: str
        rule: str
    ```
  - [ ] RequestLog 模型
- [ ] Alembic 配置
  - [ ] alembic.ini
  - [ ] env.py
  - [ ] 初始迁移脚本
- [ ] 数据库索引
  - [ ] user_id 外键索引
  - [ ] analysis_id 外键索引
  - [ ] user_id + created_at 复合索引
  - [ ] email 唯一索引

#### 认证模块 (2 天)
- [ ] JWT 工具类
  ```python
  class JWTManager:
      def create_access_token(user_id: str) -> str
      def create_refresh_token(user_id: str) -> str
      def verify_token(token: str) -> TokenPayload
  ```
- [ ] 密码哈希工具
  ```python
  class PasswordManager:
      def hash_password(password: str) -> str
      def verify_password(password: str, hash: str) -> bool
  ```
- [ ] 认证依赖
  ```python
  def get_current_user(token: str) -> User
  def get_optional_user(token: str = None) -> User | None
  ```
- [ ] 认证 API 端点
  - [ ] POST /api/v1/auth/register
  - [ ] POST /api/v1/auth/login
  - [ ] POST /api/v1/auth/refresh

#### Pipeline 核心 (4-5 天)
- [ ] Pipeline 基础框架
  ```python
  class Pipeline:
      async def process(text: str, mode: str) -> AnalysisResult
  ```
- [ ] 阶段 1：预处理
  - [ ] 句子分割器
    ```python
    class SentenceSplitter:
        def split(text: str) -> List[Sentence]
    ```
  - [ ] 说话人识别器
    ```python
    class SpeakerDetector:
        def detect(text: str) -> List[Speaker]
    ```
  - [ ] 中文检测器
    ```python
    class ChineseDetector:
        def detect(text: str) -> List[ChineseSegment]
    ```
- [ ] 阶段 2：规则纠错
  - [ ] LanguageTool 服务封装
    ```python
    class LanguageToolService:
        async def check(text: str) -> List[GrammarError]
    ```
  - [ ] 错误分类器
    ```python
    class ErrorClassifier:
        def classify(error: GrammarError) -> ErrorType
    ```
  - [ ] 严重程度评估
    ```python
    class SeverityEvaluator:
        def evaluate(error: GrammarError) -> Severity
    ```
- [ ] 阶段 3：LLM 优化
  - [ ] 智谱 AI 服务封装
    ```python
    class ZhipuService:
        async def detect_intent(text: str) -> IntentResult
        async def optimize_naturalness(text: str, intent: IntentResult) -> str
        async def suggest_english(chinese: str, context: str) -> str
    ```
  - [ ] 意图识别
  - [ ] 自然度优化（仅在 natural 模式）
  - [ ] 中英混用纠正
- [ ] 阶段 4：后处理
  - [ ] 结果合并器
    ```python
    class ResultMerger:
        def merge(
            rule_errors: List[GrammarError],
            llm_result: str,
            intent: IntentResult
        ) -> AnalysisResult
    ```
  - [ ] 错误报告生成器
    ```python
    class ErrorReportGenerator:
        def generate(errors: List[Error]) -> ErrorReport
    ```
  - [ ] 学习建议生成器
    ```python
    class LearningTipGenerator:
        def generate(statistics: ErrorStatistics) -> List[str]
    ```

#### API 端点 (3-4 天)
- [ ] POST /api/v1/analyze
  - [ ] 请求验证（Pydantic）
  - [ ] 限流检查
  - [ ] 调用 Pipeline
  - [ ] 保存到数据库
  - [ ] 返回结果
- [ ] GET /api/v1/history
  - [ ] 分页参数验证
  - [ ] 查询用户记录
  - [ ] 序列化返回
- [ ] GET /api/v1/history/{id}
  - [ ] 权限验证
  - [ ] 查询详情
  - [ ] 返回完整结果
- [ ] DELETE /api/v1/history/{id}
  - [ ] 权限验证
  - [ ] 删除记录
- [ ] GET /api/v1/statistics/overview
  - [ ] 聚合查询
  - [ ] 计算统计
  - [ ] 返回结果
- [ ] POST /api/v1/export
  - [ ] 格式验证
  - [ ] 生成文件
  - [ ] 返回文件流
- [ ] GET /api/v1/settings
  - [ ] 查询用户设置
- [ ] PUT /api/v1/settings
  - [ ] 更新设置

#### 外部服务集成 (2 天)
- [ ] Redis 客户端
  ```python
  class RedisClient:
      async def check_rate_limit(user_id: str) -> bool
      async def increment_count(user_id: str) -> int
  ```
- [ ] 限流中间件
  ```python
  class RateLimitMiddleware:
      async def check_request(request: Request)
  ```
- [ ] 智谱 AI 错误处理
  - [ ] 重试机制
  - [ ] 降级策略
- [ ] LanguageTool 错误处理
  - [ ] 连接池管理
  - [ ] 超时处理

---

### 3.3 前端实现 (预计 10-14 天)

#### 基础框架 (1 天)
- [ ] Vue Router 配置
  ```typescript
  const routes = [
    { path: '/', component: HomeView },
    { path: '/history', component: HistoryView },
    { path: '/statistics', component: StatisticsView }
  ]
  ```
- [ ] 全局样式
  - [ ] Tailwind 基础配置
  - [ ] 自定义颜色
  - [ ] Glassmorphism 效果
- [ ] Axios 配置
  ```typescript
  axios.defaults.baseURL = '/api/v1'
  axios.interceptors.request.use(authInterceptor)
  axios.interceptors.response.use(errorInterceptor)
  ```

#### Pinia Stores (2 天)
- [ ] analysisStore.ts
  ```typescript
  export const useAnalysisStore = defineStore('analysis', {
    state: (): AnalysisState => ({ ... }),
    actions: {
      async analyzeText(text, mode) { ... },
      setView(view) { ... },
      ...
    }
  })
  ```
- [ ] historyStore.ts
- [ ] userStore.ts
- [ ] uiStore.ts
  - [ ] collapsedPanels
  - [ ] layoutMode
  - [ ] theme

#### 核心组件 (5-6 天)

**Navbar 组件**
- [ ] Navbar.vue
- [ ] Logo.vue
- [ ] NavLinks.vue
- [ ] UserMenu.vue

**InputPanel 组件**
- [ ] InputPanel.vue
- [ ] ModeSwitch.vue
  - [ ] 切换动画
  - [ ] 模式描述
- [ ] TextInput.vue
  - [ ] 字符计数
  - [ ] 输入验证
- [ ] CharCounter.vue
- [ ] ActionButtons.vue
  - [ ] 分析按钮
  - [ ] 导入按钮
  - [ ] 清空按钮

**ComparePanel 组件**
- [ ] ComparePanel.vue
- [ ] ViewToggle.vue
  - [ ] 标签切换
  - [ ] 选中状态
- [ ] ErrorStatistics.vue
  - [ ] 统计卡片
  - [ ] 数字动画
- [ ] SideBySideView.vue
  - [ ] 原文显示
  - [ ] 错误高亮
  - [ ] 纠正后显示
- [ ] OriginalOnlyView.vue
- [ ] CorrectedOnlyView.vue
- [ ] ResultActions.vue
  - [ ] 导出按钮
  - [ ] 保存按钮
  - [ ] 重新分析按钮

**AnalysisPanel 组件**
- [ ] AnalysisPanel.vue
- [ ] SearchAndFilter.vue
  - [ ] 搜索输入
  - [ ] 类型筛选
- [ ] ErrorCard.vue
  - [ ] ErrorHeader.vue
  - [ ] ErrorDetails.vue
  - [ ] GrammarRule.vue
  - [ ] 展开/折叠动画
- [ ] LearningTips.vue

**布局控制**
- [ ] LayoutControls.vue
  - [ ] 4 种布局切换按钮
  - [ ] 图标
- [ ] Footer.vue
- [ ] Toast.vue
  - [ ] 全局提示组件
  - [ ] 自动消失

#### API 客户端 (1-2 天)
- [ ] API 基础配置
  ```typescript
  const api = {
    auth: { ... },
    analysis: { ... },
    history: { ... },
    statistics: { ... },
    export: { ... },
    settings: { ... }
  }
  ```
- [ ] 认证拦截器
- [ ] 错误处理拦截器
- [ ] 类型定义
  ```typescript
  interface AnalysisResult { ... }
  interface Error { ... }
  interface Statistics { ... }
  ```

#### 交互逻辑 (2-3 天)
- [ ] 错误卡片点击联动
  - [ ] 点击卡片 → 高亮文中错误
  - [ ] 滚动到错误位置
- [ ] 区域折叠
  - [ ] 折叠动画
  - [ ] 状态记忆
- [ ] 布局切换
  - [ ] 显示/隐藏面板
  - [ ] 响应式适配
- [ ] 视图切换
  - [ ] 并排/原文/纠正后
  - [ ] 过渡动画
- [ ] 加载状态
  - [ ] 分析中动画
  - [ ] 进度提示
- [ ] 错误提示
  - [ ] API 错误显示
  - [ ] 表单验证提示

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

- [ ] API 文档
  - [ ] Swagger/OpenAPI 配置
  - [ ] 接口示例
  - [ ] 错误码说明
- [ ] 部署文档
  - [ ] 环境要求
  - [ ] 部署步骤
  - [ ] 故障排查
- [ ] 用户文档
  - [ ] 功能说明
  - [ ] 使用教程
  - [ ] FAQ

---

## 🎯 里程碑

### Milestone 1: 项目初始化完成
**预计**: Week 1
**标志**:
- [ ] 后端项目可运行
- [ ] 前端项目可运行
- [ ] Docker Compose 可启动所有服务

### Milestone 2: 核心 Pipeline 可用
**预计**: Week 2-3
**标志**:
- [ ] 可处理简单文本并返回纠错结果
- [ ] 前端可显示分析结果

### Milestone 3: MVP 功能完整
**预计**: Week 4-5
**标志**:
- [ ] 所有核心 API 可用
- [ ] 所有核心组件实现
- [ ] 基本的错误处理完成

### Milestone 4: 测试通过
**预计**: Week 6
**标志**:
- [ ] 单元测试覆盖率 > 70%
- [ ] 集成测试通过
- [ ] E2E 测试通过

### Milestone 5: 部署就绪
**预计**: Week 7
**标志**:
- [ ] Docker 镜像构建成功
- [ ] 可在本地通过 Docker Compose 启动
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

## 📊 工作量估算

| 阶段 | 预计工时 | 预计日历时间 |
|------|---------|-------------|
| Phase 2.5 | 2-3 天 | 3 天 |
| 3.1 项目初始化 | 2-3 天 | 3 天 |
| 3.2 后端实现 | 40-50 小时 | 10-14 天 |
| 3.3 前端实现 | 40-50 小时 | 10-14 天 |
| 3.4 测试 | 20-30 小时 | 5-7 天 |
| 3.5 部署准备 | 10-15 小时 | 2-3 天 |
| **总计** | **114-171 小时** | **5-7 周** |

---

**最后更新**: 2026-01-19
**维护者**: English Transfer Assistant Team
