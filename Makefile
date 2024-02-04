# Makefile for building and pushing Docker images using Docker or Podman

# Variables
IMAGE_NAME := dperique/termi-chat
VERSION := $(shell cat VERSION)
ENGINE := podman # Default to docker, change to podman if needed

.PHONY: build push all

# Default target
all: build push

build:
	@echo "Building Docker image with version $(VERSION) using $(ENGINE)"
	@$(ENGINE) build -t $(IMAGE_NAME):$(VERSION) .

push:
	@echo "Pushing Docker image with version $(VERSION) using $(ENGINE)"
	@$(ENGINE) push $(IMAGE_NAME):$(VERSION)

# Utility targets to switch between Docker and Podman
use-docker:
	@$(eval ENGINE := docker)
	@echo "Container engine set to Docker"

use-podman:
	@$(eval ENGINE := podman)
	@echo "Container engine set to Podman"

