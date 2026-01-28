#!/bin/bash

################################################################################
# English Transfer Assistant - Development Startup Script
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

# PID file for tracking background processes
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# Log files
mkdir -p "$PROJECT_ROOT/logs"
BACKEND_LOG="$PROJECT_ROOT/logs/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/logs/frontend.log"

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
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

################################################################################
# Cleanup Function
################################################################################

cleanup() {
    echo -e "\n${YELLOW}Stopping all services...${NC}"

    # Stop backend
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            print_info "Stopping backend server (PID: $BACKEND_PID)..."
            kill "$BACKEND_PID" 2>/dev/null || true
            wait "$BACKEND_PID" 2>/dev/null || true
            print_success "Backend server stopped"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    # Stop frontend
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            print_info "Stopping frontend dev server (PID: $FRONTEND_PID)..."
            kill "$FRONTEND_PID" 2>/dev/null || true
            wait "$FRONTEND_PID" 2>/dev/null || true
            print_success "Frontend dev server stopped"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi

    # Stop Docker containers
    print_info "Stopping Docker containers..."
    docker-compose down 2>/dev/null || true
    print_success "Docker containers stopped"

    echo -e "\n${GREEN}All services stopped successfully!${NC}\n"
    exit 0
}

# Trap Ctrl+C and other signals
trap cleanup SIGINT SIGTERM

################################################################################
# Check Prerequisites
################################################################################

check_docker() {
    print_info "Checking Docker Desktop..."

    if ! run_with_timeout 3 docker info > /dev/null 2>&1; then
        print_error "Docker is not running!"
        print_info "Attempting to start Docker Desktop..."

        # Try to start Docker Desktop on macOS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open -a Docker
            print_info "Waiting for Docker to start..."
            sleep 10

            # Wait up to 60 seconds for Docker to be ready
            for i in {1..12}; do
                if run_with_timeout 3 docker info > /dev/null 2>&1; then
                    print_success "Docker Desktop started"
                    return 0
                fi
                echo -n "."
                sleep 5
            done
            echo

            if ! run_with_timeout 3 docker info > /dev/null 2>&1; then
                print_error "Failed to start Docker Desktop. Please start it manually."
                exit 1
            fi
        else
            print_error "Please start Docker Desktop manually and run this script again."
            exit 1
        fi
    else
        print_success "Docker is running"
    fi
}

check_poetry() {
    print_info "Checking Poetry installation..."

    if ! command -v poetry &> /dev/null; then
        print_error "Poetry is not installed!"
        print_info "Install it from: https://python-poetry.org/docs/#installation"
        exit 1
    fi

    POETRY_VERSION=$(poetry --version)
    print_success "Poetry installed: $POETRY_VERSION"
}

check_node() {
    print_info "Checking Node.js installation..."

    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed!"
        print_info "Install it from: https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
}

################################################################################
# Start Services
################################################################################

start_docker_services() {
    print_header "Starting Docker Services"

    cd "$PROJECT_ROOT"

    print_info "Starting PostgreSQL container..."
    docker-compose up -d postgres

    print_info "Waiting for containers to be healthy..."

    # Wait for PostgreSQL
    print_info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker exec english-assistant-db pg_isready -U postgres &> /dev/null; then
            print_success "PostgreSQL is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    echo

}

start_backend() {
    print_header "Starting Backend Server"

    cd "$PROJECT_ROOT/backend"

    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Installing dependencies..."
        poetry install
    fi

    print_info "Starting backend server in background..."
    print_info "Logs: $BACKEND_LOG"

    # Start backend in background
    poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"

    # Wait for backend to start
    print_info "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend server started (PID: $BACKEND_PID)"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    echo

    print_error "Backend server failed to start. Check logs: $BACKEND_LOG"
    exit 1
}

start_frontend() {
    print_header "Starting Frontend Dev Server"

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        npm install
    fi

    print_info "Starting frontend dev server in background..."
    print_info "Logs: $FRONTEND_LOG"

    # Start frontend in background
    npm run dev > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

    # Wait for frontend to start
    print_info "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            print_success "Frontend dev server started (PID: $FRONTEND_PID)"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    echo

    print_warning "Frontend may still be starting. Check logs: $FRONTEND_LOG"
}

################################################################################
# Display Service Information
################################################################################

display_info() {
    print_header "Services Started Successfully!"

    echo -e "${GREEN}Backend API:${NC}"
    echo -e "  URL:        ${BLUE}http://localhost:8000${NC}"
    echo -e "  Health:     ${BLUE}http://localhost:8000/health${NC}"
    echo -e "  API Docs:   ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "  Logs:       ${BLUE}$BACKEND_LOG${NC}"
    echo ""

    echo -e "${GREEN}Frontend App:${NC}"
    echo -e "  URL:        ${BLUE}http://localhost:5173${NC}"
    echo -e "  Logs:       ${BLUE}$FRONTEND_LOG${NC}"
    echo ""

    echo -e "${GREEN}Databases:${NC}"
    echo -e "  PostgreSQL: ${BLUE}localhost:5432${NC}"
    echo ""

    echo -e "${GREEN}Quick Test Commands:${NC}"
    echo -e "  Backend health:   ${YELLOW}curl http://localhost:8000/health${NC}"
    echo -e "  View backend log: ${YELLOW}tail -f $BACKEND_LOG${NC}"
    echo -e "  View frontend log: ${YELLOW}tail -f $FRONTEND_LOG${NC}"
    echo -e "  Stop all:         ${YELLOW}Press Ctrl+C${NC}"
    echo ""

    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "English Transfer Assistant - Development Environment"

    # Check prerequisites
    check_docker
    check_poetry
    check_node

    # Start services
    start_docker_services
    start_backend
    start_frontend

    # Display information
    display_info

    # Keep script running
    print_info "Script is now monitoring services. Press Ctrl+C to stop all."
    echo ""

    # Wait indefinitely (until Ctrl+C)
    while true; do
        sleep 1
    done
}

# Run main function
main
