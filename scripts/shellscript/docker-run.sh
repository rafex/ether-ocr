#!/usr/bin/env bash
# docker-run.sh — Run ether-ocr CLI inside a Docker container
# Uses stdin/stdout for file transfer — works with local and remote Docker/Podman.
set -euo pipefail

IMAGE_NAME="${DOCKER_IMAGE:-ether-ocr}"
IMAGE_TAG="${DOCKER_TAG:-latest}"

INPUT="${1:-}"
OUTPUT="${2:-ocr_output.txt}"

if [ -z "$INPUT" ]; then
  echo "Usage: $0 <input.pdf|input.png> [output.txt]"
  echo ""
  echo "Runs OCR on the input file inside a Docker container."
  echo "  input   - PDF or image file to OCR"
  echo "  output  - Output text file (default: ocr_output.txt)"
  exit 1
fi

INPUT_ABS="$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "$INPUT")"
INPUT_NAME="$(basename "$INPUT_ABS")"
INPUT_EXT="${INPUT_NAME##*.}"

echo "==> Running OCR in Docker container"
echo "    Input:  ${INPUT_ABS}"
echo "    Output: ${OUTPUT}"
echo "    Image:  ${IMAGE_NAME}:${IMAGE_TAG}"

cat "$INPUT_ABS" | docker run --rm -i \
  "${IMAGE_NAME}:${IMAGE_TAG}" \
  python3 -c "
import sys, tempfile
from pathlib import Path
from ether_ocr_core.pipeline import ocr_document

data = sys.stdin.buffer.read()

with tempfile.NamedTemporaryFile(suffix='.${INPUT_EXT}', delete=False) as tmp:
    tmp.write(data)
    tmp_path = tmp.name

out_path = Path('/tmp/ocr_output.txt')

try:
    result = ocr_document(Path(tmp_path), out_path)
    print(f'Pages: {result.pages}', file=sys.stderr)
    print(f'Paragraphs: {result.paragraphs}', file=sys.stderr)
    print(f'Size: {result.size_bytes / 1024:.1f} KB', file=sys.stderr)
    print(f'OCR used: {\"yes\" if result.used_ocr else \"no\"}', file=sys.stderr)
    sys.stdout.write(out_path.read_text(encoding='utf-8'))
finally:
    Path(tmp_path).unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
" > "$OUTPUT"

echo "==> OCR complete. Output: ${OUTPUT}"
