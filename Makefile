.DEFAULT_GOAL := build
.PHONY: build build.server build.client publish publish.server push.client

IMAGE ?= semoac/cronjob-manager-app
VERSION ?= $(shell git describe --tags --always --dirty)


build: build.server build.client

build.server:
	docker build -t "$(IMAGE):server-$(VERSION)" -t "$(IMAGE):server-latest" -f server/Dockerfile server

build.client:
	docker build -t "$(IMAGE):client-$(VERSION)" -t "$(IMAGE):client-latest" -f client/Dockerfile client

publish: publish.server publish.client
	docker push  "$(IMAGE):server-latest"
	docker push  "$(IMAGE):client-latest"

publish.server: build.server
	docker push "$(IMAGE):server-$(VERSION)"

publish.client: build.client
	docker push "$(IMAGE):client-$(VERSION)"