# =============================================================================
# Thyroid Nodule Evaluation System - Makefile
# =============================================================================

.PHONY: help dev dev-build dev-down dev-logs prod prod-build prod-down prod-logs test clean

# Default target
help:
	@echo "Thyroid Nodule Evaluation System - Available Commands"
	@echo "======================================================"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make dev-logs     - View development logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production environment"
	@echo "  make prod-down    - Stop production environment"
	@echo "  make prod-logs    - View production logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run backend tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Remove all containers and volumes"
	@echo "  make shell        - Open shell in backend container"
	@echo "  make migrate      - Run database migrations"
	@echo "  make init-vectors - Initialize vector store from PDFs"

# -----------------------------------------------------------------------------
# Development Commands
# -----------------------------------------------------------------------------
dev:
	docker-compose up -d

dev-build:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

dev-down:
	docker-compose down

dev-logs:
	docker-compose logs -f

# -----------------------------------------------------------------------------
# Production Commands
# -----------------------------------------------------------------------------
prod:
	docker-compose -f docker-compose.prod.yml up -d

prod-build:
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.prod.yml build --no-cache
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# -----------------------------------------------------------------------------
# Testing Commands
# -----------------------------------------------------------------------------
test:
	docker-compose exec backend pytest -v

test-cov:
	docker-compose exec backend pytest --cov=thyroid --cov-report=term-missing

# -----------------------------------------------------------------------------
# Utility Commands
# -----------------------------------------------------------------------------
clean:
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
	docker system prune -f

shell:
	docker-compose exec backend /bin/bash

migrate:
	docker-compose exec backend python manage.py migrate

init-vectors:
	docker-compose exec -e INIT_VECTORSTORE=true backend python manage.py ingest_guides

# -----------------------------------------------------------------------------
# SSL Certificate Commands (Let's Encrypt)
# -----------------------------------------------------------------------------
ssl-init:
	@echo "Initializing SSL certificates with Let's Encrypt..."
	@echo "Make sure your domain points to this server and port 80 is accessible."
	docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
		--webroot --webroot-path=/var/www/certbot \
		--email your-email@example.com \
		--agree-tos --no-eff-email \
		-d your-domain.com

ssl-renew:
	docker-compose -f docker-compose.prod.yml run --rm certbot renew
	docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
