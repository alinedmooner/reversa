
# ==============================================================================
# Installation & Setup
# ==============================================================================

# Install dependencies with pip into the active environment (pyenv: reversa).
# Nota: esta máquina no usa uv; CI (GitHub Actions) sí usa uv con uv.lock.
install:
	pip install -e .
	pip install "pytest>=8.3.4,<9.0.0" "pytest-asyncio>=0.23.8,<1.0.0" nest-asyncio

# ==============================================================================
# Playground Targets
# ==============================================================================

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try (BR): Caí no golpe do falso parente, fiz um Pix de R\$$ 50.000 para   |"
	@echo "|        a chave 123.456.789-09 há 10 minutos.                                |"
	@echo "| 💡 Try (CO): Me hicieron un secuestro relámpago, transferí \$$11.000.000 a   |"
	@echo "|        la llave 3001234567 hace 10 minutos.                                 |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	adk web . --port 8501 --reload_agents

# ==============================================================================
# A2A Protocol Inspector
# ==============================================================================

# Launch A2A Protocol Inspector to test your agent implementation
inspector: setup-inspector-if-needed build-inspector-if-needed
	@echo "==============================================================================="
	@echo "| 🔍 A2A Protocol Inspector                                                  |"
	@echo "==============================================================================="
	@echo "| 🌐 Inspector UI: http://localhost:5001                                     |"
	@echo "|                                                                             |"
	@echo "| 💡 Testing Remote Deployment:                                               |"
	@echo "|    Use the Agent Card URL from 'make deploy' output                        |"
	@echo "|                                                                             |"
	@echo "|    🔐 Auth: Expand 'Authentication & Headers', select 'Bearer Token',       |"
	@echo "|       and paste output of: gcloud auth print-access-token                  |"
	@echo "|                                                                             |"
	@echo "| ℹ️  Note: Local testing requires deploying to Agent Engine first.          |"
	@echo "==============================================================================="
	@echo ""
	cd tools/a2a-inspector/backend && uv run app.py

# Internal: Setup inspector if not already present (runs once)
# Note: a2a-inspector has no tagged releases yet; pinned to commit 893e406.
setup-inspector-if-needed:
	@if [ ! -d "tools/a2a-inspector" ]; then \
		echo "" && \
		echo "📦 First-time setup: Installing A2A Inspector..." && \
		echo "" && \
		mkdir -p tools && \
		git clone --quiet https://github.com/a2aproject/a2a-inspector.git tools/a2a-inspector && \
		(cd tools/a2a-inspector && git -c advice.detachedHead=false checkout --quiet 893e4062f6fbd85a8369228ce862ebbf4a025694) && \
		echo "📥 Installing Python dependencies..." && \
		(cd tools/a2a-inspector && uv sync --quiet) && \
		echo "📥 Installing Node.js dependencies..." && \
		(cd tools/a2a-inspector/frontend && npm install --silent) && \
		echo "🔨 Building frontend..." && \
		(cd tools/a2a-inspector/frontend && npm run build --silent) && \
		echo "" && \
		echo "✅ A2A Inspector setup complete!" && \
		echo ""; \
	fi

# Internal: Build inspector frontend if needed
build-inspector-if-needed:
	@if [ -d "tools/a2a-inspector" ] && [ ! -f "tools/a2a-inspector/frontend/public/script.js" ]; then \
		echo "🔨 Building inspector frontend..."; \
		cd tools/a2a-inspector/frontend && npm run build; \
	fi

# ==============================================================================
# Backend Deployment Targets
# ==============================================================================

# Deploy the agent remotely
# Usage: make deploy [AGENT_IDENTITY=true] [SECRETS="KEY=SECRET_ID,..."] - Set AGENT_IDENTITY=true to enable per-agent IAM identity (Preview)
deploy:
	# Stage limpio del paquete: el tarball de vertexai empaqueta TODO el
	# directorio (incluye .env y __pycache__ si no se excluyen) y guarda los
	# paths TAL CUAL se pasan (tar.add), así que el deploy corre DESDE el stage
	# para que el paquete viaje como app/... Requirements explícitos del
	# contenedor (LESSONS.md): google-adk[a2a] + pins otel.
	rm -rf .deploy_src && mkdir -p .deploy_src && \
	rsync -a --exclude='.env' --exclude='__pycache__' --exclude='.requirements.txt' app/ .deploy_src/app/ && \
	cp app/requirements.txt .deploy_src/app/app_utils/.requirements.txt && \
	(cd .deploy_src && python -m app.app_utils.deploy \
		--source-packages=./app \
		--entrypoint-module=app.agent_engine_app \
		--entrypoint-object=agent_engine \
		--requirements-file=app/app_utils/.requirements.txt \
		$(if $(AGENT_IDENTITY),--agent-identity) \
		$(if $(filter command line,$(origin SECRETS)),--set-secrets="$(SECRETS)")) && \
	cp .deploy_src/deployment_metadata.json deployment_metadata.json

# Alias for 'make deploy' for backward compatibility
backend: deploy

# ==============================================================================
# Infrastructure Setup
# ==============================================================================

# Set up development environment resources using Terraform
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# Testing & Code Quality
# ==============================================================================

# Run unit tests (gate local; no requiere GCP)
test:
	pytest tests/unit

# Run integration tests (requiere proyecto GCP + auth Vertex activos)
test-integration:
	pytest tests/integration

# ==============================================================================
# Agent Evaluation
# ==============================================================================

# Run agent evaluation using ADK eval
# Usage: make eval [EVALSET=tests/eval/evalsets/basic.evalset.json] [EVAL_CONFIG=tests/eval/eval_config.json]
eval:
	@echo "==============================================================================="
	@echo "| Running Agent Evaluation                                                    |"
	@echo "==============================================================================="
	pip install --quiet ".[eval]"
	adk eval ./app $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,))

# Run evaluation with all evalsets
eval-all:
	@echo "==============================================================================="
	@echo "| Running All Evalsets                                                        |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ Running: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ All evalsets completed"

# Run code quality checks (codespell, ruff, ty)
lint:
	pip install --quiet ".[lint]"
	codespell
	ruff check . --diff
	ruff format . --check --diff
	ty check .