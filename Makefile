PYTHON  ?= python3.12
export VERSION:=$(shell jq '.version' package.json)

UNAME_S := $(shell uname -s)

.PHONY: all install init init_py init_npm up dev help

all: init

install:
ifeq ($(UNAME_S),Darwin)
	@echo "macOS: python@3.12, node, jq (brew)"
	brew install python@3.12 node jq || true
else
	@echo "Linux: python3.12-venv, npm, jq (apt)"
	sudo apt update || true
	sudo apt install -y python3.12-venv npm jq
endif

init: init_py init_npm
	mkdir -p logs

init_py:
	@echo "| VENV INIT |"
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

init_npm:
	@echo "| NPM  INIT |"
	cd serviz/frontend && npm ci && npm run build

up:
	@echo "VERSION=$(VERSION)"
	. venv/bin/activate && honcho start

# npm install to update packages
dev:
	cd serviz/frontend && npm run dev

help:
	@printf '%s\n' 'make install  - системные пакеты (python3.12, node, jq)'
	@printf '%s\n' 'make init     - venv + pip install + npm ci + сборка фронта'
	@printf '%s\n' 'make up       - запуск всех сервисов локально через honcho'
	@printf '%s\n' 'make dev      - фронт в dev-режиме (Vite HMR)'
