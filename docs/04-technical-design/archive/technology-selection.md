# English Transfer Assistant - 技术选型文档

**项目**: 面向英语学习者的 AI 文本纠错工具

**文档版本**: v1.0

**创建日期**: 2026-01-20

**状态**: 最终版

---

## 目录

1. [技术选型概述](#技术选型概述)
2. [后端技术栈](#后端技术栈)
3. [前端技术栈](#前端技术栈)
4. [数据库技术](#数据库技术)
5. [缓存技术](#缓存技术)
6. [AI 服务集成](#ai-服务集成)
7. [部署策略](#部署策略)
8. [架构模式与扩展性](#架构模式与扩展性)
9. [配置管理](#配置管理)
10. [开发工具链](#开发工具链)

---

## 技术选型概述

### 设计原则

1. **简单优先**: 单人开发项目，避免过度设计
2. **渐进增强**: MVP 使用简单技术，后期可扩展
3. **可替换性**: 通过抽象层支持技术栈升级
4. **成本可控**: 优先使用开源/低成本方案
5. **开发效率**: 选择团队熟悉且生态成熟的技术

### 技术栈总览

| 分类 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **后端框架** | FastAPI | 0.115+ | Web 框架 |
| **运行时** | Python | 3.11+ | 后端语言 |
| **ASGI 服务器** | Uvicorn | 0.30+ | 异步服务器 |
| **数据库** | PostgreSQL | 16 | 主数据库 |
| **ORM** | SQLAlchemy | 2.0+ | 数据库抽象 |
| **异步驱动** | asyncpg | - | PostgreSQL 异步驱动 |
| **数据迁移** | Alembic | - | 数据库版本管理 |
| **缓存** | Python Dict / Redis | - | 内存缓存 / 分布式缓存 |
| **前端框架** | Vue | 3.5+ | UI 框架 |
| **构建工具** | Vite | 5.0+ | 前端构建工具 |
| **语言** | TypeScript | 5.3+ | 前端类型系统 |
| **状态管理** | Pinia | - | Vue 状态管理 |
| **样式** | Tailwind CSS | 3.4+ | CSS 框架 |
| **LLM 服务** | 智谱 AI | GLM-4-Flash | 文本优化 |
| **语法检查** | LanguageTool | - | 语法规则引擎 |
| **认证** | JWT (python-jose) | - | 令牌认证 |
| **密码哈希** | passlib | - | 密码加密 |

---

## 后端技术栈

### 1. FastAPI

**选择理由**:

1. **原生异步支持**: 基于 ASGI，支持高并发
2. **自动文档生成**: Swagger UI 和 ReDoc 开箱即用
3. **类型安全**: Pydantic 数据验证，减少运行时错误
4. **性能优异**: 性能接近 Node.js 和 Go
5. **生态成熟**: 中间件、ORM、依赖注入支持完善
6. **学习曲线平缓**: 类似 Flask，易于上手

**版本选择**: 0.115+ (稳定版本)

**核心依赖**:
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.9.0
pydantic-settings==2.6.0
python-multipart==0.0.12
```

### 2. Python 3.11+

**选择理由**:

1. **性能提升**: 比 3.8 快 10-60%
2. **类型系统增强**: 更好的类型提示支持
3. **异步优化**: asyncio 性能提升
4. **错误消息改进**: 更清晰的错误追踪
5. **长期支持**: 官方维护至 2027 年

**语言特性使用**:
- 类型提示 (Type Hints)
- 异步/等待 (async/await)
- 上下文管理器 (Context Managers)
- 数据类 (dataclasses)

### 3. Uvicorn

**选择理由**:

1. **ASGI 标准**: 完整实现 ASGI 规范
2. **高性能**: 基于 uvloop 和 httptools
3. **热重载**: 开发模式支持自动重启
4. **进程管理**: 支持多 worker 部署

**启动命令**:
```bash
# 开发环境（单进程，热重载）
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境（多进程）
uvicorn backend.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## 数据库技术

### PostgreSQL 16

**选择理由**:

1. **功能强大**: 支持复杂查询、JSON、全文搜索
2. **数据完整性**: ACID 事务，外键约束
3. **扩展性**: 可扩展到 TB 级数据
4. **开源免费**: 无许可证成本
5. **生态成熟**: 丰富的工具和社区支持
6. **云服务支持**: Supabase、Neon、AWS RDS 等托管服务

**用户明确要求**: "数据库使用：PostgreSQL"

### SQLAlchemy 2.0+

**选择理由**:

1. **异步支持**: 2.0 版本原生支持 async/await
2. **ORM 功能**: 自动映射 SQL 到 Python 对象
3. **数据库无关**: 理论上支持 MySQL、SQLite 等切换
4. **类型安全**: 配合 Pydantic 使用
5. **迁移工具**: Alembic 集成

**Repository 模式**: 使用 Repository 抽象层实现数据库可替换性

```python
# backend/repositories/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """数据库仓库基类"""

    @abstractmethod
    async def create(self, obj: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def update(self, id: str, obj: T) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
```

### asyncpg

**选择理由**:

1. **高性能**: C 语言扩展，比 libpq 快 3 倍
2. **原生异步**:专为 asyncio 设计
3. **连接池**: 内置连接池管理
4. **类型支持**: 支持 JSON、UUID 等 PostgreSQL 类型

**连接字符串**:
```
postgresql+asyncpg://eta_user:eta_password@localhost:5432/english_transfer
```

### Alembic

**选择理由**:

1. **版本控制**: 数据库 schema 迁移管理
2. **回滚支持**: 支持迁移回滚
3. **自动生成**: 可从 SQLAlchemy 模型生成迁移脚本
4. **多环境**: 支持开发、测试、生产环境

**基本命令**:
```bash
# 生成迁移
alembic revision --autogenerate -m "Add users table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 缓存技术

### 渐进式缓存策略

**MVP 阶段**: Python Dict 内存缓存
**生产阶段**: Redis 分布式缓存

### MVP: Python Dict

**选择理由**:

1. **零依赖**: 无需额外服务
2. **简单高效**: 单用户场景下足够
3. **开发友好**: 易于调试和测试
4. **成本低**: 无基础设施成本

**实现示例**:
```python
# backend/cache/memory_cache.py
from typing import Any, Optional
import time

class MemoryCache:
    """简单的内存缓存实现"""

    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, expire_time = self._cache[key]
        if time.time() > expire_time:
            del self._cache[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self._cache[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
```

### 生产: Redis

**何时升级**:

- 需要多进程/多服务器部署
- 需要持久化缓存
- 需要分布式限流
- 用户量 > 1000

**Redis 配置**:
```python
# backend/cache/redis_cache.py
import aioredis

class RedisCache:
    """Redis 缓存实现"""

    def __init__(self, url: str):
        self.redis = aioredis.from_url(url)

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
```

### 缓存抽象层

```python
# backend/cache/base.py
from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseCache(ABC):
    """缓存基类，支持不同实现"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass
```

**配置驱动切换**:
```python
# backend/core/cache.py
from backend.cache.base import BaseCache
from backend.cache.memory_cache import MemoryCache
from backend.cache.redis_cache import RedisCache

def get_cache() -> BaseCache:
    """根据配置返回缓存实现"""
    if settings.cache_backend == "redis":
        return RedisCache(settings.redis_url)
    return MemoryCache()
```

---

## 前端技术栈

### 1. Vue 3.5+

**选择理由**:

1. **渐进式框架**: 易于集成到现有项目
2. **组合式 API**: 更好的逻辑复用和类型推导
3. **性能优异**: 虚拟 DOM 优化，编译时优化
4. **生态成熟**: Vue Router、Pinia、Vite 官方支持
5. **学习曲线**: 比 React 更平缓
6. **单文件组件**: .vue 文件格式清晰

### 2. Vite 5.0+

**选择理由**:

1. **极速热更新**: 基于 ESM，比 Webpack 快 10 倍
2. **开箱即用**: TypeScript、CSS 预处理器支持
3. **生产优化**: 自动代码分割、Tree-shaking
4. **生态丰富**: 插件系统完善
5. **开发体验**: 简洁的配置

**构建命令**:
```bash
# 开发环境
npm run dev

# 生产构建（输出到 backend/static/）
npm run build

# 预览构建结果
npm run preview
```

**配置静态文件输出**:
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: '../backend/static',
    emptyOutDir: true,
  },
})
```

### 3. TypeScript 5.3+

**选择理由**:

1. **类型安全**: 编译时捕获错误
2. **IDE 支持**: 自动补全、重构
3. **可维护性**: 大型项目必备
4. **文档性**: 类型即文档

### 4. Tailwind CSS 3.4+

**选择理由**:

1. **实用优先**: 快速构建 UI
2. **设计系统**: 统一的颜色、间距规范
3. **按需生成**: 生产环境只打包用到的样式
4. **Dark Mode**: 内置暗色模式支持
5. **响应式**: 移动优先的断点系统

**配置示例**:
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        accent: '#F97316',
      }
    }
  }
}
```

### 5. Pinia

**选择理由**:

1. **Vue 3 官方推荐**: 替代 Vuex
2. **轻量级**: 比 Vuex 小很多
3. **类型友好**: 完美的 TypeScript 支持
4. **DevTools**: Vue DevTools 集成
5. **简洁 API**: 不需要 mutations

**Store 示例**:
```typescript
// stores/analysisStore.ts
import { defineStore } from 'pinia'

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    isAnalyzing: false,
    currentAnalysis: null,
  }),
  actions: {
    async analyzeText(text: string) {
      this.isAnalyzing = true
      // ...
    }
  }
})
```

### 6. Axios

**选择理由**:

1. **拦截器**: 请求/响应拦截
2. **错误处理**: 统一的错误处理
3. **取消请求**: AbortController 支持
4. **进度监控**: 上传/下载进度
5. **兼容性**: 支持 IE11（虽不需要）

**配置示例**:
```typescript
// api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器（添加 Token）
client.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器（处理错误）
client.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // Token 过期，跳转登录
    }
    return Promise.reject(error)
  }
)

export default client
```

---

## AI 服务集成

### 1. 智谱 AI (GLM-4-Flash)

**选择理由**:

1. **中文优化**: 对中英混用文本处理更好
2. **成本优势**: Flash 模型比 GPT-4 便宜 10 倍
3. **快速响应**: Flash 模型专为速度优化
4. **国内服务**: 网络稳定，无需代理
5. **API 友好**: 标准 OpenAI 格式

**SDK 安装**:
```bash
pip install zhipuai
```

**核心功能**:
- 文本意图识别 (text_type, tone, speakers)
- 自然度优化 (naturalness correction)
- 中英混用纠正 (Chinese-English mixing)

**成本控制**:
- 使用 GLM-4-Flash (0.1 元/1K tokens)
- 批量处理 (一次 API 调用处理多个句子)
- 缓存机制 (相同文本 24 小时内不重复调用)
- 降级策略 (API 失败时使用纯规则引擎)

### 2. LanguageTool

**选择理由**:

1. **规则引擎**: 基于 Linguistic Grammar 规则
2. **免费使用**: 本地部署无成本
3. **Python 支持**: language_tool_python 库
4. **准确性高**: 语法、拼写、时态检查
5. **可扩展**: 支持自定义规则

**SDK 安装**:
```bash
pip install language-tool-python
```

**使用示例**:
```python
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')
matches = tool.check("I go to park yesterday.")

for match in matches:
    print(f"错误: {match.ruleId}")
    print(f"建议: {match.replacements}")
```

---

## 部署策略

### 部署模式演进

```
MVP (开发)     →  小型部署         →  中型部署           →  大型部署
↓              ↓                   ↓                    ↓
直接运行       直接运行 +          Docker Compose       Kubernetes + CI/CD
本地 PostgreSQL  托管 PostgreSQL    (PostgreSQL + Redis)  (多服务编排)
               (Supabase/Neon)
```

### 方案 1: 开发环境 (MVP)

**适用场景**: 本地开发、单用户测试

**技术栈**:
- Python 直接运行
- 本地 PostgreSQL
- 内存缓存
- 前端开发服务器 (Vite dev)

**启动命令**:
```bash
# 1. 启动 PostgreSQL
brew services start postgresql  # macOS
# 或
sudo systemctl start postgresql  # Linux

# 2. 创建数据库
createdb english_transfer

# 3. 安装依赖
pip install -r requirements.txt
npm install

# 4. 运行迁移
alembic upgrade head

# 5. 启动后端
uvicorn backend.main:app --reload

# 6. 启动前端（新终端）
npm run dev
```

**优点**:
- 最简单，无容器化开销
- 易于调试（热重载、断点）
- 快速迭代

**缺点**:
- 需要手动管理 PostgreSQL
- 不适合生产环境

---

### 方案 2: 小型生产部署

**适用场景**: 个人项目、小团队 (< 100 用户)

**技术栈**:
- Python 直接运行
- 托管 PostgreSQL (Supabase/Neon)
- 内存缓存
- 前端静态文件由 FastAPI 服务

**部署步骤**:

1. **选择托管 PostgreSQL**:
   - **Supabase** (推荐): 免费层 500MB，自动备份
   - **Neon**: Serverless PostgreSQL，按使用付费
   - **Railway**: 简单易用

2. **构建前端**:
   ```bash
   npm run build  # 输出到 backend/static/
   ```

3. **配置环境变量**:
   ```bash
   # .env.production
   DATABASE_URL=postgresql+asyncpg://user:pass@host/db
   ZHIPUAI_API_KEY=your_api_key
   CACHE_BACKEND=memory
   ```

4. **启动服务**:
   ```bash
   # 安装依赖
   pip install -r requirements.txt

   # 运行迁移
   alembic upgrade head

   # 启动服务器（生产模式）
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
   ```

5. **反向代理 (可选)**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

**优点**:
- 无需容器化知识
- 数据库自动备份和扩展
- 部署简单

**缺点**:
- 需要手动管理进程 (可用 systemd/supervisor)
- 扩展性有限

---

### 方案 3: 中型生产部署

**适用场景**: 团队项目、小规模商业应用 (< 1000 用户)

**技术栈**:
- Docker Compose 编排
- PostgreSQL 容器
- Redis 容器
- Nginx 反向代理

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: eta_user
      POSTGRES_PASSWORD: eta_password
      POSTGRES_DB: english_transfer
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://eta_user:eta_password@postgres:5432/english_transfer
      REDIS_URL: redis://redis:6379
      CACHE_BACKEND: redis
      ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend/static:/app/static

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./backend/static:/usr/share/nginx/html
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

**部署命令**:
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**优点**:
- 一键部署
- 环境一致性好
- 数据持久化
- 易于扩展

**缺点**:
- 需要 Docker 知识
- 单机部署，无法水平扩展

---

### 方案 4: 大型生产部署 (未来)

**适用场景**: 商业应用、大规模用户 (> 1000 用户)

**技术栈**:
- Kubernetes 编排
- 托管 PostgreSQL (Supabase/Neon/AWS RDS)
- 托管 Redis (Redis Cloud/ElastiCache)
- CI/CD 自动化部署
- 监控和日志 (Prometheus + Grafana)

**何时升级**:
- 需要多服务器负载均衡
- 需要自动扩缩容
- 需要高可用性
- 团队规模 > 5 人

**说明**: 此方案超出当前单人开发范围，暂不详细设计

---

## 架构模式与扩展性

### 1. Repository 模式

**目的**: 抽象数据库访问层，支持数据库切换

**结构**:
```
backend/repositories/
├── base.py              # 抽象基类
├── user_repository.py   # 用户仓库
├── analysis_repository.py  # 分析仓库
└── error_repository.py  # 错误仓库
```

**基类定义**:
```python
# backend/repositories/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """数据库仓库抽象基类"""

    @abstractmethod
    async def create(self, obj: T) -> T:
        """创建对象"""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """根据 ID 获取对象"""
        pass

    @abstractmethod
    async def list(self, limit: int = 10, offset: int = 0) -> List[T]:
        """列出对象"""
        pass

    @abstractmethod
    async def update(self, id: str, obj: T) -> Optional[T]:
        """更新对象"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """删除对象"""
        pass
```

**SQLAlchemy 实现**:
```python
# backend/repositories/analysis_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.analysis import Analysis
from backend.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[Analysis]):
    """SQLAlchemy 分析仓库实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: Analysis) -> Analysis:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, id: str) -> Optional[Analysis]:
        result = await self.session.execute(
            select(Analysis).where(Analysis.id == id)
        )
        return result.scalar_one_or_none()

    # ... 其他方法
```

**未来切换数据库示例**:
```python
# backend/repositories/mongodb_analysis_repository.py
class MongoDBAnalysisRepository(BaseRepository[Analysis]):
    """MongoDB 分析仓库实现（示例）"""

    def __init__(self, client):
        self.collection = client.english_transfer.analyses

    async def create(self, obj: Analysis) -> Analysis:
        doc = obj.model_dump()
        result = await self.collection.insert_one(doc)
        obj.id = str(result.inserted_id)
        return obj

    # ... 其他方法
```

### 2. Factory 模式

**目的**: 根据配置动态创建 Repository 和 Cache 实例

```python
# backend/core/factory.py
from backend.cache.base import BaseCache
from backend.cache.memory_cache import MemoryCache
from backend.cache.redis_cache import RedisCache
from backend.repositories.base import BaseRepository
from backend.repositories.analysis_repository import AnalysisRepository

def get_cache() -> BaseCache:
    """根据配置返回缓存实例"""
    if settings.cache_backend == "redis":
        return RedisCache(settings.redis_url)
    return MemoryCache()

def get_analysis_repository() -> BaseRepository:
    """根据配置返回分析仓库实例"""
    session = get_db_session()
    return AnalysisRepository(session)
```

### 3. 服务层 (Service Layer)

**目的**: 业务逻辑层，协调 Repository 和外部服务

```
backend/services/
├── auth_service.py       # 认证服务
├── analysis_service.py   # 分析服务
├── zhipu_service.py      # 智谱 AI 服务
└── language_tool_service.py  # LanguageTool 服务
```

**示例**:
```python
# backend/services/analysis_service.py
from backend.repositories.analysis_repository import AnalysisRepository
from backend.services.zhipu_service import ZhipuService
from backend.services.language_tool_service import LanguageToolService

class AnalysisService:
    """文本分析服务"""

    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        zhipu_service: ZhipuService,
        lt_service: LanguageToolService,
    ):
        self.analysis_repo = analysis_repo
        self.zhipu_service = zhipu_service
        self.lt_service = lt_service

    async def analyze_text(self, text: str, mode: str) -> AnalysisResult:
        """分析文本（协调多个服务）"""
        # 1. 语言工具检查
        grammar_errors = await self.lt_service.check_grammar(text)

        # 2. 智谱 AI 优化
        if mode == "natural":
            optimized_text = await self.zhipu_service.optimize_naturalness(text)
        else:
            optimized_text = text

        # 3. 保存到数据库
        analysis = Analysis(
            original_text=text,
            corrected_text=optimized_text,
            errors=grammar_errors,
        )
        await self.analysis_repo.create(analysis)

        return analysis
```

### 4. 分层架构

```
┌─────────────────────────────────────┐
│         Frontend (Vue)              │
└──────────────┬──────────────────────┘
               │ HTTP API
┌──────────────▼──────────────────────┐
│         API Layer (FastAPI)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Service Layer (业务逻辑)      │
│  - AnalysisService                  │
│  - AuthService                      │
└──────────┬──────────┬───────────────┘
           │          │
┌──────────▼─────┐ ┌─▼──────────────┐
│  Repository    │ │  External APIs  │
│  (Database)    │ │  - Zhipu AI     │
│                │ │  - LanguageTool │
└────────────────┘ └─────────────────┘
```

**优点**:
- 职责清晰
- 易于测试
- 支持替换底层实现

---

## 配置管理

### 环境变量

**文件结构**:
```
.
├── .env                    # 本地开发（不提交到 Git）
├── .env.example            # 环境变量模板
├── .env.production         # 生产环境（不提交）
└── .env.docker             # Docker 环境（不提交）
```

### 环境变量定义

```python
# backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "English Transfer Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # 数据库配置
    database_url: str = "postgresql+asyncpg://eta_user:eta_password@localhost:5432/english_transfer"

    # 缓存配置
    cache_backend: str = "memory"  # "memory" | "redis"
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600  # 默认 TTL（秒）

    # AI 服务配置
    zhipuai_api_key: str
    zhipuai_model: str = "glm-4-flash"

    # JWT 配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 限流配置
    rate_limit_enabled: bool = True
    anonymous_limit_per_hour: int = 5
    free_user_limit_per_day: int = 50
    pro_user_limit_per_day: int = 500

    # CORS 配置
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 环境变量模板

```bash
# .env.example

# 应用配置
APP_NAME=English Transfer Assistant
DEBUG=true

# 数据库
DATABASE_URL=postgresql+asyncpg://eta_user:eta_password@localhost:5432/english_transfer

# 缓存
CACHE_BACKEND=memory  # memory | redis
REDIS_URL=redis://localhost:6379

# AI 服务
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_MODEL=glm-4-flash

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 限流
RATE_LIMIT_ENABLED=true
ANONYMOUS_LIMIT_PER_HOUR=5
FREE_USER_LIMIT_PER_DAY=50
PRO_USER_LIMIT_PER_DAY=500

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

---

## 开发工具链

### 后端开发工具

| 工具 | 用途 | 版本 |
|------|------|------|
| **Poetry** | 依赖管理 | 1.8+ |
| **Black** | 代码格式化 | 24.0+ |
| **Ruff** | 代码检查 | 0.1+ |
| **Pytest** | 测试框架 | 7.4+ |
| **pytest-asyncio** | 异步测试 | 0.21+ |
| **httpx** | HTTP 测试客户端 | 0.25+ |
| **pre-commit** | Git hooks | 3.6+ |

**安装命令**:
```bash
pip install poetry black ruff pytest pytest-asyncio httpx pre-commit
```

**配置示例**:

**Poetry (pyproject.toml)**:
```toml
[tool.poetry]
name = "english-transfer-assistant"
version = "1.0.0"
description = "AI-powered English text correction tool"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.30.0"}
sqlalchemy = "^2.0.0"
asyncpg = "^0.29.0"
alembic = "^1.13.0"
pydantic = "^2.9.0"
pydantic-settings = "^2.6.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
zhipuai = "^1.0.0"
language-tool-python = "^2.7.1"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^24.0.0"
ruff = "^0.1.0"
httpx = "^0.25.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**Black**:
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

**Ruff**:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
]
```

**Pytest**:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 前端开发工具

| 工具 | 用途 | 版本 |
|------|------|------|
| **npm** | 包管理器 | 10+ |
| **TypeScript** | 类型检查 | 5.3+ |
| **ESLint** | 代码检查 | 8+ |
| **Prettier** | 代码格式化 | 3+ |
| **Vitest** | 单元测试 | 1+ |
| **Playwright** | E2E 测试 | 1.40+ |

**package.json**:
```json
{
  "name": "english-transfer-assistant-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write src/",
    "test": "vitest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.55.0",
    "eslint-plugin-vue": "^9.19.0",
    "prettier": "^3.1.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

### Git Hooks (pre-commit)

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**安装**:
```bash
pip install pre-commit
pre-commit install
```

---

## 附录

### A. 版本兼容性矩阵

| 依赖 | Python 3.11 | Python 3.12 | 说明 |
|------|------------|------------|------|
| FastAPI 0.115 | ✅ | ✅ | 完全支持 |
| SQLAlchemy 2.0 | ✅ | ✅ | 完全支持 |
| asyncpg 0.29 | ✅ | ✅ | 完全支持 |
| Vue 3.5 | - | - | 前端不依赖 Python |

### B. 依赖清单

**后端 (requirements.txt)**:
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.9.0
pydantic-settings==2.6.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
zhipuai==1.0.0
language-tool-python==2.7.1
aioredis==2.0.1
```

**前端 (package.json - 核心依赖)**:
```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  }
}
```

### C. 参考资料

| 资源 | 链接 |
|------|------|
| FastAPI 官方文档 | https://fastapi.tiangolo.com/ |
| SQLAlchemy 2.0 文档 | https://docs.sqlalchemy.org/en/20/ |
| Vue 3 官方文档 | https://vuejs.org/ |
| 智谱 AI API 文档 | https://open.bigmodel.cn/ |
| LanguageTool 文档 | https://languagetool.org/ |
| PostgreSQL 文档 | https://www.postgresql.org/docs/ |
| Vite 文档 | https://vitejs.dev/ |

---

## 总结

### 技术选型决策记录

| 决策点 | 选择 | 替代方案 | 理由 |
|--------|------|---------|------|
| 后端框架 | FastAPI | Flask, Django | 原生异步、性能高、自动文档 |
| 数据库 | PostgreSQL 16 | MySQL, SQLite | 功能强大、用户明确要求 |
| ORM | SQLAlchemy 2.0 | Django ORM, TypeORM | 异步支持、数据库无关 |
| 缓存 | Memory → Redis | Memcached | 渐进式、配置驱动 |
| 前端框架 | Vue 3 | React, Svelte | 学习曲线平缓、组合式 API |
| 构建工具 | Vite | Webpack, esbuild | 速度快、开发体验好 |
| 状态管理 | Pinia | Vuex, Redux | 轻量、类型友好 |
| LLM 服务 | 智谱 AI | OpenAI, Claude | 成本低、中文优化 |
| 语法检查 | LanguageTool | Grammarly | 开源、本地部署 |

### 扩展路径

**当前 (MVP)**:
- Python 直接运行
- 本地/托管 PostgreSQL
- 内存缓存
- 单进程部署

**下一步 (生产)**:
- Docker Compose 部署
- 托管 PostgreSQL (Supabase/Neon)
- Redis 缓存
- Nginx 反向代理

**未来 (规模化)**:
- Kubernetes 编排
- CI/CD 自动化
- 监控和日志系统
- 多区域部署

---

**文档状态**: ✅ 完成

**最后更新**: 2026-01-20

**维护者**: English Transfer Assistant Team
