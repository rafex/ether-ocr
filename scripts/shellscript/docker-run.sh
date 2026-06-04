#!/usr/bin/env bash
# docker-run.sh — Run ether-ocr inside a Docker container
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
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

INPUT_ABS="$(realpath "$INPUT")"
INPUT_NAME="$(basename "$INPUT_ABS")"
INPUT_DIR="$(dirname "$INPUT_ABS")"

echo "==> Running OCR in Docker container"
echo "    Input:  ${INPUT_ABS}"
echo "    Output: ${OUTPUT}"
echo "    Image:  ${IMAGE_NAME}:${IMAGE_TAG}"

docker run --rm \
  -v "${INPUT_DIR}:/data/input:ro" \
  -v "${ROOT_DIR}:/data/output" \
  "${IMAGE_NAME}:${IMAGE_TAG}" \
  python3 -m ether_ocr ocr "/data/input/${INPUT_NAME}" "/data/output/${OUTPUT}"

echo "==> OCR complete. Output: ${ROOT_DIR}/${OUTPUT}"
