# LLM Multi-Provider Configuration System - Design Document

**Date:** 2026-02-03
**Status:** Approved
**Estimated Implementation Time:** 11 hours

---

## Overview

Add support for multiple LLM providers (Zhipu AI, OpenAI, Anthropic) with user-configurable API keys and model selection, while maintaining system-provided default keys.

## Requirements

### Functional Requirements

1. **AI Key Management**
   - System provides default API keys for all providers
   - Users can optionally add their own API keys
   - User keys override system defaults
   - Keys stored encrypted in database

2. **Supported Providers**
   - **Zhipu AI:** GLM-4-FlashX (default), GLM-4-Flash, GLM-4-Plus, GLM-4-Air
   - **OpenAI:** GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
   - **Anthropic:** Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku

3. **Configuration Method**
   - Settings only - persistent user preference
   - All analyses use user's configured provider + model
   - Default: GLM-4-FlashX

### Non-Functional Requirements

- **Security:** All API keys encrypted at rest using Fernet
- **Performance:** GLM-4-FlashX for faster processing (<10s target)
- **Reliability:** Graceful degradation to LanguageTool-only on provider failures
- **Auditability:** Track all config changes and provider usage

---

## Architecture

### Database Schema

#### 1. New Table: `ea_llm_providers`

System-level configuration for supported LLM providers.

```sql
CREATE TABLE ea_llm_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    default_api_key_encrypted TEXT NOT NULL,
    supported_models JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Supported models format:
-- [
--   {"name": "glm-4-flashx", "display_name": "GLM-4-FlashX", "is_default": true},
--   {"name": "glm-4-flash", "display_name": "GLM-4-Flash", "is_default": false}
-- ]
```

#### 2. New Table: `ea_user_llm_configs`

User-specific LLM configurations and custom API keys.

```sql
CREATE TABLE ea_user_llm_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES ea_users(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL,
    selected_model VARCHAR(100) NOT NULL,
    custom_api_key_encrypted TEXT,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider_name)
);

CREATE INDEX idx_user_llm_configs_user_provider ON ea_user_llm_configs(user_id, provider_name);
CREATE INDEX idx_user_llm_configs_active ON ea_user_llm_configs(user_id, is_active);
```

#### 3. Update Table: `ea_user_settings`

Add LLM preference fields.

```sql
ALTER TABLE ea_user_settings
ADD COLUMN active_llm_provider VARCHAR(50) DEFAULT 'zhipu',
ADD COLUMN active_llm_model VARCHAR(100) DEFAULT 'glm-4-flashx';
```

### Provider Abstraction Layer

#### Base Provider Interface

```python
# services/llm/base_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def analyze_text(
        self,
        text: str,
        mode: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze text and return corrections.

        Args:
            text: Input text to analyze
            mode: Analysis mode ('accuracy' or 'natural')
            context: Additional context (preprocessed data, etc.)

        Returns:
            {
                "corrected_text": str,
                "suggestions": List[Dict],
                "token_usage": {"input": int, "output": int, "total": int},
                "processing_time_ms": int
            }
        """
        pass

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Return list of supported models for this provider"""
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD based on token usage"""
        pass
```

#### Provider Implementations

**ZhipuProvider** (services/llm/zhipu_provider.py)
- Wraps existing zhipuai SDK integration
- Models: glm-4-flashx, glm-4-flash, glm-4-plus, glm-4-air
- Pricing: ~$0.0001 per 1K tokens (GLM-4-FlashX)

**OpenAIProvider** (services/llm/openai_provider.py)
- Uses openai Python SDK
- Models: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- Pricing: $0.01-0.03 per 1K tokens

**AnthropicProvider** (services/llm/anthropic_provider.py)
- Uses anthropic Python SDK
- Models: claude-3-opus, claude-3-sonnet, claude-3-haiku
- Pricing: $0.015-0.075 per 1K tokens

#### Provider Factory

```python
# services/llm/provider_factory.py
class LLMProviderFactory:
    """Factory to create appropriate LLM provider instance"""

    _providers = {
        "zhipu": ZhipuProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider
    }

    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: str,
        model: str
    ) -> BaseLLMProvider:
        """
        Create and return provider instance.

        Raises:
            ValueError: If provider_name not supported
        """
        if provider_name not in LLMProviderFactory._providers:
            raise ValueError(f"Unsupported provider: {provider_name}")

        return LLMProviderFactory._providers[provider_name](api_key, model)

    @staticmethod
    def get_supported_providers() -> List[str]:
        """Return list of supported provider names"""
        return list(LLMProviderFactory._providers.keys())
```

### API Endpoints

#### 1. GET `/api/v1/llm/providers`

List all available LLM providers and their models.

**Response:**
```json
{
  "providers": [
    {
      "name": "zhipu",
      "display_name": "Zhipu AI",
      "is_enabled": true,
      "models": [
        {
          "name": "glm-4-flashx",
          "display_name": "GLM-4-FlashX",
          "is_default": true,
          "description": "Fastest model, optimized for speed"
        },
        {
          "name": "glm-4-flash",
          "display_name": "GLM-4-Flash",
          "is_default": false,
          "description": "Balanced speed and quality"
        },
        {
          "name": "glm-4-plus",
          "display_name": "GLM-4-Plus",
          "is_default": false,
          "description": "Higher quality, slower processing"
        },
        {
          "name": "glm-4-air",
          "display_name": "GLM-4-Air",
          "is_default": false,
          "description": "Lightweight, most cost-effective"
        }
      ]
    },
    {
      "name": "openai",
      "display_name": "OpenAI",
      "is_enabled": true,
      "models": [
        {"name": "gpt-4", "display_name": "GPT-4", "is_default": true},
        {"name": "gpt-4-turbo", "display_name": "GPT-4 Turbo"},
        {"name": "gpt-3.5-turbo", "display_name": "GPT-3.5 Turbo"}
      ]
    },
    {
      "name": "anthropic",
      "display_name": "Anthropic",
      "is_enabled": true,
      "models": [
        {"name": "claude-3-opus", "display_name": "Claude 3 Opus"},
        {"name": "claude-3-sonnet", "display_name": "Claude 3 Sonnet", "is_default": true},
        {"name": "claude-3-haiku", "display_name": "Claude 3 Haiku"}
      ]
    }
  ]
}
```

#### 2. GET `/api/v1/llm/config`

Get user's current LLM configuration.

**Authentication:** Required

**Response:**
```json
{
  "active_provider": "zhipu",
  "active_model": "glm-4-flashx",
  "has_custom_key": false,
  "using_system_default": true,
  "provider_display_name": "Zhipu AI",
  "model_display_name": "GLM-4-FlashX"
}
```

#### 3. PUT `/api/v1/llm/config`

Update user's LLM configuration.

**Authentication:** Required

**Request:**
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "api_key": "sk-..." // Optional - omit to use system default
}
```

**Response:**
```json
{
  "active_provider": "openai",
  "active_model": "gpt-4",
  "has_custom_key": true,
  "using_system_default": false
}
```

**Validation:**
- Provider must be in supported list
- Model must be valid for selected provider
- API key tested before saving (make test API call)

#### 4. DELETE `/api/v1/llm/config/api-key`

Remove user's custom API key (fall back to system default).

**Authentication:** Required

**Response:**
```json
{
  "message": "Custom API key removed. Using system default.",
  "active_provider": "openai",
  "active_model": "gpt-4",
  "has_custom_key": false,
  "using_system_default": true
}
```

### Service Layer

#### LLMConfigService

```python
# services/llm_config_service.py
class LLMConfigService:
    """Manages LLM provider configurations and API keys"""

    def __init__(self, db: Session):
        self.db = db
        self.encryptor = self._init_encryptor()

    def get_user_config(self, user_id: str) -> Dict[str, Any]:
        """Get user's active LLM configuration"""

    def update_user_config(
        self,
        user_id: str,
        provider: str,
        model: str,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user's LLM configuration with validation"""

    def get_api_key_for_user(self, user_id: str, provider: str) -> str:
        """
        Get API key for user and provider.
        Returns user's custom key if set, otherwise system default.
        """

    def remove_custom_key(self, user_id: str, provider: str) -> None:
        """Remove user's custom API key"""

    def get_system_providers(self) -> List[Dict[str, Any]]:
        """Get all system-configured providers"""

    def encrypt_api_key(self, key: str) -> str:
        """Encrypt API key for storage"""

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""

    async def validate_api_key(
        self,
        provider: str,
        model: str,
        api_key: str
    ) -> bool:
        """Test API key by making a small test request"""
```

### Data Flow

#### Analysis Request Flow

```
1. User Request → POST /api/v1/analyze
   {
     "text": "She dont like pizza",
     "mode": "accuracy"
   }

2. AnalysisEndpoint
   ├─ Authenticate user → Get user_id
   ├─ Check rate limits
   └─ Call AnalysisService.analyze()

3. AnalysisService.analyze()
   ├─ LLMConfigService.get_user_config(user_id)
   │  ├─ Query ea_user_settings.active_llm_provider
   │  ├─ Query ea_user_settings.active_llm_model
   │  └─ LLMConfigService.get_api_key_for_user(user_id, provider)
   │     ├─ Check ea_user_llm_configs for custom key
   │     └─ Fall back to ea_llm_providers.default_api_key_encrypted
   │
   ├─ LLMProviderFactory.create_provider(provider, api_key, model)
   │  └─ Return ZhipuProvider | OpenAIProvider | AnthropicProvider
   │
   └─ AnalysisPipeline.analyze(text, mode, llm_provider)

4. AnalysisPipeline (Modified)
   ├─ Stage 1: Preprocessing
   ├─ Stage 2: Rule-based (LanguageTool)
   ├─ Stage 3: LLM Optimization
   │  ├─ Use injected llm_provider instead of hardcoded Zhipu
   │  ├─ llm_provider.analyze_text(text, mode, context)
   │  └─ Track token usage & cost per provider
   └─ Stage 4: Merge results

5. Response
   {
     "analysis_id": "...",
     "corrected_text": "She doesn't like pizza",
     "errors": [...],
     "statistics": {...},
     "llm_metadata": {
       "provider": "zhipu",
       "model": "glm-4-flashx",
       "processing_time_ms": 8500,
       "token_usage": {"input": 10, "output": 12, "total": 22},
       "estimated_cost": 0.0000022
     }
   }
```

#### API Key Resolution Logic

```python
def get_api_key_for_user(user_id: str, provider: str) -> str:
    """Resolve which API key to use for this user and provider"""

    # 1. Try to get user's custom key
    user_config = db.query(UserLLMConfig).filter(
        UserLLMConfig.user_id == user_id,
        UserLLMConfig.provider_name == provider
    ).first()

    if user_config and user_config.custom_api_key_encrypted:
        return decrypt_api_key(user_config.custom_api_key_encrypted)

    # 2. Fall back to system default
    system_provider = db.query(LLMProvider).filter(
        LLMProvider.name == provider,
        LLMProvider.is_enabled == True
    ).first()

    if not system_provider:
        raise ValueError(f"Provider {provider} not available")

    return decrypt_api_key(system_provider.default_api_key_encrypted)
```

### Error Handling

#### Provider-Specific Errors

**Invalid API Key:**
```json
{
  "error": "INVALID_API_KEY",
  "message": "Your API key for OpenAI is invalid. Please update it in settings.",
  "provider": "openai",
  "status_code": 401
}
```

**Model Not Available:**
```json
{
  "error": "MODEL_NOT_AVAILABLE",
  "message": "Model gpt-5 is not available. Falling back to gpt-4.",
  "provider": "openai",
  "fallback_model": "gpt-4",
  "status_code": 200
}
```

**Provider Rate Limit:**
```json
{
  "error": "PROVIDER_RATE_LIMIT",
  "message": "OpenAI rate limit exceeded. Try again in 60 seconds.",
  "provider": "openai",
  "retry_after": 60,
  "status_code": 429
}
```

**Provider Timeout:**
```json
{
  "error": "PROVIDER_TIMEOUT",
  "message": "OpenAI request timed out. Results based on LanguageTool only.",
  "provider": "openai",
  "degraded_mode": true,
  "status_code": 200
}
```

#### Graceful Degradation Strategy

```
Attempt 1: Use user's selected provider with configured key
├─ Success → Return full results
└─ Failure → Check error type
     ├─ User has custom key → Return error (don't hide user's broken key)
     └─ Using system default → Try fallback

Attempt 2: Try system default key (if different from attempt 1)
├─ Success → Return results with warning
└─ Failure → Degraded mode

Degraded Mode: LanguageTool only
├─ Run rule-based correction only
├─ Set llm_metadata.provider = "none"
└─ Add warning in response
```

### Security

#### API Key Encryption

**Algorithm:** Fernet (symmetric encryption)
- AES 128-bit encryption in CBC mode
- HMAC using SHA256 for authentication
- Keys are base64 url-safe encoded

**Implementation:**
```python
from cryptography.fernet import Fernet
import base64
import os

class APIKeyEncryptor:
    def __init__(self):
        # Get encryption key from environment
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return self.cipher.encrypt(api_key.encode()).decode()

    def decrypt(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

**Key Generation:**
```python
# Generate new encryption key (run once, store in .env)
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Add to .env as ENCRYPTION_KEY
```

#### Access Control

**User Permissions:**
- ✅ Users can read their own LLM configs
- ✅ Users can update their own LLM configs
- ✅ Users can delete their own custom API keys
- ❌ Users cannot see other users' configs
- ❌ Users cannot see actual API keys (only `has_custom_key` boolean)
- ❌ Users cannot modify system default keys

**Admin Permissions:**
- ✅ Admins can manage system provider configs
- ✅ Admins can update system default API keys
- ✅ Admins can enable/disable providers
- ✅ Admins can view aggregated usage statistics per provider

#### Security Best Practices

1. **Never Log API Keys**
   - Exclude from all log statements
   - Redact in error messages
   - Mask in admin UI (show last 4 chars only)

2. **API Key Validation**
   - Test key before storing (make small test request)
   - Invalidate cached keys on 401 errors
   - Prompt user to update on repeated failures

3. **Rate Limiting**
   - Track usage per provider separately
   - Different limits for different providers
   - Prevent API key abuse

4. **Audit Trail**
   ```sql
   CREATE TABLE ea_llm_config_audit (
       id UUID PRIMARY KEY,
       user_id UUID NOT NULL,
       action VARCHAR(50), -- 'UPDATE_PROVIDER', 'ADD_KEY', 'REMOVE_KEY'
       provider VARCHAR(50),
       ip_address VARCHAR(45),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### Performance Optimization

#### GLM-4-FlashX Performance Target

**Current (GLM-4-Flash):** ~14.6 seconds average
**Target (GLM-4-FlashX):** <10 seconds average

**Optimizations:**
1. **Parallel Processing**
   - Run LanguageTool and LLM in parallel (don't wait for sequential completion)
   - Reduces total time by ~30%

2. **Caching**
   - Cache LLM results by text hash for 24 hours
   - Check cache before making API call
   - Estimated 40% cache hit rate

3. **Request Batching**
   - For multiple sentences, batch into single LLM request
   - Reduces API roundtrip overhead

4. **Connection Pooling**
   - Reuse HTTP connections to provider APIs
   - Reduces connection establishment time

#### Token Usage Optimization

**Current Issue:** Sending entire text to LLM
**Optimization:** Send only error-prone sections

```python
def optimize_llm_input(text: str, rule_errors: List[Error]) -> str:
    """
    Send only sentences with errors to LLM.
    For texts with few errors, reduces token usage by 60-80%.
    """
    if len(rule_errors) == 0:
        return ""  # Skip LLM entirely

    # Extract sentences containing errors
    error_sentences = extract_sentences_with_errors(text, rule_errors)
    return "\n".join(error_sentences)
```

### Testing Strategy

#### Unit Tests

```python
# tests/llm/test_providers.py
def test_zhipu_provider_initialization():
    provider = ZhipuProvider(api_key="test-key", model="glm-4-flashx")
    assert provider.model == "glm-4-flashx"

def test_zhipu_provider_analyze_text():
    provider = ZhipuProvider(api_key=REAL_KEY, model="glm-4-flashx")
    result = await provider.analyze_text("She dont like it", "accuracy", {})
    assert "corrected_text" in result
    assert result["token_usage"]["total"] > 0

def test_provider_factory_creates_correct_provider():
    provider = LLMProviderFactory.create_provider("zhipu", "key", "glm-4-flashx")
    assert isinstance(provider, ZhipuProvider)

def test_api_key_encryption_decryption():
    encryptor = APIKeyEncryptor()
    original = "sk-test-key-12345"
    encrypted = encryptor.encrypt(original)
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == original
    assert encrypted != original

# tests/llm/test_config_service.py
def test_get_user_config_returns_defaults():
    config = llm_config_service.get_user_config(user_id)
    assert config["active_provider"] == "zhipu"
    assert config["active_model"] == "glm-4-flashx"
    assert config["using_system_default"] is True

def test_update_user_config_saves_encrypted_key():
    llm_config_service.update_user_config(
        user_id, "openai", "gpt-4", "sk-test-key"
    )
    # Verify key is encrypted in database
    config = db.query(UserLLMConfig).filter_by(user_id=user_id).first()
    assert config.custom_api_key_encrypted != "sk-test-key"
    assert config.custom_api_key_encrypted.startswith("gAAAAA")  # Fernet format

def test_delete_custom_key_falls_back_to_system():
    llm_config_service.remove_custom_key(user_id, "openai")
    api_key = llm_config_service.get_api_key_for_user(user_id, "openai")
    # Should return system default, not user's key
    assert api_key == SYSTEM_DEFAULT_OPENAI_KEY
```

#### Integration Tests

```python
# tests/integration/test_analysis_with_providers.py
@pytest.mark.integration
async def test_analysis_with_zhipu_flashx():
    response = await analyze_text(
        text="She dont like pizza",
        mode="accuracy",
        user_id=test_user_id
    )
    assert response["llm_metadata"]["provider"] == "zhipu"
    assert response["llm_metadata"]["model"] == "glm-4-flashx"
    assert response["llm_metadata"]["processing_time_ms"] < 10000

@pytest.mark.integration
async def test_analysis_with_custom_openai_key():
    # Set user's custom OpenAI key
    llm_config_service.update_user_config(
        test_user_id, "openai", "gpt-4", CUSTOM_OPENAI_KEY
    )

    response = await analyze_text(
        text="She dont like pizza",
        mode="accuracy",
        user_id=test_user_id
    )
    assert response["llm_metadata"]["provider"] == "openai"
    assert response["llm_metadata"]["model"] == "gpt-4"

@pytest.mark.integration
async def test_graceful_degradation_on_provider_failure():
    # Use invalid API key to trigger failure
    llm_config_service.update_user_config(
        test_user_id, "openai", "gpt-4", "invalid-key"
    )

    response = await analyze_text(
        text="She dont like pizza",
        mode="accuracy",
        user_id=test_user_id
    )
    # Should fall back to LanguageTool only
    assert response["llm_metadata"]["provider"] == "none"
    assert response["llm_metadata"]["degraded_mode"] is True
    assert len(response["errors"]) > 0  # Still has rule-based errors
```

#### Performance Tests

```python
# tests/performance/test_provider_speed.py
@pytest.mark.performance
async def test_glm_4_flashx_faster_than_flash():
    text = "She dont like pizza and he dont eat vegetables neither."

    # Test GLM-4-Flash
    start = time.time()
    result_flash = await analyze_with_provider("zhipu", "glm-4-flash", text)
    time_flash = time.time() - start

    # Test GLM-4-FlashX
    start = time.time()
    result_flashx = await analyze_with_provider("zhipu", "glm-4-flashx", text)
    time_flashx = time.time() - start

    # FlashX should be at least 30% faster
    assert time_flashx < time_flash * 0.7
    assert time_flashx < 10.0  # Under 10 seconds target

@pytest.mark.performance
async def test_concurrent_requests_with_different_providers():
    """Test that different providers can handle concurrent requests"""
    tasks = [
        analyze_with_provider("zhipu", "glm-4-flashx", "Text 1"),
        analyze_with_provider("openai", "gpt-4", "Text 2"),
        analyze_with_provider("anthropic", "claude-3-sonnet", "Text 3"),
    ]

    start = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start

    # Concurrent execution should be faster than sequential
    assert all(r is not None for r in results)
    assert total_time < 30.0  # All three complete in <30s
```

---

## Implementation Plan

### Phase 1: Database & Models (2 hours)

**Tasks:**
1. Create migration for `ea_llm_providers` table
2. Create migration for `ea_user_llm_configs` table
3. Update `ea_user_settings` with LLM fields
4. Create SQLAlchemy models:
   - `LLMProvider` (models/llm_provider.py)
   - `UserLLMConfig` (models/user_llm_config.py)
   - Update `UserSettings` model
5. Seed initial data for system providers

**Files:**
- `alembic/versions/xxxx_add_llm_provider_tables.py`
- `backend/models/llm_provider.py`
- `backend/models/user_llm_config.py`
- `backend/models/user.py` (update UserSettings)
- `backend/scripts/seed_llm_providers.py`

### Phase 2: Provider Abstraction (3 hours)

**Tasks:**
1. Create base provider interface
2. Refactor existing Zhipu integration into ZhipuProvider
3. Implement OpenAIProvider
4. Implement AnthropicProvider
5. Create ProviderFactory
6. Add provider-specific error handling

**Files:**
- `backend/services/llm/base_provider.py`
- `backend/services/llm/zhipu_provider.py`
- `backend/services/llm/openai_provider.py`
- `backend/services/llm/anthropic_provider.py`
- `backend/services/llm/provider_factory.py`
- `backend/services/llm/__init__.py`

**Dependencies:**
```toml
# pyproject.toml
openai = "^1.10.0"
anthropic = "^0.18.0"
```

### Phase 3: Config Service & Encryption (2 hours)

**Tasks:**
1. Create API key encryption utilities
2. Implement LLMConfigService
3. Add system provider seeding script
4. Create config validation logic
5. Add audit logging

**Files:**
- `backend/core/encryption.py`
- `backend/services/llm_config_service.py`
- `backend/scripts/seed_llm_providers.py`
- Update `.env.example` with ENCRYPTION_KEY

**Environment:**
```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Phase 4: API Endpoints (2 hours)

**Tasks:**
1. Create LLM config router (api/v1/llm.py)
2. Implement GET /llm/providers endpoint
3. Implement GET /llm/config endpoint
4. Implement PUT /llm/config endpoint
5. Implement DELETE /llm/config/api-key endpoint
6. Register router in main.py
7. Update analyze endpoint to use new provider system

**Files:**
- `backend/api/v1/llm.py`
- `backend/schemas/llm.py`
- `backend/main.py` (register router)
- `backend/api/v1/analysis.py` (update)
- `backend/services/analysis_service.py` (update)

### Phase 5: Testing (2 hours)

**Tasks:**
1. Write unit tests for providers
2. Write unit tests for config service
3. Write integration tests for analysis with different providers
4. Write performance tests for GLM-4-FlashX
5. Test graceful degradation scenarios

**Files:**
- `tests/llm/test_providers.py`
- `tests/llm/test_config_service.py`
- `tests/integration/test_analysis_providers.py`
- `tests/performance/test_provider_speed.py`

---

## Migration & Rollout

### Database Migration Steps

1. **Backup current database**
   ```bash
   pg_dump -h 110.40.137.26 -U english_assistant db_english_assistant > backup.sql
   ```

2. **Run migrations**
   ```bash
   poetry run alembic upgrade head
   ```

3. **Seed system providers**
   ```bash
   poetry run python scripts/seed_llm_providers.py
   ```

4. **Verify data**
   ```sql
   SELECT * FROM ea_llm_providers;
   SELECT * FROM ea_user_settings LIMIT 10;
   ```

### Rollout Strategy

**Phase 1: Internal Testing (Day 1)**
- Deploy to staging environment
- Test all three providers with real API keys
- Verify encryption/decryption works
- Test graceful degradation

**Phase 2: Beta Release (Day 2-3)**
- Enable for 10% of users (tier = 'pro')
- Monitor error rates and performance
- Collect feedback on model selection

**Phase 3: Full Release (Day 4)**
- Enable for all users
- Announce new features
- Monitor provider usage distribution

### Monitoring

**Metrics to Track:**
- Provider usage distribution (% using each provider)
- Average processing time per provider
- Error rates per provider
- Token usage and costs per provider
- Custom API key adoption rate

**Alerts:**
- Provider error rate > 5%
- Processing time > 15 seconds (95th percentile)
- System default API key usage > 80% (indicates low custom key adoption)

---

## Risks & Mitigations

### Risk 1: API Key Security Breach

**Impact:** High - Compromised keys could lead to unauthorized API usage and costs

**Mitigation:**
- Encrypt all keys at rest using Fernet
- Store encryption key in environment variable (never in code)
- Implement key rotation mechanism
- Monitor for unusual API usage patterns
- Set spending limits on all provider accounts

### Risk 2: Provider Service Outages

**Impact:** Medium - Users can't analyze text if provider is down

**Mitigation:**
- Graceful degradation to LanguageTool-only mode
- Allow users to configure multiple providers as fallbacks
- Cache recent results for 24 hours
- Monitor provider status pages

### Risk 3: Cost Overruns from User Keys

**Impact:** Low - Users bear their own costs

**Mitigation:**
- Provide cost estimates before analysis
- Show token usage in response
- Warn users when switching to expensive providers (OpenAI GPT-4)
- Recommend GLM-4-FlashX for best price/performance

### Risk 4: Performance Regression

**Impact:** Medium - GLM-4-FlashX might not be faster than expected

**Mitigation:**
- Benchmark before and after
- Implement parallel processing (LanguageTool + LLM)
- Optimize prompts for faster responses
- Cache aggressively

---

## Success Metrics

### Performance Targets

- ✅ Analysis processing time: <10 seconds (95th percentile) with GLM-4-FlashX
- ✅ Provider API error rate: <2%
- ✅ Custom API key adoption: >30% of pro users within 30 days
- ✅ Graceful degradation success rate: >95% (fallback works when provider fails)

### User Adoption Targets

- 60% of users stick with default (Zhipu GLM-4-FlashX)
- 25% of pro users add custom API keys
- 15% of users switch to OpenAI or Anthropic

### Cost Targets

- Average cost per analysis: <$0.01 (using system defaults)
- User-provided keys cover 30% of LLM costs within 60 days

---

## Future Enhancements

### Phase 2 Features (Post-MVP)

1. **Provider Analytics Dashboard**
   - Show user their usage by provider
   - Cost breakdown over time
   - Performance comparison charts

2. **Auto-Provider Selection**
   - AI selects best provider based on text type
   - Business writing → Claude
   - Casual text → GLM-4-FlashX
   - Technical writing → GPT-4

3. **Provider Fallback Chain**
   - User configures: Primary → Secondary → Tertiary
   - Auto-fallback on errors

4. **Batch Analysis Optimization**
   - Analyze multiple texts in one request
   - Bulk discounts from providers

5. **Custom Model Fine-tuning**
   - Allow users to upload fine-tuned models
   - Support for custom endpoints

---

## Appendix

### Provider Comparison

| Provider | Models | Avg Speed | Cost (per 1K tokens) | Quality |
|----------|--------|-----------|----------------------|---------|
| **Zhipu AI** | GLM-4-FlashX | 8s | $0.0001 | Good |
| Zhipu AI | GLM-4-Flash | 12s | $0.0002 | Good |
| Zhipu AI | GLM-4-Plus | 18s | $0.0005 | Excellent |
| OpenAI | GPT-3.5-Turbo | 5s | $0.001 | Good |
| OpenAI | GPT-4-Turbo | 10s | $0.01 | Excellent |
| OpenAI | GPT-4 | 15s | $0.03 | Excellent |
| Anthropic | Claude-3-Haiku | 6s | $0.00025 | Good |
| Anthropic | Claude-3-Sonnet | 12s | $0.003 | Excellent |
| Anthropic | Claude-3-Opus | 20s | $0.015 | Outstanding |

**Recommendation:** GLM-4-FlashX for best balance of speed and cost.

### Environment Variables

```bash
# .env additions

# Encryption key for API keys (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-32-byte-base64-key-here

# System default API keys (encrypted)
SYSTEM_ZHIPU_API_KEY=your-zhipu-key
SYSTEM_OPENAI_API_KEY=your-openai-key
SYSTEM_ANTHROPIC_API_KEY=your-anthropic-key

# Default LLM configuration
DEFAULT_LLM_PROVIDER=zhipu
DEFAULT_LLM_MODEL=glm-4-flashx
```

### API Response Examples

#### Successful Analysis with GLM-4-FlashX

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_text": "She dont like pizza and he dont eat vegetables neither.",
  "corrected_text": "She doesn't like pizza and he doesn't eat vegetables either.",
  "mode": "accuracy",
  "errors": [
    {
      "error_type": "grammar",
      "original_span": "dont",
      "corrected_span": "doesn't",
      "start_index": 4,
      "end_index": 8,
      "explanation": "Use doesn't (does not) with third-person singular subjects."
    },
    {
      "error_type": "grammar",
      "original_span": "dont",
      "corrected_span": "doesn't",
      "start_index": 31,
      "end_index": 35
    },
    {
      "error_type": "word_choice",
      "original_span": "neither",
      "corrected_span": "either",
      "start_index": 52,
      "end_index": 59,
      "explanation": "Use 'either' in negative sentences, not 'neither'."
    }
  ],
  "statistics": {
    "total_errors": 3,
    "rule_engine_errors": 2,
    "llm_corrections": 1,
    "error_types": {
      "grammar": 2,
      "word_choice": 1
    }
  },
  "llm_metadata": {
    "provider": "zhipu",
    "provider_display_name": "Zhipu AI",
    "model": "glm-4-flashx",
    "model_display_name": "GLM-4-FlashX",
    "processing_time_ms": 8200,
    "token_usage": {
      "input_tokens": 18,
      "output_tokens": 22,
      "total_tokens": 40
    },
    "estimated_cost_usd": 0.000004,
    "using_custom_key": false
  },
  "processing_time_ms": 9100,
  "created_at": "2026-02-03T10:30:45.123Z"
}
```

#### Graceful Degradation Example

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "original_text": "She dont like pizza.",
  "corrected_text": "She doesn't like pizza.",
  "mode": "accuracy",
  "errors": [
    {
      "error_type": "grammar",
      "original_span": "dont",
      "corrected_span": "doesn't",
      "start_index": 4,
      "end_index": 8
    }
  ],
  "statistics": {
    "total_errors": 1,
    "rule_engine_errors": 1,
    "llm_corrections": 0
  },
  "llm_metadata": {
    "provider": "none",
    "provider_display_name": "Rule-based only",
    "model": null,
    "degraded_mode": true,
    "degradation_reason": "OpenAI API timeout after 30s",
    "processing_time_ms": 0
  },
  "warnings": [
    "LLM provider unavailable. Results based on LanguageTool only."
  ],
  "processing_time_ms": 1200,
  "created_at": "2026-02-03T10:31:15.456Z"
}
```

---

**End of Design Document**
