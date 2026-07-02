# Dockerfile — ether-ocr OCR engine
# Multi-stage build: slim runtime with Tesseract + Poppler + Python
# Installs 4 packages: core, api, cli, mcp

# ─── Base stage ──────────────────────────────────────────────
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

RUN pdftotext -v 2>&1 | head -1 && \
    tesseract --version 2>&1 | head -1

# ─── Builder stage ───────────────────────────────────────────
FROM base AS builder

WORKDIR /build

COPY python/ether-core-ocr/ ./ether-core-ocr/
COPY python/ether-api-ocr/   ./ether-api-ocr/
COPY python/ether-cli-ocr/   ./ether-cli-ocr/
COPY python/ether-mcp-ocr/   ./ether-mcp-ocr/

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir \
    ./ether-core-ocr/ \
    ./ether-api-ocr/ \
    ./ether-cli-ocr/ \
    ./ether-mcp-ocr/

# ─── Runtime stage ───────────────────────────────────────────
FROM base AS runtime

WORKDIR /workspace

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY python/ ./python/
COPY scripts/ ./scripts/

RUN mkdir -p /data/input /data/output

EXPOSE 8000 9001

CMD ["bash", "scripts/shellscript/entrypoint.sh"]
