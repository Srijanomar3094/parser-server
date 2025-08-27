.PHONY: help install test run migrate clean docker-up docker-down docker-build

help: ## Show this help message
	@echo "Contract Intelligence Parser - Available Commands:"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

test: ## Run the test suite
	python manage.py test

run: ## Start the development server
	python manage.py runserver

migrate: ## Run database migrations
	python manage.py migrate

makemigrations: ## Create new migrations
	python manage.py makemigrations

clean: ## Clean up Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-build: ## Build and start Docker services
	docker-compose up --build -d

docker-logs: ## View Docker logs
	docker-compose logs -f

setup: ## Initial setup (install, migrate, create superuser)
	pip install -r requirements.txt
	python manage.py migrate
	python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

check-mongo: ## Test MongoDB connection
	python test_mongodb.py

dev: ## Start development environment
	@echo "Starting development environment..."
	@make docker-up
	@echo "Waiting for MongoDB to be ready..."
	@sleep 10
	@make setup
	@make run

