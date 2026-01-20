# English Transfer Assistant

> 面向英语学习者的 AI 文本纠错与分析工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/vue-3.5+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-red.svg)](https://fastapi.tiangolo.com/)

---

## 📖 项目简介

**English Transfer Assistant** 是一个基于 Web 的英语文本纠错工具，帮助英语学习者改进任何英文文本（对话、邮件、作文等），通过智能纠错和结构化错误分析提升英语水平。

### 核心功能

- ✅ **智能纠错**: AI 识别文本类型和语气，提供准确的语法纠正
- ✅ **深度分析**: 结构化错误卡片，按类型分组，每个错误提供对比、标签、解释和语法规则
- ✅ **学习导向**: 不只纠正，更帮助用户理解错误原因
- ✅ **灵活适配**: 支持"准确性优先"和"自然度优先"两种纠正策略

### 目标用户

- 🏢 **职场人士**: 需要商务英语、邮件沟通、会议表达帮助
- 📚 **英语初学者**: 基础薄弱，经常出现语法、时态、单词错误
- 📝 **备考人群**: 准备四六级、雅思、托福等考试

---

## 🚀 快速开始

### 查看文档

```bash
# 查看文档索引
cat docs/README.md

# 查看 UI 设计（在浏览器中打开）
open docs/02-ui-design/ui-final.html
```

### 文档结构

```
docs/
├── 01-product-research/       # 产品调研
│   ├── findings.md             # 产品调研与决策
│   ├── task_plan.md            # 任务计划
│   └── progress.md             # 进度日志
├── 02-ui-design/              # UI 设计
│   └── ui-final.html           # 最终 UI（可交互）
├── 03-product-features/        # 产品功能
│   ├── product-capabilities.md # 产品能力设计
│   └── functional-requirements.md # 功能点与用例图
├── 04-technical-design/        # 技术方案
│   ├── technical-implementation-plan.md # 技术实现方案
│   └── architecture.md         # 系统架构
├── 05-tasks/                   # 待办事项
│   └── implementation-checklist.md # 实施清单
└── README.md                   # 文档索引
```

---

## 🛠️ 技术栈

### 后端
- **框架**: Python FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **LLM**: 智谱 AI (GLM-4-Flash)
- **语法检查**: LanguageTool
- **认证**: JWT Token

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **样式**: Tailwind CSS
- **路由**: Vue Router

### 基础设施
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **监控**: 日志系统

---

## 📋 产品路线图

### v1.0 (MVP) - 批量纠错工具
- ✅ 粘贴任何英文文本
- ✅ 4 阶段深度纠错（预处理 → 规则纠错 → LLM 优化 → 后处理）
- ✅ 双栏对比 + 错误高亮
- ✅ 导出学习笔记
- ✅ 历史记录保存（最近 10 条）

### v1.5 - 增强批量体验
- ⏳ 支持导入文件（TXT, JSON, Markdown）
- ⏳ 错误统计分析（易错点、进步曲线）
- ⏳ 个人学习空间（历史记录、收藏）
- ⏳ PDF 导出

### v2.0 - 实时模式
- ⏳ 实时对话纠错
- ⏳ 快速响应模式
- ⏳ 移动端适配

---

## 📊 当前进度

- **Phase 1**: ✅ Requirements & Discovery (100%)
- **Phase 2**: ✅ Planning & Structure (100%)
  - ✅ 产品能力设计
  - ✅ UI 设计
  - ✅ 技术实现方案
  - ✅ 功能点定义
  - ✅ 待办事项清单
- **Phase 3**: ⏳ Implementation (0%)
- **Phase 4**: ⏳ Testing (0%)
- **Phase 5**: ⏳ Deployment (0%)

**下一步**: 开始 Phase 3.1 - 项目初始化

---

## 🎯 核心特性

### 1. 智能文本输入
- 全文本类型支持：对话、邮件、作文、日常表达
- AI 自动识别文本类型、语气、说话人
- 支持中英夹杂文本

### 2. 双模式纠正
- **准确性优先**: 纠正语法错误，保留原本风格
- **自然度优先**: 改写成地道表达，可能调整结构

### 3. 分层错误分类
- **主要类型**: 语法、时态、单词选择、中英混用
- **子分类**: 可展开查看详细分类
- **错误卡片**: 原文 → 纠正、类型标签、解释、规则

### 4. 灵活布局
- 三栏布局：输入区 | 对照区 | 分析区
- 区域折叠：三个区域都可以独立隐藏
- 快速布局：4 种预设布局一键切换

---

## 📚 核心文档

| 文档 | 描述 | 适用对象 |
|------|------|---------|
| [产品调研](docs/01-product-research/findings.md) | 目标用户、使用场景、技术栈 | 所有成员 |
| [UI 设计](docs/02-ui-design/ui-final.html) | 完整 UI 实现（可交互） | 前端开发 |
| [产品功能](docs/03-product-features/product-capabilities.md) | 产品能力设计 | 产品经理 |
| [功能详细说明](docs/03-product-features/functional-requirements.md) | 18 个功能点、用例图 | 开发/测试 |
| [技术选型](docs/04-technical-design/technology-selection.md) | 技术栈、部署策略、扩展性 | 开发者 |
| [技术方案](docs/04-technical-design/technical-implementation-plan.md) | API、组件、状态管理 | 开发者 |
| [系统架构](docs/04-technical-design/architecture.md) | 架构设计、数据库 | 架构师 |
| [待办事项](docs/05-tasks/implementation-checklist.md) | 100+ 任务清单 | 所有开发者 |

---

## 🤝 贡献指南

当前项目处于开发阶段，暂不对外开放贡献。

---

## 📄 许可证

MIT License

---

## 👥 团队

English Transfer Assistant Team

---

**项目状态**: 🔄 开发中
**最后更新**: 2026-01-19
