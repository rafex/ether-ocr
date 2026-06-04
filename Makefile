# Makefile — Build orchestrator for ether-ocr
# This file only orchestrates scripts. No inline logic.
# Scripts live in: scripts/mk/ and scripts/shellscript/

SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: help build test lint api docker-build docker-push clean

# ─── Default target ───────────────────────────────────────────
.DEFAULT_GOAL := help

help: ## Show this help
	@echo "ether-ocr — OCR pipeline build orchestrator"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ─── Development targets ──────────────────────────────────────

build: ## Build the Python package
	@echo "==> Building ether-ocr package"
	python3 "$(ROOT_DIR)/scripts/python/build.py"

test: ## Run test suite
	@echo "==> Running tests"
	python3 "$(ROOT_DIR)/scripts/python/test.py"

lint: ## Lint and format check
	@echo "==> Running linter"
	python3 "$(ROOT_DIR)/scripts/python/lint.py"

api: ## Start the REST API server
	@echo "==> Starting ether-ocr API server"
	python3 "$(ROOT_DIR)/scripts/python/api.py"

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

docker-push: ## Push Docker image to registry
	@echo "==> Pushing Docker image"
	bash "$(ROOT_DIR)/scripts/shellscript/docker-push.sh"

# ─── Utility targets ──────────────────────────────────────────

setup: ## Install system dependencies (macOS or Debian/Ubuntu)
	@echo "==> Installing system dependencies"
	bash "$(ROOT_DIR)/scripts/shellscript/setup.sh"

clean: ## Clean build artifacts
	@echo "==> Cleaning build artifacts"
	rm -rf python/build python/dist python/*.egg-info
	rm -rf .pytest_cache python/.pytest_cache
	find python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find python -type f -name '*.pyc' -delete 2>/dev/null || true

# ─── Include reusable Make rules ──────────────────────────────
include scripts/mk/docker.mk
