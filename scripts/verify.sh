#!/bin/bash

################################################################################
# English Transfer Assistant - Environment Verification Script
################################################################################

# Don't exit on error - we want to report all failures
set +e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Track results
PASSED=0
FAILED=0
WARNINGS=0

################################################################################
# Helper Functions
################################################################################

# Timeout function for commands that might hang
run_with_timeout() {
    local timeout_seconds=$1
    shift
    local command=("$@")
    local pid

    # Run command in background
    "${command[@]}" &
    pid=$!

    # Wait for timeout or completion
    local count=0
    while kill -0 $pid 2>/dev/null; do
        if [ $count -ge $timeout_seconds ]; then
            kill $pid 2>/dev/null
            wait $pid 2>/dev/null
            return 124  # timeout exit code
        fi
        sleep 1
        ((count++))
    done

    wait $pid
    return $?
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
}

################################################################################
# Verification Functions
################################################################################

verify_poetry() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Poetry Installation${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    if ! command -v poetry &> /dev/null; then
        print_fail "Poetry is not installed"
        print_info "Install from: https://python-poetry.org/docs/#installation"
        return 1
    fi

    POETRY_VERSION=$(poetry --version 2>&1)
    print_success "Poetry installed: $POETRY_VERSION"

    # Check version
    POETTY_VERSION_NUMBER=$(poetry --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    print_info "Version: $POETTY_VERSION_NUMBER"
}

verify_docker() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Docker Installation${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    if ! command -v docker &> /dev/null; then
        print_fail "Docker is not installed"
        print_info "Install from: https://www.docker.com/products/docker-desktop"
        return 1
    fi

    DOCKER_VERSION=$(docker --version 2>/dev/null | grep -oE 'Docker version [0-9]+\.[0-9]+\.[0-9]+')
    print_success "Docker installed: $DOCKER_VERSION"

    # Check if daemon is running with timeout to prevent hanging
    if run_with_timeout 3 docker info > /dev/null 2>&1; then
        print_success "Docker daemon is running"
    else
        print_fail "Docker daemon is not running"
        print_info "Start Docker Desktop to proceed"
        return 1
    fi
}

verify_backend_deps() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Backend Dependencies${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    if [ ! -d "$PROJECT_ROOT/backend" ]; then
        print_fail "Backend directory not found"
        return 1
    fi

    if [ ! -d "$PROJECT_ROOT/backend/.venv" ]; then
        print_fail "Python virtual environment not found (.venv)"
        print_info "Run: cd backend && poetry install"
        return 1
    fi

    print_success "Backend virtual environment exists"

    # Check if key packages are installed
    cd "$PROJECT_ROOT/backend"

    if poetry run python -c "import fastapi" 2>/dev/null; then
        print_success "FastAPI is installed"
    else
        print_fail "FastAPI is not installed"
        return 1
    fi

    if poetry run python -c "import sqlalchemy" 2>/dev/null; then
        print_success "SQLAlchemy is installed"
    else
        print_fail "SQLAlchemy is not installed"
        return 1
    fi
}

verify_frontend_deps() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Frontend Dependencies${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    if [ ! -d "$PROJECT_ROOT/frontend" ]; then
        print_fail "Frontend directory not found"
        return 1
    fi

    if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
        print_fail "Node modules not found (node_modules)"
        print_info "Run: cd frontend && npm install"
        return 1
    fi

    print_success "Frontend node_modules exists"

    # Check package.json
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        print_success "package.json exists"
    else
        print_fail "package.json not found"
        return 1
    fi
}

verify_backend_health() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Backend Health Check${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    print_info "Testing backend health endpoint..."

    if ! curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        print_fail "Backend health check failed (http://localhost:8000/health)"
        print_info "Make sure backend is running: cd backend && poetry run uvicorn main:app --reload"
        return 1
    fi

    RESPONSE=$(curl -s http://localhost:8000/health)
    print_success "Backend health check passed"

    if echo "$RESPONSE" | grep -q "healthy"; then
        print_success "Backend status: healthy"
    else
        print_warning "Backend status check unclear"
    fi
}

verify_frontend_access() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Frontend Access Check${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    print_info "Testing frontend access..."

    if ! curl -s -f http://localhost:5173 > /dev/null 2>&1; then
        print_fail "Frontend not accessible (http://localhost:5173)"
        print_info "Make sure frontend is running: cd frontend && npm run dev"
        return 1
    fi

    print_success "Frontend is accessible"
}

verify_postgres() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}PostgreSQL Connection${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    print_info "Testing PostgreSQL connection..."

    if ! docker ps | grep -q "english-assistant-db"; then
        print_warning "PostgreSQL container is not running"
        print_info "Start with: docker-compose up -d postgres"
        return 1
    fi

    print_success "PostgreSQL container is running"

    if docker exec english-assistant-db pg_isready -U postgres > /dev/null 2>&1; then
        print_success "PostgreSQL is accepting connections"
    else
        print_fail "PostgreSQL is not ready"
        return 1
    fi

    # Test database connection
    if docker exec english-assistant-db psql -U postgres -d english_assistant -c "SELECT 1;" > /dev/null 2>&1; then
        print_success "Can connect to 'english_assistant' database"
    else
        print_warning "Cannot connect to 'english_assistant' database"
    fi
}

verify_redis() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Redis Connection${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    print_info "Testing Redis connection..."

    if ! docker ps | grep -q "english-assistant-redis"; then
        print_warning "Redis container is not running"
        print_info "Start with: docker-compose up -d redis"
        return 1
    fi

    print_success "Redis container is running"

    if docker exec english-assistant-redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis is responding to PING"
    else
        print_fail "Redis is not responding"
        return 1
    fi
}

verify_file_structure() {
    echo -e "\n${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}File Structure${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

    # Check key files
    local files=(
        "$PROJECT_ROOT/docker-compose.yml"
        "$PROJECT_ROOT/backend/pyproject.toml"
        "$PROJECT_ROOT/backend/main.py"
        "$PROJECT_ROOT/frontend/package.json"
        "$PROJECT_ROOT/frontend/vite.config.ts"
    )

    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found: $(basename $file)"
        else
            print_fail "Missing: $(basename $file)"
        fi
    done
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "English Transfer Assistant - Environment Verification"

    # Run all checks
    verify_poetry
    verify_docker
    verify_backend_deps
    verify_frontend_deps
    verify_file_structure
    verify_backend_health
    verify_frontend_access
    verify_postgres
    verify_redis

    # Print summary
    print_header "Verification Summary"

    TOTAL=$((PASSED + FAILED + WARNINGS))

    echo -e "${GREEN}Passed:   $PASSED${NC}"
    echo -e "${RED}Failed:   $FAILED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${BLUE}Total:    $TOTAL${NC}"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  ✓ All critical checks passed!${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"
        exit 0
    else
        echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}  ✗ Some checks failed. Please fix the issues above.${NC}"
        echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}\n"
        exit 1
    fi
}

# Run main function
main
