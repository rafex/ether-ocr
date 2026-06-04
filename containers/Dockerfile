# Dockerfile — ether-ocr OCR engine
# Multi-stage build: slim runtime with Tesseract + Poppler + Python

# ─── Base stage ──────────────────────────────────────────────
FROM python:3.11-slim AS base

# Install system dependencies: Poppler (pdftotext + pdfimages) + Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Verify installations
RUN pdftotext -v 2>&1 | head -1 && \
    tesseract --version 2>&1 | head -1

# ─── Builder stage ───────────────────────────────────────────
FROM base AS builder

WORKDIR /build

# Install Python dependencies into a virtual environment
COPY python/pyproject.toml python/README.md ./
COPY python/src/ ./src/

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -e '.[ocr,api]'

# ─── Runtime stage ───────────────────────────────────────────
FROM base AS runtime

WORKDIR /workspace

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/workspace/python/src"

# Copy project files
COPY python/ ./python/
COPY scripts/ ./scripts/

# Create data directories
RUN mkdir -p /data/input /data/output

# Default command: start the REST API server
EXPOSE 8000
CMD ["python3", "-m", "ether_ocr.api.server"]
