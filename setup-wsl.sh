#!/bin/bash

# Setup script for Car Rental Website in WSL
# This script sets up the development environment for the project

set -e

echo "================================"
echo "Car Rental Website - WSL Setup"
echo "================================"
echo ""

# Check if running in WSL
if ! grep -qi microsoft /proc/version; then
    echo "Warning: This script is designed for WSL (Windows Subsystem for Linux)"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Install Poetry if not present
if ! command -v poetry &> /dev/null; then
    echo ""
    echo "Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    
    echo "Poetry installed successfully!"
else
    echo "Poetry is already installed: $(poetry --version)"
fi

# Configure Poetry to create virtual environments in project directory
echo ""
echo "Configuring Poetry..."
poetry config virtualenvs.in-project true

# Install project dependencies
echo ""
echo "Installing project dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env .env.backup 2>/dev/null || true
    cat > .env << 'EOF'
HOST=0.0.0.0
PORT=5000
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo ".env file created. Please update it with your actual values."
else
    echo ""
    echo ".env file already exists."
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
poetry run python -c "from src.utils import create_folders; create_folders()"

echo ""
echo "================================"
echo "Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update the .env file with your configuration"
echo "2. Run 'make dev' to start the development server"
echo "   OR run 'poetry run uvicorn main:app --host 0.0.0.0 --port 5000 --reload'"
echo ""
echo "Available commands:"
echo "  make setup  - Run initial setup"
echo "  make dev    - Start development server"
echo "  make prod   - Start production server"
echo "  make test   - Run tests"
echo "  make format - Format code with black"
echo "  make lint   - Lint code with flake8"
echo "  make clean  - Clean cache files"
echo ""
