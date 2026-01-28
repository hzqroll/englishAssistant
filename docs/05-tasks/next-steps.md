# 下一步开发任务清单

**创建日期**: 2026-01-27
**当前状态**: Phase 3 实施阶段 (35%)
**目标**: 完成 MVP 核心功能

---

## 📋 任务优先级说明

- **P0 (紧急)**: 阻塞 MVP 发布的关键任务
- **P1 (高)**: 重要功能，影响用户体验
- **P2 (中)**: 增强功能，可延后

---

## 🚀 P0 任务：阻塞 MVP 发布

### 任务组 1: 配置 Alembic 数据库迁移 (2-3 小时)

**目标**: 建立数据库版本管理和迁移机制

#### 1.1 初始化 Alembic
```bash
cd backend
poetry run alembic init alembic
```

**检查清单**:
- [ ] 确认生成 `alembic/` 目录
- [ ] 确认生成 `alembic.ini` 配置文件
- [ ] 将 `alembic/` 目录移动到项目根目录（可选）

#### 1.2 配置 alembic/env.py

**文件**: `backend/alembic/env.py`

**需要修改的内容**:
```python
# 1. 导入 SQLAlchemy 模型
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.base import Base
from models.user import User, UserSettings, APICredit
from models.analysis import Analysis, ErrorDetail, Tag, AnalysisTag, AnalysisCache

# 2. 修改 target_metadata
target_metadata = Base.metadata
```

**检查清单**:
- [ ] 导入所有模型类
- [ ] 设置 `target_metadata = Base.metadata`
- [ ] 配置数据库连接（从 `core.config` 读取）

#### 1.3 配置 alembic.ini

**文件**: `backend/alembic.ini`

**需要修改**:
```ini
# 设置数据库连接 URL
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/english_assistant

# 或使用环境变量
# sqlalchemy.url = ${DATABASE_URL}
```

**检查清单**:
- [ ] 更新 `sqlalchemy.url`
- [ ] 测试连接是否正常

#### 1.4 生成初始迁移脚本

```bash
cd backend
poetry run alembic revision --autogenerate -m "Initial migration"
```

**预期结果**:
- 生成 `alembic/versions/001_initial_migration.py`
- 包含所有表的创建语句
- 包含索引定义

**检查清单**:
- [ ] 检查生成的迁移文件内容
- [ ] 确认所有表都被包含（User, Analysis, ErrorDetail 等）
- [ ] 确认索引和外键约束正确

#### 1.5 测试数据库迁移

```bash
# 启动 PostgreSQL
docker-compose up -d postgres

# 执行迁移
poetry run alembic upgrade head

# 检查数据库
docker exec -it english-assistant-db psql -U postgres -d english_assistant
\dt  # 列出所有表
```

**检查清单**:
- [ ] 迁移成功执行
- [ ] 所有表已创建
- [ ] 测试降级 `alembic downgrade -1`
- [ ] 测试再次升级 `alembic upgrade head`

---

### 任务组 2: 实现认证 API 业务逻辑 (3-4 小时)

**目标**: 完成用户注册、登录、token 刷新功能

#### 2.1 完善 JWT 工具类

**文件**: `backend/core/security.py`

**需要实现的方法**:
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT access token"""

def create_refresh_token(data: dict) -> str:
    """创建 JWT refresh token (7天有效期)"""

def verify_token(token: str, secret: str) -> Optional[TokenPayload]:
    """验证并解析 JWT token"""

def get_current_user(token: str = Depends(HTTPBearer())) -> User:
    """从 token 获取当前用户 (认证依赖)"""

def get_optional_user(token: Optional[str] = None) -> Optional[User]:
    """获取可选用户 (匿名用户返回 None)"""
```

**检查清单**:
- [ ] 实现 `create_access_token()` - 30分钟有效期
- [ ] 实现 `create_refresh_token()` - 7天有效期
- [ ] 实现 `verify_token()` - 处理过期和无效 token
- [ ] 实现 `get_current_user()` - FastAPI 依赖
- [ ] 实现 `get_optional_user()` - 支持匿名访问
- [ ] 添加单元测试

#### 2.2 实现用户注册端点

**文件**: `backend/api/v1/auth.py`

**端点**: `POST /api/v1/auth/register`

**实现内容**:
```python
@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册

    验证:
    - email 格式
    - email 唯一性
    - 密码强度 (可选)

    流程:
    1. 检查 email 是否已存在
    2. 哈希密码
    3. 创建 User 记录
    4. 创建 UserSettings 记录
    5. 生成 access_token 和 refresh_token
    6. 返回用户信息和 token
    """
    # TODO: 实现注册逻辑
```

**检查清单**:
- [ ] 验证 email 唯一性
- [ ] 使用 `password_service.hash_password()` 哈希密码
- [ ] 创建 User 和 UserSettings
- [ ] 生成 JWT tokens
- [ ] 返回符合 `RegisterResponse` 的响应
- [ ] 添加错误处理 (邮箱已存在、无效输入等)

#### 2.3 实现用户登录端点

**文件**: `backend/api/v1/auth.py`

**端点**: `POST /api/v1/auth/login`

**实现内容**:
```python
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录

    流程:
    1. 查询用户 (通过 email)
    2. 验证密码
    3. 检查用户状态 (is_active, is_verified)
    4. 生成 access_token 和 refresh_token
    5. 更新最后登录时间
    6. 返回用户信息和 token
    """
    # TODO: 实现登录逻辑
```

**检查清单**:
- [ ] 查询用户并通过 email 验证
- [ ] 使用 `password_service.verify_password()` 验证密码
- [ ] 检查用户状态
- [ ] 生成 JWT tokens
- [ ] 更新 `last_login_at` 字段
- [ ] 添加错误处理 (用户不存在、密码错误、账户禁用等)

#### 2.4 实现 token 刷新端点

**文件**: `backend/api/v1/auth.py`

**端点**: `POST /api/v1/auth/refresh`

**实现内容**:
```python
@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    刷新 access token

    流程:
    1. 验证 refresh_token
    2. 从 token 获取 user_id
    3. 查询用户是否存在且有效
    4. 生成新的 access_token
    5. 返回新的 access_token
    """
    # TODO: 实现 token 刷新逻辑
```

**检查清单**:
- [ ] 验证 refresh_token 有效性
- [ ] 检查用户是否存在
- [ ] 生成新的 access_token
- [ ] 添加错误处理 (token 过期、用户不存在等)

#### 2.5 集成认证路由到 main.py

**文件**: `backend/main.py`

**需要取消注释**:
```python
from api.v1 import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
```

**检查清单**:
- [ ] 导入 `auth.router`
- [ ] 注册路由到 FastAPI app
- [ ] 访问 http://localhost:8000/docs 确认端点显示
- [ ] 测试所有认证端点

---

### 任务组 3: 实现分析 API 业务逻辑 (4-5 小时)

**目标**: 完成文本分析核心功能

#### 3.1 实现分析端点

**文件**: `backend/api/v1/analysis.py`

**端点**: `POST /api/v1/analyze`

**当前状态**: 骨架已存在，有 21 个 TODO 标记

**需要实现的逻辑**:
```python
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """
    分析和纠正英文文本

    流程:
    1. 验证输入 (文本长度、模式)
    2. 获取用户 (支持匿名访问)
    3. 检查限流配额
    4. 检查缓存 (可选)
    5. 运行 AnalysisPipeline
    6. 保存结果到数据库
    7. 更新用户配额
    8. 返回结果
    """
    # 1. 获取用户 (可选)
    user = None
    if credentials:
        user = await get_current_user(credentials.credentials)

    # 2. 检查限流
    if user:
        rate_limit.check(user.tier)
    else:
        rate_limit.check_anonymous()

    # 3. 运行 Pipeline
    pipeline = AnalysisPipeline()
    result = await pipeline.analyze(
        text=request.text,
        mode=request.mode
    )

    # 4. 保存到数据库
    analysis = Analysis(
        user_id=user.id if user else None,
        original_text=request.text,
        corrected_text=result.corrected_text,
        mode=request.mode,
        # ... 其他字段
    )
    db.add(analysis)
    db.commit()

    # 5. 返回结果
    return AnalyzeResponse(
        original_text=request.text,
        corrected_text=result.corrected_text,
        errors=result.errors,
        # ... 其他字段
    )
```

**检查清单**:
- [ ] 实现可选认证 (匿名用户支持)
- [ ] 集成 `RateLimitService` 检查配额
- [ ] 集成 `AnalysisPipeline` 处理文本
- [ ] 保存 `Analysis` 记录到数据库
- [ ] 保存 `ErrorDetail` 记录到数据库
- [ ] 更新用户配额 (credits_remaining)
- [ ] 返回符合 `AnalyzeResponse` 的响应
- [ ] 添加错误处理 (文本过长、配额不足、Pipeline 失败等)

#### 3.2 集成 AnalysisService

**文件**: `backend/services/analysis_service.py`

**当前状态**: 骨架已存在

**需要完善的方法**:
```python
class AnalysisService:
    async def analyze(
        self,
        request: AnalyzeRequest,
        user: Optional[User],
        db: Session
    ) -> AnalyzeResponse:
        """执行文本分析的完整流程"""

    def _check_quota(self, user: Optional[User]) -> None:
        """检查用户配额"""

    def _save_result(
        self,
        db: Session,
        user: Optional[User],
        result: PipelineResult
    ) -> Analysis:
        """保存分析结果到数据库"""

    def _map_to_response(
        self,
        analysis: Analysis,
        pipeline_result: PipelineResult
    ) -> AnalyzeResponse:
        """映射数据库结果到 API 响应"""
```

**检查清单**:
- [ ] 实现 `analyze()` 方法
- [ ] 实现 `_check_quota()` 方法
- [ ] 实现 `_save_result()` 方法
- [ ] 实现 `_map_to_response()` 方法
- [ ] 添加错误处理和日志

#### 3.3 添加缓存支持 (可选)

**文件**: `backend/services/analysis_service.py`

**实现内容**:
```python
def _get_cache_key(self, text: str, mode: str) -> str:
    """生成缓存键"""
    return f"analysis:{hashlib.md5(f'{text}:{mode}'.encode()).hexdigest()}"

async def _get_cached_result(self, text: str, mode: str) -> Optional[MergedResult]:
    """从缓存获取结果"""
    key = self._get_cache_key(text, mode)
    return self.cache_service.get(key)

async def _cache_result(
    self,
    text: str,
    mode: str,
    result: MergedResult
) -> None:
    """缓存结果"""
    key = self._get_cache_key(text, mode)
    self.cache_service.set(key, result, ttl=86400)  # 24小时
```

**检查清单**:
- [ ] 实现缓存键生成
- [ ] 实现缓存读取
- [ ] 实现缓存写入
- [ ] 测试缓存命中率

#### 3.4 集成分析路由到 main.py

**文件**: `backend/main.py`

**需要取消注释**:
```python
from api.v1 import analysis
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
```

**检查清单**:
- [ ] 导入 `analysis.router`
- [ ] 注册路由到 FastAPI app
- [ ] 访问 http://localhost:8000/docs 确认端点显示
- [ ] 使用 Swagger UI 测试分析端点

---

### 任务组 4: 实现历史记录 API (2-3 小时)

**目标**: 完成历史记录查询功能

#### 4.1 实现历史查询端点

**文件**: `backend/api/v1/history.py`

**端点**: `GET /api/v1/history`

**实现内容**:
```python
@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户分析历史

    分页参数:
    - page: 页码 (从1开始)
    - page_size: 每页数量 (最大100)

    返回:
    - 分析记录列表
    - 总数和分页信息
    """
    # TODO: 实现历史查询逻辑
```

**检查清单**:
- [ ] 实现分页查询
- [ ] 按创建时间倒序排列
- [ ] 应用软删除过滤 (is_deleted=False)
- [ ] 计算总数和分页元数据
- [ ] 返回符合 `HistoryListResponse` 的响应

#### 4.2 实现历史详情端点

**端点**: `GET /api/v1/history/{id}`

**实现内容**:
```python
@router.get("/history/{id}", response_model=HistoryDetailResponse)
async def get_history_detail(
    id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单条分析记录详情

    权限检查:
    - 用户只能查看自己的记录
    """
    # TODO: 实现详情查询逻辑
```

**检查清单**:
- [ ] 查询指定 ID 的分析记录
- [ ] 验证记录属于当前用户
- [ ] 加载关联的 ErrorDetail 记录
- [ ] 返回完整详情

#### 4.3 实现历史删除端点

**端点**: `DELETE /api/v1/history/{id}`

**实现内容**:
```python
@router.delete("/history/{id}", status_code=204)
async def delete_history(
    id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除分析记录 (软删除)

    权限检查:
    - 用户只能删除自己的记录
    """
    # TODO: 实现软删除逻辑
```

**检查清单**:
- [ ] 查询指定 ID 的分析记录
- [ ] 验证记录属于当前用户
- [ ] 执行软删除 (设置 deleted_at, is_deleted=True)
- [ ] 返回 204 状态码

#### 4.4 集成历史路由到 main.py

**文件**: `backend/main.py`

**需要取消注释**:
```python
from api.v1 import history
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
```

**检查清单**:
- [ ] 导入 `history.router`
- [ ] 注册路由到 FastAPI app
- [ ] 测试所有历史端点

---

## 🧪 P1 任务：重要功能

### 任务组 5: 前后端集成测试 (3-4 小时)

**目标**: 验证前后端能够正常协作

#### 5.1 测试认证流程

**测试步骤**:
1. 启动后端服务
   ```bash
   cd backend
   poetry run uvicorn main:app --reload --port 8000
   ```

2. 启动前端服务
   ```bash
   cd frontend
   npm run dev
   ```

3. 测试注册流程
   - 访问 http://localhost:5173/auth
   - 填写注册表单
   - 提交并验证响应
   - 检查是否跳转到首页

4. 测试登录流程
   - 使用已注册的账号登录
   - 验证 token 存储
   - 检查用户信息显示

5. 测试 token 刷新
   - 等待 access token 过期
   - 执行需要认证的操作
   - 验证自动刷新机制

**检查清单**:
- [ ] 注册功能正常
- [ ] 登录功能正常
- [ ] Token 自动刷新正常
- [ ] 认证状态持久化正常
- [ ] 路由守卫正常工作

#### 5.2 测试文本分析流程

**测试步骤**:
1. 登录系统

2. 输入测试文本
   ```
   I go to park yesterday. The weather was beautiful.
   ```

3. 选择 "准确性优先" 模式

4. 点击 "分析文本" 按钮

5. 验证结果
   - 显示纠正后文本
   - 显示错误卡片
   - 错误高亮正确
   - 错误详情准确

6. 测试不同的输入
   - 短文本 (< 100 词)
   - 长文本 (500+ 词)
   - 包含中英混合
   - 包含对话格式

**检查清单**:
- [ ] 分析请求成功
- [ ] 结果正确显示
- [ ] 错误高亮准确
- [ ] 错误卡片展开/折叠正常
- [ ] 进度指示器正常
- [ ] 错误提示正常

#### 5.3 测试历史记录功能

**测试步骤**:
1. 执行多次文本分析

2. 访问历史记录页面

3. 验证列表显示
   - 分页正常
   - 时间顺序正确
   - 记录完整

4. 点击查看详情
   - 详情页面正常
   - 所有信息显示

5. 测试删除功能
   - 删除一条记录
   - 验证列表更新

**检查清单**:
- [ ] 历史列表正常显示
- [ ] 分页功能正常
- [ ] 详情查看正常
- [ ] 删除功能正常
- [ ] 权限控制正常

#### 5.4 修复集成问题

**常见问题**:
- CORS 错误
- Token 格式不匹配
- 响应数据结构不一致
- 错误处理不当
- 状态管理问题

**检查清单**:
- [ ] 记录所有发现的问题
- [ ] 按优先级修复
- [ ] 回归测试
- [ ] 更新文档

---

### 任务组 6: 完善错误处理 (2-3 小时)

**目标**: 统一和优化错误处理

#### 6.1 统一后端错误码

**文件**: `backend/core/exceptions.py` (需创建)

**定义错误类**:
```python
class EnglishAssistantException(Exception):
    """基础异常类"""

class ValidationError(EnglishAssistantException):
    """验证错误 - 400"""

class AuthenticationError(EnglishAssistantException):
    """认证错误 - 401"""

class AuthorizationError(EnglishAssistantException):
    """授权错误 - 403"""

class NotFoundError(EnglishAssistantException):
    """资源未找到 - 404"""

class RateLimitError(EnglishAssistantException):
    """限流错误 - 429"""

class AnalysisError(EnglishAssistantException):
    """分析失败 - 500"""

class LLMError(EnglishAssistantException):
    """LLM 服务错误 - 500"""
```

**检查清单**:
- [ ] 创建 `core/exceptions.py`
- [ ] 定义所有异常类
- [ ] 添加错误码枚举
- [ ] 编写错误消息模板

#### 6.2 添加全局异常处理器

**文件**: `backend/main.py`

**实现内容**:
```python
from fastapi.responses import JSONResponse
from core.exceptions import *

@app.exception_handler(EnglishAssistantException)
async def custom_exception_handler(request: Request, exc: EnglishAssistantException):
    """全局自定义异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": str(exc),
                "details": exc.details if hasattr(exc, 'details') else None
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 验证错误处理器"""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数验证失败",
                "details": exc.errors()
            }
        }
    )
```

**检查清单**:
- [ ] 实现全局异常处理器
- [ ] 处理 Pydantic 验证错误
- [ ] 处理自定义业务错误
- [ ] 添加日志记录
- [ ] 测试各种错误场景

#### 6.3 完善前端错误提示

**文件**: `frontend/src/stores/uiStore.ts`

**改进内容**:
```typescript
interface ErrorMessage {
  title: string
  message: string
  type: 'error' | 'warning' | 'info'
  duration?: number
}

function showError(error: any, context?: string) {
  // 根据 HTTP 状态码显示不同提示
  if (error.response) {
    const { status, data } = error.response
    switch (status) {
      case 400:
        toast.add({
          title: '请求错误',
          message: data.error?.message || '请检查输入参数',
          type: 'error'
        })
        break
      case 401:
        toast.add({
          title: '未授权',
          message: '请先登录',
          type: 'warning'
        })
        // 跳转到登录页
        router.push('/auth')
        break
      case 429:
        toast.add({
          title: '请求过多',
          message: data.error?.message || '请稍后再试',
          type: 'warning'
        })
        break
      case 500:
        toast.add({
          title: '服务器错误',
          message: '服务暂时不可用，请稍后重试',
          type: 'error'
        })
        break
      default:
        toast.add({
          title: '未知错误',
          message: data.error?.message || '发生未知错误',
          type: 'error'
        })
    }
  } else if (error.request) {
    // 网络错误
    toast.add({
      title: '网络错误',
      message: '请检查网络连接',
      type: 'error'
    })
  } else {
    // 其他错误
    toast.add({
      title: '错误',
      message: error.message,
      type: 'error'
    })
  }
}
```

**检查清单**:
- [ ] 实现统一错误处理函数
- [ ] 根据状态码显示不同提示
- [ ] 处理网络错误
- [ ] 添加错误日志记录
- [ ] 测试各种错误场景

---

## 📝 P2 任务：测试和文档

### 任务组 7: 编写核心功能测试 (4-5 小时)

#### 7.1 Pipeline 单元测试

**文件**: `backend/tests/test_pipeline.py`

**测试用例**:
```python
@pytest.mark.unit
async def test_preprocessor():
    """测试预处理器"""
    preprocessor = Preprocessor()
    result = preprocessor.preprocess("Hello. World!")
    assert len(result.messages) == 2

@pytest.mark.unit
async def test_rule_engine():
    """测试规则引擎"""
    engine = RuleEngine()
    errors = engine.check("I go to park yesterday.")
    assert len(errors) > 0
    assert errors[0].type == "tense"

@pytest.mark.unit
async def test_merger():
    """测试结果合并"""
    merger = Merger()
    result = merger.merge(rule_errors, llm_result)
    assert result.corrected_text is not None
```

**检查清单**:
- [ ] 测试 Preprocessor
- [ ] 测试 RuleEngine
- [ ] 测试 LLMEngine (mock)
- [ ] 测试 Merger
- [ ] 测试完整 Pipeline

#### 7.2 API 集成测试

**文件**: `backend/tests/test_api_endpoints.py`

**测试用例**:
```python
@pytest.mark.integration
async def test_register(client):
    """测试用户注册"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "username": "testuser"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

@pytest.mark.integration
async def test_login(client, test_user):
    """测试用户登录"""
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.integration
async def test_analyze(client, auth_headers):
    """测试文本分析"""
    response = await client.post("/api/v1/analyze", json={
        "text": "I go to park yesterday.",
        "mode": "accuracy"
    }, headers=auth_headers)
    assert response.status_code == 200
    assert "corrected_text" in response.json()
```

**检查清单**:
- [ ] 测试注册端点
- [ ] 测试登录端点
- [ ] 测试刷新端点
- [ ] 测试分析端点
- [ ] 测试历史查询端点
- [ ] 测试认证和授权

#### 7.3 运行测试套件

```bash
cd backend

# 运行所有测试
poetry run pytest

# 运行单元测试
poetry run pytest -m unit

# 运行集成测试
poetry run pytest -m integration

# 生成覆盖率报告
poetry run pytest --cov=backend --cov-report=html
```

**检查清单**:
- [ ] 所有测试通过
- [ ] 代码覆盖率 > 70%
- [ ] 修复失败的测试
- [ ] 生成覆盖率报告

---

## 📊 进度跟踪

### 完成标准

**P0 任务完成标准**:
- [ ] Alembic 配置完成，迁移脚本可正常运行
- [ ] 认证 API 完整实现并测试通过
- [ ] 分析 API 完整实现并测试通过
- [ ] 历史记录 API 完整实现并测试通过
- [ ] 前后端集成测试通过

**P1 任务完成标准**:
- [ ] 错误处理统一完善
- [ ] 核心功能单元测试覆盖率 > 70%
- [ ] 集成测试通过

### 下一步行动

**立即开始**:
1. 配置 Alembic 数据库迁移 (任务组 1)
2. 实现认证 API (任务组 2)
3. 实现分析 API (任务组 3)

**本周完成**:
- 历史记录 API (任务组 4)
- 前后端集成测试 (任务组 5)
- 错误处理完善 (任务组 6)

**下周计划**:
- 编写测试 (任务组 7)
- 性能优化
- 部署准备

---

## 🔗 相关文档

- [CLAUDE.md](../../CLAUDE.md) - AI 开发指南
- [AGENTS.md](../../AGENTS.md) - 开发规范
- [implementation-checklist.md](./implementation-checklist.md) - 完整实施清单
- [architecture.md](../04-technical-design/architecture.md) - 系统架构
- [scripts/README.md](../../scripts/README.md) - 脚本文档

---

**最后更新**: 2026-01-27
**维护者**: English Transfer Assistant Team
**版本**: v1.0
