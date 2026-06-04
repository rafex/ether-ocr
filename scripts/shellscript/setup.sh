#!/usr/bin/env bash
# setup.sh — Install system dependencies for ether-ocr
set -euo pipefail

echo "==> Installing system dependencies for ether-ocr"

detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"
  elif command -v apt-get &>/dev/null; then
    echo "debian"
  elif command -v dnf &>/dev/null; then
    echo "fedora"
  elif command -v apk &>/dev/null; then
    echo "alpine"
  else
    echo "unknown"
  fi
}

OS=$(detect_os)
echo "    Detected OS: ${OS}"

case "$OS" in
  macos)
    echo "==> Installing via Homebrew..."
    brew install poppler tesseract tesseract-lang
    echo "==> Installing Python dependencies..."
    python3 -m pip install --upgrade pip
    python3 -m pip install pytesseract pdf2image pillow
    ;;
  debian)
    echo "==> Installing via apt..."
    sudo apt-get update
    sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
    python3 -m pip install --upgrade pip
    python3 -m pip install pytesseract pdf2image pillow
    ;;
  fedora)
    echo "==> Installing via dnf..."
    sudo dnf install -y poppler-utils tesseract tesseract-langpack-spa tesseract-langpack-eng
    python3 -m pip install --upgrade pip
    python3 -m pip install pytesseract pdf2image pillow
    ;;
  alpine)
    echo "==> Installing via apk..."
    sudo apk add poppler-utils tesseract-ocr tesseract-ocr-data-spa tesseract-ocr-data-eng
    python3 -m pip install --upgrade pip
    python3 -m pip install pytesseract pdf2image pillow
    ;;
  *)
    echo "ERROR: Unsupported OS. Please install manually:"
    echo "  - Poppler (pdftotext)"
    echo "  - Tesseract OCR + language data (spa, eng)"
    echo "  - Python packages: pytesseract pdf2image pillow"
    exit 1
    ;;
esac

echo ""
echo "==> Setup complete. Run 'make test' to verify installation."
echo ""
echo "Installed tools:"
echo "  pdftotext: $(command -v pdftotext 2>/dev/null || echo 'NOT FOUND')"
echo "  tesseract: $(command -v tesseract 2>/dev/null || echo 'NOT FOUND')"
