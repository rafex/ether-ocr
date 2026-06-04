# docker.mk — Reusable Docker rules for Makefile
# Included by the root Makefile via: include scripts/mk/docker.mk

DOCKER_IMAGE ?= ether-ocr
DOCKER_TAG ?= latest
DOCKERFILE ?= containers/Dockerfile

.PHONY: docker-build-verbose docker-clean docker-shell

docker-build-verbose: ## Build Docker image with full output
	@echo "==> Building $(DOCKER_IMAGE):$(DOCKER_TAG)"
	docker build \
		-t "$(DOCKER_IMAGE):$(DOCKER_TAG)" \
		-f "$(DOCKERFILE)" \
		"$(ROOT_DIR)"

docker-clean: ## Remove Docker image
	@echo "==> Removing $(DOCKER_IMAGE):$(DOCKER_TAG)"
	docker rmi "$(DOCKER_IMAGE):$(DOCKER_TAG)" 2>/dev/null || true

docker-shell: ## Open a shell inside the Docker container
	@echo "==> Opening shell in $(DOCKER_IMAGE):$(DOCKER_TAG)"
	docker run --rm -it \
		-v "$(ROOT_DIR):/workspace" \
		"$(DOCKER_IMAGE):$(DOCKER_TAG)" \
		/bin/bash
