#!/bin/bash

# Ecom Application Deployment Script
# Author: Om Kumar Kaushik
# Description: Automated deployment script with rollback capability

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/opt/ecom-app"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ENVIRONMENT="${1:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f "$APP_DIR/.env" ]; then
        log_error ".env file not found in $APP_DIR"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

create_backup() {
    log_info "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup current docker-compose configuration
    if [ -f "$APP_DIR/docker-compose.yml" ]; then
        cp "$APP_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose_$TIMESTAMP.yml"
    fi
    
    # Backup data directory
    if [ -d "$APP_DIR/data" ]; then
        tar -czf "$BACKUP_DIR/data_$TIMESTAMP.tar.gz" -C "$APP_DIR" data
    fi
    
    # Export current container state
    docker-compose -f "$APP_DIR/docker-compose.yml" config > "$BACKUP_DIR/docker-compose.state_$TIMESTAMP.yml"
    
    log_info "Backup created at $BACKUP_DIR"
}

pull_latest_images() {
    log_info "Pulling latest Docker images..."
    
    cd "$APP_DIR"
    docker-compose pull
    
    log_info "Images pulled successfully"
}

run_health_check() {
    local max_attempts=30
    local attempt=1
    
    log_info "Running health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
            log_info "Health check passed"
            return 0
        fi
        
        log_warn "Health check failed, attempt $attempt/$max_attempts"
        sleep 2
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

deploy() {
    log_info "Starting deployment for $ENVIRONMENT environment..."
    
    cd "$APP_DIR"
    
    # Source environment variables
    source .env
    
    # Stop existing containers gracefully
    log_info "Stopping existing containers..."
    docker-compose down --timeout 30
    
    # Start new containers
    log_info "Starting new containers..."
    docker-compose up -d
    
    # Wait for containers to be ready
    sleep 10
    
    # Check container status
    log_info "Checking container status..."
    docker-compose ps
    
    # Run health check
    if run_health_check; then
        log_info "Deployment successful!"
        
        # Cleanup old images
        log_info "Cleaning up old images..."
        docker image prune -f
        
        # Remove old backups (keep last 5)
        find "$BACKUP_DIR" -name "*.yml" -type f | sort -r | tail -n +6 | xargs -r rm
        find "$BACKUP_DIR" -name "*.tar.gz" -type f | sort -r | tail -n +6 | xargs -r rm
        
        return 0
    else
        log_error "Health check failed!"
        return 1
    fi
}

rollback() {
    log_warn "Rolling back to previous deployment..."
    
    cd "$APP_DIR"
    
    # Find the most recent backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/docker-compose.state_*.yml 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup found for rollback"
        exit 1
    fi
    
    log_info "Using backup: $LATEST_BACKUP"
    
    # Stop current containers
    docker-compose down --timeout 30
    
    # Use backup configuration
    docker-compose -f "$LATEST_BACKUP" up -d
    
    sleep 10
    
    if run_health_check; then
        log_info "Rollback successful"
    else
        log_error "Rollback failed"
        exit 1
    fi
}

show_logs() {
    log_info "Showing application logs..."
    cd "$APP_DIR"
    docker-compose logs --tail=100 -f
}

main() {
    case "${2:-deploy}" in
        deploy)
            check_prerequisites
            create_backup
            pull_latest_images
            if ! deploy; then
                log_error "Deployment failed, initiating rollback..."
                rollback
                exit 1
            fi
            ;;
        rollback)
            rollback
            ;;
        logs)
            show_logs
            ;;
        status)
            cd "$APP_DIR"
            docker-compose ps
            ;;
        *)
            echo "Usage: $0 {production|staging} {deploy|rollback|logs|status}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy the application"
            echo "  rollback - Rollback to previous deployment"
            echo "  logs     - Show application logs"
            echo "  status   - Show container status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
