.PHONY: help install install-dev install-prod clean test lint format check run run-prod docker-build docker-run

# Default target
help:
	@echo "AI Communication Assistant Backend - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  install-prod   Install production dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run            Run development server"
	@echo "  test           Run tests"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with black and isort"
	@echo "  check          Run all quality checks"
	@echo ""
	@echo "Production:"
	@echo "  run-prod       Run production server with Gunicorn"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          Clean up temporary files"
	@echo "  help           Show this help message"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

install-prod:
	pip install -r requirements-prod.txt

# Development targets
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint:
	flake8 app/
	mypy app/

format:
	black app/
	isort app/

check: format lint test

# Production targets
run-prod:
	gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Docker targets
docker-build:
	docker build -t ai-communication-assistant-backend .

docker-run:
	docker run -p 8000:8000 --env-file .env ai-communication-assistant-backend

# Maintenance targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".black_cache" -exec rm -rf {} +

# Database targets
db-init:
	python -c "from app.database import create_tables; create_tables()"

db-reset: clean
	rm -f data/email_database.db
	python -c "from app.database import create_tables; create_tables()"

# Environment setup
env-setup:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env 2>/dev/null || echo "Please create .env file manually"; \
		echo "Please update .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

# Quick start for new developers
quickstart: env-setup install-dev db-init
	@echo "Quick start complete!"
	@echo "1. Update your .env file with API keys and credentials"
	@echo "2. Run 'make run' to start the development server"
	@echo "3. Visit http://localhost:8000/docs for API documentation"
