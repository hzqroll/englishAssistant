# Task Plan: English Transfer Assistant
<!-- 面向英语学习者的对话纠错工具 -->

## Goal
构建一个基于 Web 的英语文本纠错工具，帮助英语学习者改进任何英文文本（对话、邮件、作文等），通过智能纠错和结构化错误分析提升英语水平。

## Current Phase
Phase 2: Planning & Structure

## Phases

### Phase 1: Requirements & Discovery
- [x] 理解用户需求（英语学习者对话纠错）
- [x] 确定使用场景（批量处理对话文本）
- [x] 选择技术方案（方案 3：模块化流水线）
- [x] 确定技术栈（Python + Vue + PostgreSQL + 智谱 AI）
- [x] 设计安全机制（JWT 鉴权 + Redis 限流）
- **Status:** complete

### Phase 2: Planning & Structure
- [x] 定义系统架构（前后端分离 + 4 阶段流水线）
- [x] 设计数据库结构（PostgreSQL 4 张表）
- [x] 规划前端组件（Vue 3 + Composition API）
- [x] 规划后端模块（FastAPI + 流水线处理器）
- [x] 设计安全机制（JWT + 速率限制 + 内容过滤）
- [x] **2026-01-19**: 重新定义产品能力
  - 全文本类型支持（不限于对话）
  - AI 上下文意图理解
  - 纠正策略选择（准确性优先 vs 自然度优先）
  - 分层错误分类系统
  - 结构化错误卡片
  - 学习辅助功能
- [x] **2026-01-19**: 完成 UI 设计
  - 基于 ui-ux-pro-max-skill 的 Flat Design 风格
  - 三栏布局，支持区域折叠
  - 布局切换、视图切换
  - 线框风格图标
  - 创建 `docs/ui-final.html`
- [ ] 设计智谱 AI 集成方案
- [ ] 设计 LanguageTool 集成方案
- [ ] 完成第 4 节：API 设计与接口规范
- [ ] 完成第 5 节：前端交互设计
- **Status:** in_progress

### Phase 3: Implementation
- [ ] 初始化项目结构
- [ ] 实现后端 API（FastAPI）
- [ ] 实现流水线处理器
- [ ] 实现前端界面（Vue）
- [ ] 集成智谱 AI
- [ ] 集成 LanguageTool
- [ ] 实现认证和限流
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] 单元测试（流水线各阶段）
- [ ] 集成测试（API 端到端）
- [ ] 前端测试（组件测试）
- [ ] 性能测试（并发处理）
- [ ] 安全测试（鉴权、限流、注入）
- **Status:** pending

### Phase 5: Deployment & Delivery
- [ ] Docker 容器化
- [ ] 部署配置（Nginx + PostgreSQL + Redis）
- [ ] 监控和日志
- [ ] 用户文档
- **Status:** pending

## Key Questions
1. ~~使用什么架构？~~ → 模块化流水线（4 阶段处理）
2. ~~使用什么 LLM？~~ → 智谱 AI
3. ~~如何处理限流？~~ → Redis + 分层策略（匿名/免费/付费）
4. ~~如何存储数据？~~ → PostgreSQL
5. 如何优化智谱 API 调用成本？（待设计）
6. 如何处理长对话的批处理？（待设计）

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 采用方案 3（模块化流水线） | 需要最好的输出质量和教育价值 |
| Python FastAPI + Vue 3 | 全栈 Python + Vue，前后端分离 |
| PostgreSQL | 全生产环境使用，支持复杂查询 |
| 智谱 AI | 国内访问稳定，中文理解好 |
| JWT + Redis 限流 | 公网服务必需的安全机制 |
| LanguageTool + LLM 混合 | 平衡准确性和成本 |
| 批量处理模式 | 用户粘贴对话进行批量纠错 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| 无 | - | - |

## Notes
- ✅ 已完成产品定位与路线图设计
  - 明确目标用户：职场人士、英语初学者、备考人群
  - 定义 5 个核心使用场景（2026-01-19 新增第 5 个：发送前检查）
  - 制定产品路线图：v1.0 MVP (批量) → v1.5 (增强) → v2.0 (实时)
- ✅ 已完成前 3 节设计：架构概览、组件与安全、数据流与数据库
- ✅ **2026-01-19**: 完成产品能力重新设计
  - 从"对话纠错"扩展到"全文本类型纠错"
  - 创建 `docs/plans/2026-01-19-product-capabilities-design.md`
  - 包含 7 个部分的完整产品能力设计
- ✅ **2026-01-19**: 完成 UI 设计
  - 创建 `docs/ui-final.html`（完整功能实现）
  - 基于 ui-ux-pro-max-skill 的设计系统
  - Flat Design 风格 + Glassmorphism 效果
- 待继续第 4 节：API 设计与接口规范
- 待继续第 5 节：前端交互设计

## 更新记录
- **2026-01-17**: 更新产品定位，明确目标用户、使用场景和产品路线图
- **2026-01-19**: 重新定义产品能力，从"对话纠错"扩展到"全文本类型纠错"，完成 UI 设计
