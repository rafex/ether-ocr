# Justfile — Task runner for ether-ocr
# This file only orchestrates scripts. No inline logic.
# Projects: ether-core-ocr, ether-api-ocr, ether-cli-ocr, ether-mcp-ocr

set shell := ["bash", "-c"]

root_dir := justfile_directory()

# ─── Default recipe ───────────────────────────────────────────
default: list

list:
    @just --list

# ─── Development tasks ────────────────────────────────────────

build:
    @echo "==> Building ether-ocr packages"
    python3 "{{root_dir}}/scripts/python/build.py"

test:
    @echo "==> Running tests"
    python3 "{{root_dir}}/scripts/python/test.py"

lint:
    @echo "==> Running linter"
    python3 "{{root_dir}}/scripts/python/lint.py"

api:
    @echo "==> Starting ether-ocr API server"
    PYTHONPATH="{{root_dir}}/python/ether-core-ocr/src:{{root_dir}}/python/ether-api-ocr/src" \
    python3 -m ether_ocr_api.server

mcp:
    @echo "==> Starting ether-ocr MCP server (stdio)"
    PYTHONPATH="{{root_dir}}/python/ether-mcp-ocr/src" \
    python3 -m ether_ocr_mcp.server --transport stdio

mcp-http:
    @echo "==> Starting ether-ocr MCP server (HTTP :9001)"
    PYTHONPATH="{{root_dir}}/python/ether-mcp-ocr/src" \
    python3 -m ether_ocr_mcp.server --transport http --port 9001

# ─── OCR tasks ────────────────────────────────────────────────

ocr input output:
    @echo "==> Running OCR on {{input}} -> {{output}}"
    python3 "{{root_dir}}/scripts/python/ocr.py" "{{input}}" "{{output}}"

ocr-image input output:
    @echo "==> Running OCR on image {{input}} -> {{output}}"
    python3 "{{root_dir}}/scripts/python/ocr.py" --image "{{input}}" "{{output}}"

# ─── Docker tasks ─────────────────────────────────────────────

docker-build:
    @echo "==> Building Docker image"
    bash "{{root_dir}}/scripts/shellscript/docker-build.sh"

docker-run input output='ocr_output.txt':
    @echo "==> Running OCR in Docker container"
    bash "{{root_dir}}/scripts/shellscript/docker-run.sh" "{{input}}" "{{output}}"

docker-api:
    @echo "==> Starting ether-ocr API in Docker"
    docker compose -f "{{root_dir}}/containers/docker-compose.yml" up -d

docker-push:
    @echo "==> Pushing Docker image"
    bash "{{root_dir}}/scripts/shellscript/docker-push.sh"

# ─── Utility tasks ────────────────────────────────────────────

setup:
    @echo "==> Installing system dependencies"
    bash "{{root_dir}}/scripts/shellscript/setup.sh"

clean:
    @echo "==> Cleaning build artifacts"
    rm -rf python/*/build python/*/dist python/*/*.egg-info
    rm -rf .pytest_cache python/*/.pytest_cache
    find python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find python -type f -name '*.pyc' -delete 2>/dev/null || true

import 'scripts/just/dev.just'
import 'scripts/just/docker.just'
