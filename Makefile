# EAVT Helper Makefile
# Simple commands for development and testing

.PHONY: help install test test-coverage clean lint format

help:
	@echo "🛠️  EAVT Helper Development Commands"
	@echo "=================================="
	@echo "make install        - Install package in development mode"  
	@echo "make test           - Run all tests"
	@echo "make test-coverage  - Run tests with coverage report"
	@echo "make lint           - Run code linting"
	@echo "make format         - Format code with black"
	@echo "make clean          - Clean up build artifacts"

install:
	@echo "📦 Installing EAVT Helper in development mode..."
	pip install --editable .[dev]

test:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v

test-coverage:
	@echo "🧪 Running tests with coverage..."
	python -m pytest tests/ -v --cov=eavt_helper --cov-report=term-missing --cov-report=html

lint:
	@echo "🔍 Running code linting..."
	flake8 eavt_helper/ tests/ --max-line-length=100 --ignore=E203,W503

format:
	@echo "🎨 Formatting code with black..."
	black eavt_helper/ tests/ --line-length=100

clean:
	@echo "🧹 Cleaning up build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 