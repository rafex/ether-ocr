#!/usr/bin/env bash
# docker-build.sh — Build the ether-ocr Docker image
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKERFILE="${ROOT_DIR}/containers/Dockerfile"
IMAGE_NAME="${DOCKER_IMAGE:-ether-ocr}"
IMAGE_TAG="${DOCKER_TAG:-latest}"

echo "==> Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "    Dockerfile: ${DOCKERFILE}"
echo "    Context:    ${ROOT_DIR}"

docker build \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" \
  -f "${DOCKERFILE}" \
  "${ROOT_DIR}"

echo "==> Image built: ${IMAGE_NAME}:${IMAGE_TAG}"
