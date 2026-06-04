#!/usr/bin/env bash
# docker-push.sh — Push the ether-ocr Docker image to a registry
set -euo pipefail

IMAGE_NAME="${DOCKER_IMAGE:-ether-ocr}"
IMAGE_TAG="${DOCKER_TAG:-latest}"
REGISTRY="${DOCKER_REGISTRY:-}"

FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
if [ -n "$REGISTRY" ]; then
  FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
  echo "==> Tagging image for registry: ${FULL_IMAGE}"
  docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${FULL_IMAGE}"
fi

echo "==> Pushing Docker image: ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

echo "==> Image pushed: ${FULL_IMAGE}"
