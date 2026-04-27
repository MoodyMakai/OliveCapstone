#!/bin/bash

# --- Configuration ---
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helper Functions ---
function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

function check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env file not found. Creating one from .env.example..."
        cp .env.example .env
        log_info "Please edit the .env file with your domain and email before starting."
        exit 1
    fi
}

# --- Main Commands ---
case "$1" in
    start)
        check_docker
        check_env

        # Ensure database.sqlite is a file, not a directory (prevents Docker mount issues)
        if [ -d "backend/database.sqlite" ]; then
            log_warn "Found directory at backend/database.sqlite, removing it..."
            rm -rf "backend/database.sqlite"
        fi
        touch backend/database.sqlite
        mkdir -p backend/images

        log_info "Starting BBFS Server..."
        docker compose -f "$COMPOSE_FILE" up -d --build
        log_info "Server started successfully!"
        ;;
    stop)
        log_info "Stopping BBFS Server..."
        docker compose -f "$COMPOSE_FILE" down
        log_info "Server stopped."
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    update)
        log_info "Updating BBFS Code..."
        git pull
        $0 start
        ;;
    logs)
        docker compose -f "$COMPOSE_FILE" logs -f backend
        ;;
    status)
        docker compose -f "$COMPOSE_FILE" ps
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|update|logs|status}"
        exit 1
        ;;
esac
