.PHONY: install dev prod clean test format lint setup

# Install dependencies using Poetry
install:
	poetry install

# Run development server with auto-reload
dev:
	poetry run uvicorn main:app --host 127.0.0.1 --port 5000 --reload

# Run production server
prod:
	poetry run uvicorn main:app --host 0.0.0.0 --port 5000

# Clean cache and temp files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Run tests
test:
	poetry run pytest

# Format code with black
format:
	poetry run black .

# Lint code
lint:
	poetry run flake8 src/

# First time setup
setup:
	@echo "Setting up Car Rental Website..."
	@echo "Installing Poetry dependencies..."
	poetry install
	@echo "Setup complete! Run 'make dev' to start the development server."
