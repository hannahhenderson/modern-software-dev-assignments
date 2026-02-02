.PHONY: help install dev test lint format typecheck clean run-server run-web run-client docker-up docker-down

# Default target
help:
	@echo "Petting Zootopia - Available commands:"
	@echo ""
	@echo "  Setup:"
	@echo "    make install     Install production dependencies"
	@echo "    make dev         Install all dependencies (including dev tools)"
	@echo ""
	@echo "  Run:"
	@echo "    make run-server  Start the MCP server"
	@echo "    make run-web     Start the web server (http://localhost:8000)"
	@echo "    make run-client  Start interactive CLI client"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-up   Start all services with Docker Compose"
	@echo "    make docker-down Stop Docker services"
	@echo ""
	@echo "  Quality:"
	@echo "    make test        Run tests"
	@echo "    make lint        Run linter (ruff)"
	@echo "    make format      Format code (ruff)"
	@echo "    make typecheck   Run type checker (mypy)"
	@echo ""
	@echo "  Cleanup:"
	@echo "    make clean       Remove build artifacts and caches"

# Setup
install:
	pip install -e .

dev:
	pip install -e ".[dev]"

# Run
run-server:
	python -m petting_zootopia.server

run-web:
	python -m petting_zootopia.web

run-client:
	python -m petting_zootopia.client src/petting_zootopia/server.py

# Docker
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

# Quality
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=petting_zootopia --cov-report=term-missing

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/petting_zootopia/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/petting_zootopia/__pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
