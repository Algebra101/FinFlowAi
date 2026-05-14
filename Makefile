# FinCore AI — Makefile
# Quick commands for development and deployment.
#
# Usage:
#   make dev          — Start all services locally (no Docker)
#   make docker-up    — Start all services via Docker Compose
#   make docker-down  — Stop all Docker services
#   make test         — Run test scripts
#   make seed         — Seed the database with dummy data
#   make clean        — Remove generated files

.PHONY: dev docker-up docker-down test seed clean

# Start all microservices locally (for development without Docker)
dev:
	@echo "Starting FinCore AI Microservices..."
	@start /B python services/payment-service/src/main.py
	@start /B python services/banking-service/src/main.py
	@start /B python services/fraud-service/src/main.py
	@start /B python services/credit-service/src/main.py
	@start /B python services/forecasting-service/src/main.py
	@start /B python services/identity-service/src/main.py
	@timeout /t 2 >nul
	@python services/api-gateway/src/main.py

# Docker commands
docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

# Run tests
test:
	python scripts/test_webhook.py
	python scripts/test_transfer.py

# Seed database
seed:
	python scripts/seed.py

# Generate synthetic training data
generate-data:
	python ml/synthetic-data-engine/generators/generate_sme_data.py

# Clean generated files
clean:
	del /q fincore.db 2>nul
	del /q sme_training_data.csv 2>nul
