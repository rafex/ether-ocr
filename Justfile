# Justfile — Task runner for ether-ocr
# This file only orchestrates scripts. No inline logic.
# Scripts live in: scripts/just/ and scripts/python/

set shell := ["bash", "-c"]

root_dir := justfile_directory()

# ─── Default recipe ───────────────────────────────────────────
default: list

list:
    @just --list

# ─── Development tasks ────────────────────────────────────────

# Build the Python package
build:
    @echo "==> Building ether-ocr package"
    python3 "{{root_dir}}/scripts/python/build.py"

# Run test suite
test:
    @echo "==> Running tests"
    python3 "{{root_dir}}/scripts/python/test.py"

# Lint and format check
lint:
    @echo "==> Running linter"
    python3 "{{root_dir}}/scripts/python/lint.py"

# Start the REST API server
api:
    @echo "==> Starting ether-ocr API server"
    python3 "{{root_dir}}/scripts/python/api.py"

# ─── OCR tasks ────────────────────────────────────────────────

# Run OCR on a PDF or image file
ocr input output:
    @echo "==> Running OCR on {{input}} -> {{output}}"
    python3 "{{root_dir}}/scripts/python/ocr.py" "{{input}}" "{{output}}"

# Run OCR on an image file
ocr-image input output:
    @echo "==> Running OCR on image {{input}} -> {{output}}"
    python3 "{{root_dir}}/scripts/python/ocr.py" --image "{{input}}" "{{output}}"

# ─── Docker tasks ─────────────────────────────────────────────

# Build Docker image
docker-build:
    @echo "==> Building Docker image"
    bash "{{root_dir}}/scripts/shellscript/docker-build.sh"

# Run Docker container interactively
docker-run input output='ocr_output.txt':
    @echo "==> Running OCR in Docker container"
    bash "{{root_dir}}/scripts/shellscript/docker-run.sh" "{{input}}" "{{output}}"

# Start API server with Docker Compose
docker-api:
    @echo "==> Starting ether-ocr API in Docker"
    docker compose -f "{{root_dir}}/containers/docker-compose.yml" up -d

# Push Docker image to registry
docker-push:
    @echo "==> Pushing Docker image"
    bash "{{root_dir}}/scripts/shellscript/docker-push.sh"

# ─── Utility tasks ────────────────────────────────────────────

# Install system dependencies
setup:
    @echo "==> Installing system dependencies"
    bash "{{root_dir}}/scripts/shellscript/setup.sh"

# Clean build artifacts
clean:
    @echo "==> Cleaning build artifacts"
    rm -rf python/build python/dist python/*.egg-info
    rm -rf .pytest_cache python/.pytest_cache
    find python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find python -type f -name '*.pyc' -delete 2>/dev/null || true

# ─── Import reusable Just modules ─────────────────────────────
import 'scripts/just/dev.just'
import 'scripts/just/docker.just'
