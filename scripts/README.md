# English Transfer Assistant - Development Scripts

This directory contains helper scripts for the English Transfer Assistant development workflow.

## Available Scripts

### 1. dev.sh - One-Click Development Startup

Starts all development services (PostgreSQL, Redis, Backend API, Frontend) with a single command.

**Usage:**
```bash
./scripts/dev.sh
```

**Features:**
- Checks and starts Docker Desktop if needed
- Starts PostgreSQL and Redis containers
- Waits for services to be healthy
- Starts backend server (background, logs to `logs/backend.log`)
- Starts frontend dev server (background, logs to `logs/frontend.log`)
- Displays service URLs and quick test commands
- Traps Ctrl+C to stop all services gracefully

**Service URLs:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

**Requirements:**
- Docker Desktop installed and running
- Poetry installed
- Node.js installed
- Backend dependencies installed (`poetry install`)
- Frontend dependencies installed (`npm install`)

---

### 2. verify.sh - Environment Validation

Validates that all development dependencies and services are correctly installed and running.

**Usage:**
```bash
./scripts/verify.sh
```

**Checks:**
- Poetry installation and version
- Docker daemon status
- Backend dependencies (virtual environment, key packages)
- Frontend dependencies (node_modules, package.json)
- File structure (key configuration files)
- Backend health check endpoint
- Frontend accessibility
- PostgreSQL connection and database
- Redis connection

**Exit Codes:**
- `0` - All critical checks passed
- `1` - Some checks failed

**Output:**
Color-coded pass/fail report with warnings and helpful fix suggestions.

---

### 3. test.sh - Quick Test Runner

Runs backend and frontend tests with optional lint/format checks.

**Usage:**
```bash
# Run all tests
./scripts/test.sh

# Run only backend tests
./scripts/test.sh --backend-only

# Run only frontend tests
./scripts/test.sh --frontend-only

# Run tests with lint/format checks
./scripts/test.sh --with-lint

# Show help
./scripts/test.sh --help
```

**Backend Tests:**
- Runs pytest with verbose output
- Checks test coverage (if configured)
- Optional: Ruff linting (`--with-lint`)
- Optional: Black formatting check (`--with-lint`)

**Frontend Tests:**
- Runs test suite (vitest/jest)
- Runs TypeScript type check
- Optional: ESLint check (`--with-lint`)

**Exit Codes:**
- `0` - All tests passed
- `1` - Some tests failed

---

## Quick Start Guide

### First Time Setup

1. **Install prerequisites:**
   - Docker Desktop: https://www.docker.com/products/docker-desktop
   - Poetry: https://python-poetry.org/docs/#installation
   - Node.js: https://nodejs.org/

2. **Install dependencies:**
   ```bash
   cd backend
   poetry install

   cd ../frontend
   npm install
   ```

3. **Verify environment:**
   ```bash
   ./scripts/verify.sh
   ```

4. **Start development:**
   ```bash
   ./scripts/dev.sh
   ```

### Daily Development Workflow

1. **Start services:**
   ```bash
   ./scripts/dev.sh
   ```

2. **View logs (in separate terminals):**
   ```bash
   tail -f logs/backend.log
   tail -f logs/frontend.log
   ```

3. **Run tests:**
   ```bash
   ./scripts/test.sh
   ```

4. **Stop services:**
   Press `Ctrl+C` in the terminal running `dev.sh`

---

## Troubleshooting

### Docker Issues

**Problem:** Docker daemon not running
```bash
# Start Docker Desktop manually
open -a Docker  # macOS
# or use the application menu on Windows/Linux
```

**Problem:** Containers not starting
```bash
# Check container status
docker ps -a

# View container logs
docker logs english-assistant-db
docker logs english-assistant-redis

# Restart containers
docker-compose restart
```

### Backend Issues

**Problem:** Backend not starting
```bash
# Check logs
cat logs/backend.log

# Manual start for debugging
cd backend
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Problem:** Dependencies missing
```bash
cd backend
poetry install
```

### Frontend Issues

**Problem:** Frontend not starting
```bash
# Check logs
cat logs/frontend.log

# Manual start for debugging
cd frontend
npm run dev
```

**Problem:** Type errors
```bash
cd frontend
npm run type-check
```

---

## Script Dependencies

The scripts require:
- `bash` (version 4.0+)
- `docker` and `docker-compose`
- `curl` (for health checks)
- `poetry` (for backend)
- `node` and `npm` (for frontend)

All scripts include error handling and will provide helpful messages if dependencies are missing.

---

## Customization

### Port Configuration

If you need to change default ports, update these files:
- `docker-compose.yml` - PostgreSQL (5432), Redis (6379)
- `scripts/dev.sh` - Backend (8000), Frontend (5173)
- `backend/.env` - Backend configuration
- `frontend/vite.config.ts` - Frontend port

### Environment Variables

Backend configuration is in `backend/.env` (copy from `backend/.env.example`):
```bash
cp backend/.env.example backend/.env
```

---

## Contributing

When adding new scripts:
1. Make them executable (`chmod +x scripts/your-script.sh`)
2. Follow the existing naming convention (lowercase with `.sh` extension)
3. Include ANSI colors for output consistency
4. Add proper error handling with `set -e`
5. Include this header in your script:
   ```bash
   #!/bin/bash
   #
   # Script Name - Brief Description
   #
   # Usage: ./scripts/your-script.sh [options]
   ```

---

## Additional Resources

- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [Project Documentation](../docs/)
- [GitHub Issues](https://github.com/your-repo/issues)
