.PHONY: up down restart logs status clean

up: ## Start the full observability stack
	docker compose up -d

down: ## Stop the full observability stack
	docker compose down

restart: ## Restart the full observability stack
	docker compose down
	docker compose up -d

logs: ## Tail logs from all services
	docker compose logs -f

status: ## Show status of all services
	docker compose ps

clean: ## Stop stack and remove all volumes
	docker compose down -v
	docker volume prune -f

build: ## Rebuild the ai-analyzer image
	docker compose build ai-analyzer

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
