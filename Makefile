# Makefile — Build orchestrator for ether-ocr
# This file only orchestrates scripts. No inline logic.
# Projects: ether-core-ocr, ether-api-ocr, ether-cli-ocr, ether-mcp-ocr

SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: help build test lint api mcp docker-build docker-up docker-down docker-push clean

.DEFAULT_GOAL := help

help: ## Show this help
	@echo "ether-ocr — OCR pipeline build orchestrator"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ─── Development targets ──────────────────────────────────────

build: ## Build all Python packages
	@echo "==> Building ether-ocr packages"
	python3 "$(ROOT_DIR)/scripts/python/build.py"

test: ## Run test suite (all packages)
	@echo "==> Running tests"
	python3 "$(ROOT_DIR)/scripts/python/test.py"

lint: ## Lint and format check
	@echo "==> Running linter"
	python3 "$(ROOT_DIR)/scripts/python/lint.py"

api: ## Start the REST API server
	@echo "==> Starting ether-ocr API server"
	PYTHONPATH="$(ROOT_DIR)/python/ether-core-ocr/src:$(ROOT_DIR)/python/ether-api-ocr/src" \
	python3 -m ether_ocr_api.server

mcp: ## Start the MCP server (stdio)
	@echo "==> Starting ether-ocr MCP server (stdio)"
	PYTHONPATH="$(ROOT_DIR)/python/ether-mcp-ocr/src" \
	python3 -m ether_ocr_mcp.server --transport stdio

mcp-http: ## Start the MCP server (HTTP :9001)
	@echo "==> Starting ether-ocr MCP server (HTTP :9001)"
	PYTHONPATH="$(ROOT_DIR)/python/ether-mcp-ocr/src" \
	python3 -m ether_ocr_mcp.server --transport http --port 9001

# ─── OCR targets ──────────────────────────────────────────────

ocr: ## Run OCR on a file (args: INPUT=file.pdf OUTPUT=out.txt)
	@echo "==> Running OCR on $(INPUT) -> $(OUTPUT)"
	python3 "$(ROOT_DIR)/scripts/python/ocr.py" "$(INPUT)" "$(OUTPUT)"

ocr-image: ## Run OCR on an image (args: INPUT=scan.png OUTPUT=out.txt)
	@echo "==> Running OCR on image $(INPUT) -> $(OUTPUT)"
	python3 "$(ROOT_DIR)/scripts/python/ocr.py" --image "$(INPUT)" "$(OUTPUT)"

# ─── Docker targets ───────────────────────────────────────────

docker-build: ## Build Docker image
	@echo "==> Building Docker image"
	bash "$(ROOT_DIR)/scripts/shellscript/docker-build.sh"

docker-up: ## Start API + MCP with Docker Compose
	@echo "==> Starting ether-ocr via Docker Compose"
	docker compose -f "$(ROOT_DIR)/containers/docker-compose.yml" up -d

docker-down: ## Stop Docker Compose services
	@echo "==> Stopping ether-ocr"
	docker compose -f "$(ROOT_DIR)/containers/docker-compose.yml" down

docker-push: ## Push Docker image to registry
	@echo "==> Pushing Docker image"
	bash "$(ROOT_DIR)/scripts/shellscript/docker-push.sh"

# ─── Utility targets ──────────────────────────────────────────

setup: ## Install system dependencies (macOS or Debian/Ubuntu)
	@echo "==> Installing system dependencies"
	bash "$(ROOT_DIR)/scripts/shellscript/setup.sh"

clean: ## Clean build artifacts
	@echo "==> Cleaning build artifacts"
	rm -rf python/*/build python/*/dist python/*/*.egg-info
	rm -rf .pytest_cache python/*/.pytest_cache
	find python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find python -type f -name '*.pyc' -delete 2>/dev/null || true

include scripts/mk/docker.mk
