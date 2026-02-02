#!/bin/bash

################################################################################
# English Transfer Assistant - Quick Test Script
################################################################################

set -e

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
BACKEND_TESTS=0
FRONTEND_TESTS=0

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

################################################################################
# Backend Tests
################################################################################

test_backend() {
    print_header "Running Backend Tests"

    if [ ! -d "$PROJECT_ROOT/backend" ]; then
        print_error "Backend directory not found"
        return 1
    fi

    cd "$PROJECT_ROOT/backend"

    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found. Run: poetry install"
        return 1
    fi

    # Check if pytest is installed
    if ! poetry run python -c "import pytest" 2>/dev/null; then
        print_error "pytest not installed. Run: poetry install"
        return 1
    fi

    print_info "Running backend unit tests..."
    echo ""

    # Run pytest with color output
    if poetry run pytest -v --color=yes 2>&1 | tee /tmp/pytest_output.txt; then
        BACKEND_TESTS=$(grep -oP '\d+ passed' /tmp/pytest_output.txt | grep -oP '\d+' || echo "0")
        print_success "Backend tests completed successfully"
        return 0
    else
        BACKEND_TESTS=$(grep -oP '\d+ passed' /tmp/pytest_output.txt | grep -oP '\d+' || echo "0")
        print_error "Backend tests failed"
        return 1
    fi
}

test_backend_lint() {
    print_header "Running Backend Lint Checks"

    if [ ! -d "$PROJECT_ROOT/backend" ]; then
        print_error "Backend directory not found"
        return 1
    fi

    cd "$PROJECT_ROOT/backend"

    # Check if ruff is installed
    if poetry run python -c "import ruff" 2>/dev/null; then
        print_info "Running ruff linter..."
        if poetry run ruff check . 2>&1 | tee /tmp/ruff_output.txt; then
            print_success "No ruff errors found"
        else
            print_error "Ruff found issues. Run 'poetry run ruff check --fix .' to auto-fix"
            return 1
        fi
    else
        print_warning "Ruff not installed, skipping lint check"
    fi

    # Check if black is installed
    if poetry run python -c "import black" 2>/dev/null; then
        print_info "Running black formatter check..."
        if poetry run black --check . 2>&1 | tee /tmp/black_output.txt; then
            print_success "Code formatting is correct"
        else
            print_warning "Code needs formatting. Run 'poetry run black .' to fix"
            return 1
        fi
    else
        print_warning "Black not installed, skipping format check"
    fi
}

################################################################################
# Frontend Tests
################################################################################

test_frontend() {
    print_header "Running Frontend Tests"

    if [ ! -d "$PROJECT_ROOT/frontend" ]; then
        print_error "Frontend directory not found"
        return 1
    fi

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "node_modules not found. Run: npm install"
        return 1
    fi

    # Check package.json for test script
    if ! grep -q '"test"' package.json; then
        print_warning "No test script found in package.json"
        print_info "Consider adding test setup with vitest"
        return 0
    fi

    print_info "Running frontend tests..."
    echo ""

    # Run npm test
    if npm test -- --run 2>&1 | tee /tmp/npm_test_output.txt; then
        FRONTEND_TESTS=$(grep -oP '\d+ passed' /tmp/npm_test_output.txt | grep -oP '\d+' || echo "0")
        print_success "Frontend tests completed successfully"
        return 0
    else
        FRONTEND_TESTS=$(grep -oP '\d+ passed' /tmp/npm_test_output.txt | grep -oP '\d+' || echo "0")
        print_error "Frontend tests failed"
        return 1
    fi
}

test_frontend_typecheck() {
    print_header "Running Frontend Type Check"

    if [ ! -d "$PROJECT_ROOT/frontend" ]; then
        print_error "Frontend directory not found"
        return 1
    fi

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "node_modules not found. Run: npm install"
        return 1
    fi

    print_info "Running TypeScript type check..."
    echo ""

    # Check if type-check script exists
    if grep -q '"type-check"' package.json; then
        if npm run type-check 2>&1 | tee /tmp/tsc_output.txt; then
            print_success "TypeScript type check passed"
            return 0
        else
            print_error "TypeScript type check failed"
            return 1
        fi
    else
        # Try running vue-tsc directly
        if npx vue-tsc --noEmit 2>&1 | tee /tmp/tsc_output.txt; then
            print_success "TypeScript type check passed"
            return 0
        else
            print_error "TypeScript type check failed"
            return 1
        fi
    fi
}

test_frontend_lint() {
    print_header "Running Frontend Lint Check"

    if [ ! -d "$PROJECT_ROOT/frontend" ]; then
        print_error "Frontend directory not found"
        return 1
    fi

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "node_modules not found. Run: npm install"
        return 1
    fi

    # Check if eslint is configured
    if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ]; then
        print_info "Running ESLint..."
        if npm run lint 2>&1 | tee /tmp/eslint_output.txt; then
            print_success "ESLint check passed"
            return 0
        else
            print_error "ESLint found issues"
            return 1
        fi
    else
        print_warning "ESLint not configured, skipping lint check"
        return 0
    fi
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "English Transfer Assistant - Quick Test Suite"

    # Parse command line arguments
    RUN_BACKEND=true
    RUN_FRONTEND=true
    RUN_LINT=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                RUN_FRONTEND=false
                shift
                ;;
            --frontend-only)
                RUN_BACKEND=false
                shift
                ;;
            --with-lint)
                RUN_LINT=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --backend-only    Run only backend tests"
                echo "  --frontend-only   Run only frontend tests"
                echo "  --with-lint       Include lint/format checks"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Run '$0 --help' for usage information"
                exit 1
                ;;
        esac
    done

    # Run tests
    BACKEND_RESULT=0
    FRONTEND_RESULT=0
    LINT_RESULT=0

    if [ "$RUN_BACKEND" = true ]; then
        test_backend || BACKEND_RESULT=$?

        if [ "$RUN_LINT" = true ]; then
            test_backend_lint || LINT_RESULT=$?
        fi
    fi

    if [ "$RUN_FRONTEND" = true ]; then
        test_frontend || FRONTEND_RESULT=$?
        test_frontend_typecheck || FRONTEND_RESULT=$?

        if [ "$RUN_LINT" = true ]; then
            test_frontend_lint || LINT_RESULT=$?
        fi
    fi

    # Print summary
    print_header "Test Summary"

    if [ "$RUN_BACKEND" = true ]; then
        if [ $BACKEND_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Backend Tests:   PASSED${NC}"
        else
            echo -e "${RED}✗ Backend Tests:   FAILED${NC}"
        fi
    fi

    if [ "$RUN_FRONTEND" = true ]; then
        if [ $FRONTEND_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Frontend Tests:  PASSED${NC}"
        else
            echo -e "${RED}✗ Frontend Tests:  FAILED${NC}"
        fi
    fi

    if [ "$RUN_LINT" = true ]; then
        if [ $LINT_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Lint/Format:     PASSED${NC}"
        else
            echo -e "${RED}✗ Lint/Format:     FAILED${NC}"
        fi
    fi

    echo ""

    # Exit with appropriate code
    if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ] || [ $LINT_RESULT -ne 0 ]; then
        exit 1
    else
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  ✓ All tests passed!${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"
        exit 0
    fi
}

# Run main function
main "$@"
