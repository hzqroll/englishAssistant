# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**English Transfer Assistant** is an AI-powered English text correction tool. It uses a hybrid pipeline combining rule-based checking (LanguageTool) and LLM-based optimization (ZhipuAI, OpenAI, Anthropic, Gemini).

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL.
- **Frontend**: Vue 3, TypeScript, Vite, Tailwind CSS, Pinia.
- **Architecture**: 4-stage analysis pipeline (Preprocess -> Rule Check -> LLM Optimize -> Merge).

## Common Commands

### Quick Start
- **Start All**: `./scripts/dev.sh` (Docker + Backend + Frontend)
- **Verify Env**: `./scripts/verify.sh`
- **Run Tests**: `./scripts/test.sh`

### Backend (`/backend`)
- **Install**: `poetry install`
- **Run Server**: `poetry run uvicorn main:app --reload`
- **Test**: `poetry run pytest`
- **Test (Single)**: `poetry run pytest tests/path/to/test.py`
- **Format**: `poetry run black . && poetry run ruff check . --fix`
- **Type Check**: `poetry run mypy .`
- **Database Migrations**:
  - Create: `poetry run alembic revision --autogenerate -m "message"`
  - Apply: `poetry run alembic upgrade head`

### Frontend (`/frontend`)
- **Install**: `npm install`
- **Run Dev**: `npm run dev`
- **Build**: `npm run build`
- **Test**: `npm run test`
- **Type Check**: `vue-tsc -b` (part of build)

### Docker
- **Up**: `docker-compose up -d`
- **Logs**: `docker-compose logs -f`
- **Down**: `docker-compose down`

## Code Structure

### Backend Structure
- `api/v1/`: API route handlers (auth, analysis, history).
- `models/`: SQLAlchemy ORM models (`ea_` prefix tables).
- `pipeline/`: Core logic.
  - `rule_engine.py`: LanguageTool integration.
  - `llm_engine.py`: LLM provider integration.
  - `merger.py`: Conflict resolution between rules and LLM.
- `services/`: Business logic services (User, Auth, Analysis).

### Frontend Structure
- `src/api/`: Axios client wrappers.
- `src/components/`: Vue components.
  - `panels/`: Main UI sections (Input, RuleEngine, LLM).
- `src/stores/`: Pinia state management (`analysisStore`, `authStore`).
- `src/composables/`: Reusable logic hooks.

## Coding Standards

### General
- **Files**: Prefer editing existing files over creating new ones.
- **Paths**: Use absolute paths for imports where possible.

### Backend (Python)
- **Typing**: Strict type hints required on ALL functions.
- **Style**: Google-style docstrings. Black formatting (100 char line limit).
- **Models**: Use `SoftDeleteMixin` for models. Table names prefixed with `ea_`.
- **Imports**: Grouped as Standard Library -> Third Party -> Local.
- **Async**: Use `async/await` for all I/O bound operations.

### Frontend (Vue/TS)
- **Component Style**: `<script setup lang="ts">`.
- **Imports**: Use `@/` alias for `src/`.
- **Stores**: Use Pinia Composition API syntax (not Option API).
- **Size**: Keep components under 300 lines; extract sub-components if larger.
- **Styling**: Tailwind CSS utility classes.

## Architecture & Patterns

- **Analysis Pipeline**: The core feature runs text through `AnalysisPipeline.analyze()`.
  - **Phase 1**: Rule-only analysis (fast, cheap).
  - **Phase 2**: LLM optimization (slower, costlier, user-triggered).
- **LLM Providers**: Abstracted via `LLMProvider` interface. Configured per-user or system default.
- **Error Handling**: Graceful degradation. If LLM fails, return Rule-based results.
- **State Management**: Frontend uses `analysisStore` to manage the complex state of split analysis (Rule result vs LLM result).
