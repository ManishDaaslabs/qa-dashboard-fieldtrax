#!/bin/bash

# QA Analytics Platform - Setup Script
# Usage: bash setup.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

echo "=========================================="
echo "QA Analytics Platform - Setup"
echo "Environment: $ENVIRONMENT"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python version
print_step "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

if [ "$ENVIRONMENT" = "dev" ]; then
    print_step "Setting up development environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_step "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source venv/bin/activate || . venv/Scripts/activate
    
    # Upgrade pip
    print_step "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install dependencies
    print_step "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
    
    # Create upload folder
    mkdir -p /tmp/qa_uploads
    
    # Initialize database
    print_step "Initializing SQLite database..."
    python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("Database initialized successfully")
EOF
    print_success "Database initialized"
    
    # Create .env file if not exists
    if [ ! -f ".env" ]; then
        print_step "Creating .env file..."
        cat > .env << EOF
# Development Environment Configuration
FLASK_ENV=development
FLASK_DEBUG=True
API_PORT=5000
API_HOST=0.0.0.0
DATABASE_URL=sqlite:///qa_analytics.db
EOF
        print_success ".env file created"
    fi
    
    print_success "Development environment setup complete!"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Activate virtual environment:"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo ""
    echo "2. Start the application:"
    echo "   python app.py"
    echo ""
    echo "3. Access the API:"
    echo "   curl http://localhost:5000/api/health"
    echo ""

elif [ "$ENVIRONMENT" = "prod" ]; then
    print_step "Setting up production environment with Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker Desktop"
        exit 1
    fi
    
    print_success "Docker found"
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not found. Please install Docker Compose"
        exit 1
    fi
    
    print_success "Docker Compose found"
    
    # Create .env file for production
    if [ ! -f ".env.prod" ]; then
        print_step "Creating .env.prod file..."
        cat > .env.prod << EOF
# Production Environment Configuration
DATABASE_URL=postgresql://qa_admin:secure_password_change_me@postgres:5432/qa_analytics
FLASK_ENV=production
FLASK_APP=app.py
API_PORT=5000
API_HOST=0.0.0.0
EOF
        print_success ".env.prod file created"
        print_error "IMPORTANT: Change the database password in .env.prod before deploying!"
    fi
    
    # Build Docker images
    print_step "Building Docker images..."
    docker-compose build
    print_success "Docker images built"
    
    # Start containers
    print_step "Starting services..."
    docker-compose up -d
    print_success "Services started"
    
    # Wait for database to be ready
    print_step "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Initialize database
    print_step "Initializing database..."
    docker-compose exec -T backend python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("Database initialized successfully")
EOF
    print_success "Database initialized"
    
    print_success "Production environment setup complete!"
    echo ""
    echo -e "${GREEN}Services are running:${NC}"
    echo "- Backend API: http://localhost:5000"
    echo "- Nginx Proxy: http://localhost:80"
    echo "- PostgreSQL: localhost:5432"
    echo ""
    echo -e "${GREEN}Useful commands:${NC}"
    echo "docker-compose logs -f backend      # View backend logs"
    echo "docker-compose ps                   # Show running services"
    echo "docker-compose down                 # Stop all services"
    echo ""

else
    print_error "Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

print_step "Setup complete! 🎉"
