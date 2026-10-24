#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "================================================================"
echo "  The Localhost Company — OpenHUB 2026 Bootcamp Setup"
echo "================================================================"

# 1. Create required directories
mkdir -p config workspace skills tests prompts

# 2. Initialize Git inside ./workspace
if [ ! -d "workspace/.git" ]; then
  echo "[1/4] Inicializando repositorio Git en ./workspace..."
  git init workspace
else
  echo "[1/4] Repositorio Git en ./workspace ya inicializado."
fi

# 3. Load models from .env if present
if [ -f ".env" ]; then
  # export variables defined in .env
  set -a
  source .env
  set +a
fi

CEO_MODEL="${CEO_MODEL:-hermes3:8b}"
ANALYST_MODEL="${ANALYST_MODEL:-gemma4:e4b}"

# 4. Check container engine (Podman or Docker)
if command -v podman >/dev/null 2>&1; then
  echo "[2/4] Motor de contenedores detectado: $(podman --version)"
elif command -v docker >/dev/null 2>&1; then
  echo "[2/4] Motor de contenedores detectado: $(docker --version)"
else
  echo "[!] Advertencia: No se encontró ni Podman ni Docker en el PATH."
fi

# 5. Check Ollama and model tags
if command -v ollama >/dev/null 2>&1; then
  echo "[3/4] Verificando modelos en Ollama..."
  export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
  if ollama list >/dev/null 2>&1; then
    if ! ollama list | grep -q "$CEO_MODEL"; then
      echo "  -> Modelo de CEO ($CEO_MODEL) no encontrado. Para descargarlo ejecuta: ollama pull $CEO_MODEL"
    fi
    if ! ollama list | grep -q "$ANALYST_MODEL"; then
      echo "  -> Modelo de Analista ($ANALYST_MODEL) no encontrado. Para descargarlo ejecuta: ollama pull $ANALYST_MODEL"
    fi
  else
    echo "  -> Nota: El servidor Ollama no está corriendo actualmente (inícialo con: OLLAMA_HOST=0.0.0.0:11434 ollama serve)."
  fi
else
  echo "[3/4] Ollama no detectado en el PATH."
fi

echo "[4/4] Entorno listo. Para levantar los 5 contenedores ejecuta:"
echo "      docker compose up --build -d   (o: podman-compose up --build -d)"
