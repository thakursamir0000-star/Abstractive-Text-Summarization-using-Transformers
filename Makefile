.PHONY: help install dev test lint format type-check clean run setup

help:
	@echo "Text Summarization Project - Available Commands"
	@echo "==============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete project setup with venv and dependencies"
	@echo "  make install        - Install dependencies"
	@echo "  make install-dev    - Install dependencies including dev tools"
	@echo ""
	@echo "Development:"
	@echo "  make run            - Run Streamlit app"
	@echo "  make dev            - Install dev dependencies and run app"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run flake8 linting"
	@echo "  make format         - Format code with black"
	@echo "  make type-check     - Run mypy type checking"
	@echo "  make check          - Run all checks (lint, type, format check)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run pytest tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make coverage       - Run tests with coverage report"
	@echo ""
	@echo "Python:"
	@echo "  make shell          - Open Python interactive shell"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove cache and build artifacts"
	@echo "  make clean-all      - Remove venv and all artifacts"
	@echo ""

setup:
	python -m venv venv
	. venv/bin/activate || venv\Scripts\activate
	pip install --upgrade pip
	pip install -r requirements.txt
	cp .env.example .env
	pytest tests/ -v

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt pytest pytest-cov black flake8 mypy

run:
	streamlit run app.py

dev: install-dev
	streamlit run app.py

lint:
	flake8 src/ tests/ app.py --max-line-length=88 --exclude=__pycache__

format:
	black src/ tests/ app.py

format-check:
	black --check src/ tests/ app.py

type-check:
	mypy src/ --ignore-missing-imports

check: lint type-check format-check
	@echo "✓ All checks passed!"

test:
	pytest tests/ -v --tb=short

test-verbose:
	pytest tests/ -vv --tb=long --showlocals

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

shell:
	python

docker-build:
	docker build -t text-summarizer .

docker-run:
	docker run -p 8501:8501 text-summarizer

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage .pytest_cache/ .mypy_cache/ 2>/dev/null || true
	@echo "✓ Cleaned up cache and build artifacts"

clean-all: clean
	rm -rf venv/ 2>/dev/null || true
	@echo "✓ Removed virtual environment"
