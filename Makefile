.PHONY: help run test lint fmt clean clean-venv install install-gpu setup-venv verify-gpu setup-gpu-full

# Python configuration
PYTHON_VERSION := 3.12.8
PYTHON_312 := C:\Users\John\.pyenv\pyenv-win\versions\$(PYTHON_VERSION)\python.exe

help: ## Show this help message
	@echo Available commands:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dependencies (without PyTorch GPU)
	python -m pip install --upgrade pip
	pip install -e .[dev]

install-gpu: ## Install PyTorch with CUDA 12.1 support
	@echo "Installing PyTorch with CUDA 12.1 support..."
	pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
	@echo "PyTorch installation complete!"

setup-venv: ## Create new venv with Python 3.12.8
	@echo "Creating virtual environment with Python 3.12.8..."
	@if exist .venv rmdir /s /q .venv
	$(PYTHON_312) -m venv .venv
	@echo "Virtual environment created!"
	@echo "Activate with: .venv\Scripts\activate"

verify-gpu: ## Verify GPU setup for embeddings
	python verify_gpu.py

setup-gpu-full: ## Complete GPU setup: create venv, install deps, install PyTorch GPU
	@echo "========================================"
	@echo "Starting complete GPU setup..."
	@echo "========================================"
	@echo ""
	@echo "Step 1: Creating virtual environment with Python 3.12.8..."
	@if exist .venv rmdir /s /q .venv
	$(PYTHON_312) -m venv .venv
	@echo ""
	@echo "Step 2: Activating venv and upgrading pip..."
	.venv\Scripts\python.exe -m pip install --upgrade pip
	@echo ""
	@echo "Step 3: Installing project dependencies..."
	.venv\Scripts\pip.exe install -e .[dev]
	@echo ""
	@echo "Step 4: Installing PyTorch with CUDA 12.1..."
	.venv\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
	@echo ""
	@echo "========================================"
	@echo "Setup complete!"
	@echo "========================================"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate venv: .venv\Scripts\activate"
	@echo "  2. Verify GPU: make verify-gpu"
	@echo "  3. Run your code: make run"

run: ## Run the application
	python src/main.py

test: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linter
	pylint src/

fmt: ## Format code
	black src/ tests/

clean: ## Clean cache and coverage files
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .coverage del /q .coverage
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist storage rmdir /s /q storage
	@if exist chroma_db rmdir /s /q chroma_db
	@echo "Cleaned cache and coverage files"

clean-venv: ## Remove virtual environment
	@if exist .venv rmdir /s /q .venv
	@echo "Virtual environment removed"

.DEFAULT_GOAL := help
