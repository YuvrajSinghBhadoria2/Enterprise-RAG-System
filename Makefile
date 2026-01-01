.PHONY: build up down logs ingest eval run-local

# Docker commands
build:
	docker-compose -f docker/docker-compose.yml --env-file .env build

up:
	docker-compose -f docker/docker-compose.yml --env-file .env up -d --build

down:
	docker-compose -f docker/docker-compose.yml --env-file .env down

logs:
	docker-compose -f docker/docker-compose.yml --env-file .env logs -f

api-shell:
	docker-compose -f docker/docker-compose.yml --env-file .env exec api /bin/bash

# Run evaluation inside Docker
eval:
	docker-compose -f docker/docker-compose.yml --env-file .env exec api python3 tools/run_eval.py

# Run evaluation locally (Mac fallback)
eval-local:
	export DISABLE_FAISS=1 && export KMP_DUPLICATE_LIB_OK=TRUE && export GROQ_API_KEY=${GROQ_API_KEY} && python3 tools/run_eval.py

# Ingestion (runs locally if venv active, or use via docker exec)
ingest:
	export PYTHONPATH=$$PYTHONPATH:. && python3 src/ingestion/ingest.py

# Data generation
generate-data:
	python3 tools/generate-dataset.py

# Run API and UI locally (Mac fallback)
run-local:
	@echo "Starting Enterprise RAG Locally (Safe Mode)..."
	@export DISABLE_FAISS=1 && export KMP_DUPLICATE_LIB_OK=TRUE && export GROQ_API_KEY=${GROQ_API_KEY} && \
	(uvicorn src.app.main:app --host 0.0.0.0 --port 8000 &) && \
	(sleep 5 && streamlit run src/ui/app.py --server.port 8501)
