# English Transfer Assistant - 文档索引

**项目**: 面向英语学习者的 AI 文本纠错工具
**文档版本**: v1.0
**最后更新**: 2026-01-19

---

## 📚 文档结构

```
docs/
├── 01-product-research/       # 产品调研
├── 02-ui-design/              # UI 设计
├── 03-product-features/        # 产品功能
├── 04-technical-design/        # 技术方案
├── 05-tasks/                   # 待办事项
└── README.md                   # 本文档
```

---

## 1. 产品调研 (`01-product-research/`)

### 核心文档

#### `findings.md` - 产品调研与决策记录
**内容**:
- ✅ 目标用户定义（职场人士、英语初学者、备考人群）
- ✅ 核心使用场景（5 个场景）
- ✅ 产品路线图（v1.0 → v1.5 → v2.0）
- ✅ 核心功能定义
- ✅ 技术栈选择
- ✅ 架构决策（方案 3：模块化流水线）
- ✅ 安全机制设计
- ✅ UI 设计系统说明

**适用对象**: 所有团队成员、新加入成员

#### `task_plan.md` - 任务计划
**内容**:
- ✅ 项目目标
- ✅ Phase 1-5 划分
- ✅ 当前进度状态
- ✅ 关键问题解答
- ✅ 决策记录
- ✅ 更新记录

**适用对象**: 项目经理、技术负责人

#### `progress.md` - 进度日志
**内容**:
- ✅ Session 记录
- ✅ 每个会话完成的工作
- ✅ 产品能力定义完成情况
- ✅ UI 设计完成情况
- ✅ 决策记录表
- ✅ 下一步计划

**适用对象**: 项目经理、所有团队成员

---

## 2. UI 设计 (`02-ui-design/`)

### 核心文档

#### `ui-final.html` - 最终 UI 设计（可交互）
**内容**:
- ✅ 完整的三栏布局实现
- ✅ 导航栏（glassmorphism 效果）
- ✅ 输入区（模式切换、智能文本框、字符计数）
- ✅ 对照区（视图切换、错误统计、并排对照）
- ✅ 分析区（搜索筛选、错误卡片、学习建议）
- ✅ 布局快速切换按钮（4 种预设）
- ✅ 区域折叠功能
- ✅ 线框风格图标
- ✅ 响应式设计

**技术栈**:
- Tailwind CSS
- Flat Design 风格
- Poppins + Open Sans 字体
- 深色渐变背景 + Glassmorphism

**配色**:
- 主色：#3B82F6（蓝色）
- 强调色：#F97316（橙色）
- 背景：深蓝渐变

**如何使用**:
```bash
# 在浏览器中打开
open docs/02-ui-design/ui-final.html
```

**适用对象**: 前端开发者、UI 设计师、所有团队成员

---

## 3. 产品功能 (`03-product-features/`)

### 核心文档

#### `product-capabilities.md` - 产品能力设计
**内容**:
- ✅ 产品定位与价值主张
- ✅ 核心使用场景（5 个）
- ✅ 核心输入输出能力
- ✅ 错误分析系统（分层分类）
- ✅ AI 智能理解能力
- ✅ 用户交互流程
- ✅ 边界情况处理

**适用对象**: 产品经理、所有团队成员

#### `functional-requirements.md` - 功能点与用例图
**内容**:
- ✅ 7 个功能模块划分
- ✅ 4 个用例图（主用例图、文本分析、历史记录、布局控制）
- ✅ 18 个功能点详细说明
- ✅ 每个功能的主要流程和替代流程
- ✅ 功能优先级（P0/P1/P2）
- ✅ 功能依赖关系
- ✅ 开发建议（4 个 Sprint）
- ✅ 功能追踪表

**功能清单**:
- P0 (MVP 必需): 7 个功能
- P1 (重要): 10 个功能
- P2 (增强): 1 个功能

**适用对象**: 开发者、测试工程师、产品经理

---

## 4. 技术方案 (`04-technical-design/`)

### 核心文档

#### `technology-selection.md` - 技术选型文档
**内容**:
- ✅ 技术选型概述与设计原则
- ✅ 后端技术栈（FastAPI、Python、Uvicorn）
- ✅ 前端技术栈（Vue 3、Vite、TypeScript、Tailwind CSS）
- ✅ 数据库技术（PostgreSQL 16、SQLAlchemy 2.0、asyncpg）
- ✅ 缓存技术（Memory Cache → Redis 渐进式方案）
- ✅ AI 服务集成（智谱 AI、LanguageTool）
- ✅ 部署策略（4 种部署方案：开发、小型、中型、大型）
- ✅ 架构模式与扩展性（Repository 模式、Factory 模式）
- ✅ 配置管理（环境变量、多环境支持）
- ✅ 开发工具链（Poetry、Black、Ruff、Pytest、ESLint、Prettier）
- ✅ 版本兼容性矩阵和依赖清单
- ✅ 扩展路径规划

**适用对象**: 所有开发者、技术负责人、架构师

#### `technical-implementation-plan.md` - 技术实现方案
**内容**:
- ✅ API 端点设计（6 个模块，15+ 端点）
  - 认证模块
  - 文本纠错模块
  - 历史记录模块
  - 统计分析模块
  - 导出模块
  - 用户设置模块
- ✅ 前端组件架构（组件树，20+ 组件）
- ✅ 状态管理方案（Pinia Store）
- ✅ 智谱 AI 集成方案
  - 文本意图识别
  - 自然度优化
  - 中英混用纠正
- ✅ LanguageTool 集成方案
  - 语法检查
  - 错误分类
- ✅ 数据流设计
  - Pipeline 4 阶段
  - 错误联动
- ✅ 实施待办清单（100+ 任务）
- ✅ 工作量估算（114-171 小时）
- ✅ 技术风险与应对

**适用对象**: 后端开发者、前端开发者、架构师

#### `architecture.md` - 系统架构设计
**内容**:
- ✅ 系统架构概览
- ✅ 组件设计与安全机制
- ✅ 数据流与数据库设计
- ✅ 4 张核心数据库表
- ✅ 流水线 4 阶段设计

**适用对象**: 架构师、技术负责人

---

## 5. 待办事项 (`05-tasks/`)

### 核心文档

#### `implementation-checklist.md` - 实施待办清单
**内容**:
- ✅ 100+ 个详细任务
- ✅ 分为 6 个阶段
  - Phase 2.5: 技术设计完善
  - Phase 3.1: 项目初始化（20+ 任务）
  - Phase 3.2: 后端实现（50+ 任务）
  - Phase 3.3: 前端实现（40+ 任务）
  - Phase 3.4: 测试（15+ 任务）
  - Phase 3.5: 部署准备（10+ 任务）
- ✅ 工作量估算：114-171 小时（5-7 周）
- ✅ 5 个里程碑定义
- ✅ 优先级标记（P0/P1/P2）
- ✅ 子任务拆解

**如何使用**:
1. 查看当前阶段
2. 按优先级选择任务
3. 勾选完成状态
4. 追踪进度

**适用对象**: 所有开发者、项目经理

---

## 📊 文档速查表

| 我想了解... | 查看文档 |
|------------|---------|
| **产品是什么？** | `01-product-research/findings.md` |
| **为什么这样设计？** | `01-product-research/task_plan.md` |
| **当前进度？** | `01-product-research/progress.md` |
| **UI 长什么样？** | `02-ui-design/ui-final.html`（在浏览器中打开） |
| **有哪些功能？** | `03-product-features/product-capabilities.md` |
| **功能详细说明？** | `03-product-features/functional-requirements.md` |
| **使用什么技术？** | `04-technical-design/technology-selection.md` |
| **API 怎么设计？** | `04-technical-design/technical-implementation-plan.md` |
| **系统架构？** | `04-technical-design/architecture.md` |
| **接下来做什么？** | `05-tasks/implementation-checklist.md` |

---

## 🎯 新成员快速上手

### 第 1 步：了解产品（30 分钟）
1. 阅读 `01-product-research/findings.md`
2. 在浏览器打开 `02-ui-design/ui-final.html` 查看 UI
3. 阅读 `03-product-features/product-capabilities.md`

### 第 2 步：理解功能（1 小时）
1. 阅读 `03-product-features/functional-requirements.md`
2. 查看用例图
3. 理解 18 个功能点

### 第 3 步：熟悉技术方案（2 小时）
1. 阅读 `04-technical-design/technical-implementation-plan.md`
2. 阅读 `04-technical-design/architecture.md`
3. 理解 API 设计和组件架构

### 第 4 步：开始开发
1. 查看 `05-tasks/implementation-checklist.md`
2. 找到当前阶段的任务
3. 开始实施

---

## 📝 文档维护

### 文档更新规范
1. **产品调研文档**: 产品变更时更新
2. **UI 设计文档**: UI 变更时更新 `ui-final.html`
3. **产品功能文档**: 新增功能时更新
4. **技术方案文档**: 架构变更时更新
5. **待办事项文档**: 每日更新进度

### 文档命名规范
- 使用小写字母和连字符
- 文件名要清晰描述内容
- 版本号通过 Git 管理

---

## 🔗 相关资源

- **项目根目录**: `/Users/roll/Documents/personal/claude/project/english_transfer_assistant/`
- **文档目录**: `docs/`
- **设计系统参考**: ui-ux-pro-max-skill

---

## 📧 联系方式

**项目**: English Transfer Assistant
**团队**: English Transfer Assistant Team
**最后更新**: 2026-01-19

---

**文档状态**: ✅ 完成
**版本**: v1.0
