# English Transfer Assistant - 设计文档

> 面向英语学习者的对话纠错工具

**文档版本**: v0.4
**最后更新**: 2026-01-17
**状态**: 设计中（已完成 3/5 节 + 产品定位）

---

## 目录
0. [产品定位与路线图](#产品定位与路线图)
1. [系统架构概览](#第-1-节系统架构概览)
2. [组件设计与安全机制](#第-2-节组件设计与安全机制)
3. [数据流与数据库设计](#第-3-节数据流与数据库设计)
4. [API 设计与接口规范](#第-4-节api-设计与接口规范) ⏳ 待完成
5. [前端交互设计](#第-5-节前端交互设计) ⏳ 待完成

---

## 产品定位与路线图

### 目标用户

**主要用户群体**:
1. **职场人士**: 需要商务英语、邮件沟通、会议表达帮助
2. **英语初学者**: 基础薄弱，经常出现语法、时态、单词错误
3. **备考人群**: 准备四六级、雅思、托福等考试

### 核心使用场景

| 场景 | 描述 | 用户行为 |
|------|------|----------|
| **口语练习复盘** | 练习英语口语对话后，回顾对话内容，纠正错误 | 录音/记录对话 → 粘贴到工具 → 查看纠错 → 学习错误 |
| **聊天记录整理** | 与外教或朋友聊天后，整理和纠正对话内容 | 导出聊天记录 → 批量处理 → 导出学习笔记 |
| **考前/面试前准备** | 准备面试、考试、演讲，需要检查英语表达是否准确 | 写好草稿 → 检查纠错 → 修改完善 |
| **职场沟通辅助** | 工作中需要发送英文邮件/消息，想检查表达是否得体 | 写好邮件 → 批量检查 → 确认发送 |
| **日常实时交流** | 实时对话翻译器 | **v2.0 功能** |

### 产品路线图

#### **v1.0 (MVP) - 批量纠错工具**

**核心功能**:
- ✅ 粘贴对话文本（支持手动输入和文件导入）
- ✅ 4 阶段深度纠错流水线
  - 预处理：分句、说话人识别、中文检测
  - 规则纠错：LanguageTool 处理语法/拼写/时态
  - LLM 优化：智谱 AI 优化表达流畅度
  - 后处理：结果合并、格式化、错误报告
- ✅ 双栏对比视图（原文 vs 纠正后）
- ✅ 交互式错误高亮（点击显示解释）
- ✅ 导出学习笔记（JSON/Markdown/PDF）

**技术实现**:
- 前端：Vue 3 + Composition API
- 后端：Python FastAPI
- 数据库：PostgreSQL
- LLM：智谱 AI
- 语法检查：LanguageTool
- 认证与限流：JWT + Redis

---

#### **v1.5 - 增强批量体验**

**新增功能**:
- 📁 支持导入聊天记录文件（TXT, JSON, WhatsApp 导出格式）
- 📊 错误统计分析
  - 易错点排行（错误类型分布）
  - 进步曲线（历史数据对比）
  - 学习建议（基于错误模式）
- 📚 个人学习空间
  - 历史记录管理
  - 收藏重要纠错
  - 标签分类
- 🔔 智能提醒
  - 每日学习目标
  - 易错点复习提醒

**技术增强**:
- 数据分析模块
- 可视化图表（ECharts）
- 学习算法（个性化推荐）

---

#### **v2.0 - 实时模式**

**新增功能**:
- ⚡ 实时对话纠错
  - WebSocket 实时通信
  - 流式纠错（< 1秒响应）
  - 语音输入支持（STT）
- 📱 移动端适配
  - 响应式设计
  - PWA 支持
  - 离线功能
- 🤖 AI 对话练习伙伴
  - 模拟场景对话
  - 实时纠错反馈
  - 难度自适应

**技术升级**:
- WebSocket 服务
- 语音识别集成
- 移动端优化
- 更智能的 LLM 调用策略

---

### MVP 策略说明

**为什么选择批量处理作为 MVP？**

1. **需求覆盖度**
   - 5 个核心场景中，4 个是批量场景
   - 实时翻译可以后期迭代，不影响核心价值

2. **目标用户匹配度**
   - **初学者**: 练习后系统复盘，详细学习错误原因
   - **备考人群**: 需要完整纠错分析和解释，非即时需求
   - **职场人士**: 准备邮件/演讲稿时批量检查，更稳妥

3. **技术可行性**
   - 批量模式可以深度分析（4 阶段流水线，输出质量最高）
   - 实时模式需要快速响应（< 1秒），可能牺牲准确性
   - 成本可控：批量处理可以优化 API 调用（批量、缓存）
   - 技术风险低：不需要处理并发、流式、WebSocket 等复杂技术

4. **产品价值**
   - 批量纠错有**教育价值**：详细展示错误类型、位置、解释
   - 用户可以**反复学习**，而不只是看到翻译结果
   - 更符合"学习工具"定位，而非"翻译工具"

---

## 第 1 节：系统架构概览

### 整体架构
采用前后端分离 + 4 阶段流水线处理模式

### 前端层（Vue.js）
- 单页面应用（SPA）
- 提供对话输入界面
- 实时显示处理进度（4 个阶段）
- 双栏对比视图（原文 vs 纠正后）
- 交互式错误高亮

### 后端层（Python FastAPI）
- RESTful API 服务
- 4 阶段流水线处理器：
  1. **预处理模块**：文本解析、说话人识别、中文检测
  2. **规则纠错模块**：LanguageTool，处理语法/拼写/时态
  3. **LLM 优化模块**：智谱 AI，优化表达流畅度
  4. **后处理模块**：结果合并、格式化、错误报告

### 数据层
- **PostgreSQL**（开发/生产统一使用）
- 存储对话历史、纠错记录
- 支持导出（JSON/Markdown）

### 外部服务
- **LanguageTool**（本地或 API）
- **智谱 AI** API

---

## 第 2 节：组件设计与安全机制

### 前端组件结构（Vue 3 + Composition API）

```
src/
├── components/
│   ├── ConversationInput.vue      # 对话输入框
│   ├── ProcessingProgress.vue     # 4阶段进度条
│   ├── ComparisonView.vue         # 双栏对比视图
│   ├── ErrorHighlight.vue         # 错误高亮与提示
│   └── ExportDialog.vue           # 导出功能
├── composables/
│   ├── useAuth.js                 # 认证状态管理
│   ├── useRateLimit.js            # 限流处理
│   └── usePipeline.js             # 流水线状态管理
└── stores/
    └── user.js                    # Pinia 用户状态
```

### 后端模块结构（Python FastAPI）

```
backend/
├── api/
│   ├── auth.py                    # JWT 认证端点
│   ├── conversations.py           # 对话处理端点
│   └── rate_limit.py              # 速率限制中间件
├── pipeline/
│   ├── preprocessor.py            # 预处理：分句、说话人识别
│   ├── rule_checker.py            # LanguageTool 集成
│   ├── llm_optimizer.py           # 智谱 AI 调用
│   └── postprocessor.py           # 结果合并与格式化
├── models/
│   ├── user.py                    # 用户模型
│   ├── conversation.py            # 对话记录
│   └── correction_log.py          # 纠错日志
└── services/
    ├── auth_service.py            # JWT 令牌管理
    ├── rate_limit_service.py      # Redis 限流
    └── zhipu_service.py           # 智谱 AI 封装
```

### 安全机制

#### 1. 鉴权系统
- **JWT Token** 认证（access_token + refresh_token）
- 注册/登录接口（邮箱验证）
- 可选：第三方 OAuth（Google/GitHub）

#### 2. 速率限制
- **Redis** 存储请求计数
- 分层限流策略：
  - 匿名用户：**5 次/小时**
  - 免费注册用户：**50 次/天**
  - 付费用户：**500 次/天**
- IP 级别限流防滥用

#### 3. 内容安全
- 输入长度限制（单次 ≤ 5000 字符）
- 敏感内容过滤
- CORS 配置

#### 4. API 安全
- HTTPS 强制（生产环境）
- API Key 管理（智谱 AI）
- SQL 注入防护（ORM 参数化查询）
- 请求体大小限制

---

## 第 3 节：数据流与数据库设计

### 流水线数据流

```
输入对话文本
    ↓
[预处理阶段]
  ├─ 分句（按换行/说话人标识）
  ├─ 说话人识别（A: / B: / 正则匹配）
  ├─ 中文检测（标记 \u4e00-\u9fff 字符）
  └─ 输出：List[Message] {id, speaker, text, has_chinese}
    ↓
[规则纠错阶段]
  ├─ 并发调用 LanguageTool（每句话）
  ├─ 提取错误：grammar, spelling, tense, style
  ├─ 生成初步纠正文本
  └─ 输出：List[Message] + rule_errors[]
    ↓
[LLM 优化阶段]
  ├─ 批量调用智谱 AI（10 句一批）
  ├─ Prompt：优化自然度、保持说话人口吻
  ├─ 处理中文混合句子（翻译+解释）
  └─ 输出：optimized_text + llm_suggestions[]
    ↓
[后处理阶段]
  ├─ 合并规则错误和 LLM 建议
  ├─ 生成错误注释（位置、类型、解释）
  ├─ 格式化为前端需要的 JSON
  └─ 输出：CorrectionResult
```

### PostgreSQL 数据库设计

#### 用户表 (users)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',  -- free, pro
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

#### 对话记录表 (conversations)
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    total_errors INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 错误详情表 (error_details)
```sql
CREATE TABLE error_details (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    message_index INTEGER NOT NULL,  -- 第几句话
    error_type VARCHAR(50),  -- grammar, spelling, tense, chinese_mix
    original_text TEXT,
    correction TEXT,
    explanation TEXT,
    position_start INTEGER,
    position_end INTEGER
);
```

#### 请求日志表 (request_logs)
```sql
CREATE TABLE request_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ip_address INET,
    endpoint VARCHAR(100),
    status_code INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 索引优化
```sql
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_errors_conversation ON error_details(conversation_id);
CREATE INDEX idx_logs_user_time ON request_logs(user_id, created_at);
```

### 错误处理策略

#### 1. 流水线阶段失败
- **预处理失败**：返回 400，提示输入格式
- **规则引擎失败**：跳过，仅使用 LLM
- **LLM 失败**：降级到规则引擎结果
- **后处理失败**：返回原始规则纠错结果

#### 2. API 错误
- **智谱 AI 超时**：重试 3 次，指数退避
- **配额不足**：返回 403，提示升级套餐
- **网络错误**：返回 503，存入队列稍后处理

#### 3. 数据库错误
- **连接失败**：返回 503，记录日志
- **约束冲突**：返回 409（用户已存在）
- **查询超时**：使用缓存降级

---

## 第 4 节：API 设计与接口规范

⏳ **待完成**...

---

## 第 5 节：前端交互设计

⏳ **待完成**...

---

**文档状态**: 设计进行中，已完成前 3 节。
