# ==============================================================================
# AI Agent Webhook Middleware - Enterprise Automation Makefile
# ==============================================================================

.PHONY: help setup run test lint format typecheck docker-build docker-run clean

# Default target when running just 'make'
default: help

help:
	@echo "================================================================="
	@echo " AI Agent Webhook Middleware - Elite Command Reference"
	@echo "================================================================="
	@echo "  make setup        - Initialize virtual environment & install dependencies"
	@echo "  make run          - Start FastAPI development server with hot-reload"
	@echo "  make test         - Execute pytest suite with coverage reporting"
	@echo "  make lint         - Run static analysis (Flake8)"
	@echo "  make format       - Format code automatically using Black"
	@echo "  make typecheck    - Run static type checking with Mypy"
	@echo "  make docker-build - Build production Docker image"
	@echo "  make docker-run   - Run containerized application locally"
	@echo "  make clean        - Purge all cache, build, and virtual environments"
	@echo "================================================================="

setup:
	@echo "⚙️ Setting up Python virtual environment..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✨ Setup complete! Copy .env.example to .env to configure settings."

run:
	@echo "🚀 Starting FastAPI development server..."
	@if [ ! -f .env ]; then echo "⚠️ Warning: .env file not found. Copying from .env.example..."; cp .env.example .env; fi
	./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test:
	@echo "🧪 Running PyTest suite with coverage..."
	./venv/bin/pytest -v --tb=short --cov=main

lint:
	@echo "🔍 Running Flake8 linter..."
	./venv/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	@echo "🎨 Formatting codebase with Black..."
	./venv/bin/black .

typecheck:
	@echo "🛡️ Running static type checks with Mypy..."
	./venv/bin/mypy main.py

docker-build:
	@echo "🐳 Building production Docker container..."
	docker build -t ai-agent-webhook-middleware:latest .

docker-run:
	@echo "🚢 Running container locally on port 8000..."
	docker run --rm -p 8000:8000 --env-file .env ai-agent-webhook-middleware:latest

clean:
	@echo "🧹 Purging cache, build artifacts, and virtual environment..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf venv/ .coverage htmlcov/ dist/ build/
	@echo "✨ Clean complete."
