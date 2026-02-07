.PHONY: help run test lint fmt clean install

help: ## Show this help message
	@echo Available commands:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

run: ## Run the application
	python src/main.py

test: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linter
	pylint src/

fmt: ## Format code
	black src/ tests/

clean: ## Clean cache and coverage files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf storage/ chroma_db/

.DEFAULT_GOAL := help
