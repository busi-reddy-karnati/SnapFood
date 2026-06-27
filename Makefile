# SnapFood – local development convenience targets
# Usage: make <target>

ANDROID_HOME  := $(HOME)/Android/sdk
FLUTTER       := $(HOME)/development/flutter/bin/flutter
PATH          := $(ANDROID_HOME)/emulator:$(ANDROID_HOME)/platform-tools:$(ANDROID_HOME)/cmdline-tools/latest/bin:$(HOME)/development/flutter/bin:$(PATH)

export ANDROID_HOME
export PATH

# Use absolute paths so targets work from any CWD
ROOT          := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND_DIR   := $(ROOT)/backend
VENV          := $(BACKEND_DIR)/.venv
PYTHON        := $(VENV)/bin/python3
PIP           := $(VENV)/bin/pip
DATABASE_URL  := postgresql+asyncpg://busi-reddy-karnati@/snapfood?host=/var/run/postgresql
DATABASE_URL_PSYCOPG2 := postgresql://busi-reddy-karnati@/snapfood?host=/var/run/postgresql
BACKEND_PID   := /tmp/snapfood-backend.pid
APP_DIR       := $(ROOT)/app
API_BASE_URL  := http://10.0.2.2:8000
EMULATOR_AVD  := SnapFood_Pixel6

.PHONY: setup-backend migrate seed backend backend-bg stop-backend \
        setup-app emulator run-app setup health

## setup-backend: create venv, install deps, copy .env if missing
setup-backend:
	@echo "==> Setting up backend..."
	@if [ ! -d "$(VENV)" ]; then \
		POETRY_PYTHON=$$(ls $$HOME/.cache/pypoetry/virtualenvs/*/bin/python3 2>/dev/null | head -1); \
		if [ -n "$$POETRY_PYTHON" ]; then \
			$$POETRY_PYTHON -m virtualenv $(VENV); \
		else \
			python3 -m venv $(VENV); \
		fi; \
	fi
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	$(PIP) install psycopg2-binary
	@if [ ! -f "$(BACKEND_DIR)/.env" ]; then \
		cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env; \
		echo ""; \
		echo "  *** Copied .env.example to .env — please fill in GEMINI_API_KEY ***"; \
		echo ""; \
	fi
	@echo "Backend setup complete."

## migrate: run alembic migrations
migrate:
	@echo "==> Running migrations..."
	cd $(BACKEND_DIR) && DATABASE_URL="$(DATABASE_URL)" $(VENV)/bin/alembic upgrade head

## seed: populate the database with demo data
seed:
	@echo "==> Seeding database..."
	cd $(BACKEND_DIR) && DATABASE_URL="$(DATABASE_URL)" $(PYTHON) seed.py

## backend: start uvicorn in foreground (Ctrl-C to stop)
backend:
	@echo "==> Starting backend on http://localhost:8000 ..."
	cd $(BACKEND_DIR) && DATABASE_URL="$(DATABASE_URL)" \
		$(VENV)/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## backend-bg: start uvicorn in background, PID saved to $(BACKEND_PID)
backend-bg:
	@echo "==> Starting backend in background..."
	@if [ -f "$(BACKEND_PID)" ] && kill -0 $$(cat $(BACKEND_PID)) 2>/dev/null; then \
		echo "Backend already running (PID=$$(cat $(BACKEND_PID)))."; \
	else \
		cd $(BACKEND_DIR) && DATABASE_URL="$(DATABASE_URL)" \
			$(VENV)/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 \
			> /tmp/snapfood-backend.log 2>&1 & \
		echo $$! > $(BACKEND_PID); \
		echo "Backend started (PID=$$(cat $(BACKEND_PID))). Logs: /tmp/snapfood-backend.log"; \
	fi

## stop-backend: stop the background uvicorn process
stop-backend:
	@if [ -f "$(BACKEND_PID)" ]; then \
		PID=$$(cat $(BACKEND_PID)); \
		if kill -0 $$PID 2>/dev/null; then \
			kill $$PID && echo "Stopped backend (PID=$$PID)."; \
		else \
			echo "No running process at PID=$$PID."; \
		fi; \
		rm -f $(BACKEND_PID); \
	else \
		echo "No PID file found at $(BACKEND_PID)."; \
	fi

## setup-app: run flutter pub get
setup-app:
	@echo "==> Running flutter pub get..."
	cd $(APP_DIR) && $(FLUTTER) pub get

## emulator: start the SnapFood Android emulator headless in background
emulator:
	@echo "==> Starting emulator $(EMULATOR_AVD) in background..."
	$(ANDROID_HOME)/emulator/emulator -avd $(EMULATOR_AVD) \
		-no-audio -no-boot-anim -no-snapshot-load -gpu swiftshader_indirect \
		> /tmp/snapfood-emulator.log 2>&1 &
	@echo "Emulator starting. Logs: /tmp/snapfood-emulator.log"
	@echo "Wait ~2 min then run: make run-app"

## run-app: build and run SnapFood on the emulator
run-app:
	@echo "==> Running SnapFood on emulator..."
	cd $(APP_DIR) && $(FLUTTER) run \
		--dart-define=API_BASE_URL=$(API_BASE_URL) \
		-d emulator-5554

## setup: full first-time setup (backend + db + seed + flutter)
setup: setup-backend migrate seed setup-app
	@echo ""
	@echo "==> Full setup complete. Next steps:"
	@echo "   make backend-bg   # start backend in background"
	@echo "   make emulator     # start Android emulator (wait ~2 min)"
	@echo "   make run-app      # build and run the app"
	@echo "   make health       # check backend is up"

## health: check backend health endpoint
health:
	@echo "==> Checking backend health..."
	curl -sf http://localhost:8000/api/v1/health && echo "" || \
		(echo "Backend not responding. Try: make backend-bg" && exit 1)
