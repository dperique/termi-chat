
# This goes to my docker hub account; change it if you want to
# push to your own account.
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

# targets for Docker and Podman engines
use-docker:
	@$(eval ENGINE := docker)
	@echo "Using Docker"

use-podman:
	@$(eval ENGINE := podman)
	@echo "Using Podman"

