#!/bin/bash

# Security Scanner Backend Docker Build Script
# This script builds and runs the Django backend in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if environment file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning "Environment file .env not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your configuration before running the application"
        else
            print_error "env.example file not found. Please create a .env file manually."
            exit 1
        fi
    else
        print_success "Environment file .env found"
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build development image
    print_status "Building development image..."
    docker build -t security-scanner-backend:dev .
    
    # Build production image
    print_status "Building production image..."
    docker build -f Dockerfile.prod -t security-scanner-backend:prod .
    
    print_success "Docker images built successfully"
}

# Run development environment
run_dev() {
    print_status "Starting development environment..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Start services
    docker-compose up -d
    
    print_success "Development environment started"
    print_status "Services available at:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Flower (Celery monitoring): http://localhost:5555"
    echo "  - Redis: localhost:6379"
}

# Run production environment
run_prod() {
    print_status "Starting production environment..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Production environment started"
    print_status "Services available at:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Flower (Celery monitoring): http://localhost:5555"
    echo "  - Redis: localhost:6379"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if [ "$1" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
    else
        docker-compose exec backend python manage.py migrate
    fi
    
    print_success "Database migrations completed"
}

# Show logs
show_logs() {
    if [ "$1" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    
    if [ "$1" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml down
    else
        docker-compose down
    fi
    
    print_success "Services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Remove images
    docker rmi security-scanner-backend:dev 2>/dev/null || true
    docker rmi security-scanner-backend:prod 2>/dev/null || true
    
    # Remove unused volumes
    docker volume prune -f
    
    print_success "Cleanup completed"
}

# Show help
show_help() {
    echo "Security Scanner Backend Docker Build Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build Docker images"
    echo "  dev       Run development environment"
    echo "  prod      Run production environment"
    echo "  migrate   Run database migrations"
    echo "  logs      Show logs (add 'prod' for production)"
    echo "  stop      Stop services (add 'prod' for production)"
    echo "  cleanup   Clean up Docker resources"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 dev"
    echo "  $0 prod"
    echo "  $0 migrate"
    echo "  $0 logs"
    echo "  $0 logs prod"
    echo "  $0 stop"
    echo "  $0 cleanup"
}

# Main script logic
main() {
    case "${1:-help}" in
        "build")
            check_docker
            check_env
            build_images
            ;;
        "dev")
            check_docker
            check_env
            build_images
            run_dev
            run_migrations
            ;;
        "prod")
            check_docker
            check_env
            build_images
            run_prod
            run_migrations prod
            ;;
        "migrate")
            run_migrations "${2:-}"
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "stop")
            stop_services "${2:-}"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
