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

# 3. Check container engine (Podman or Docker)
if command -v podman >/dev/null 2>&1; then
  echo "[2/4] Motor de contenedores detectado: $(podman --version)"
elif command -v docker >/dev/null 2>&1; then
  echo "[2/4] Motor de contenedores detectado: $(docker --version)"
else
  echo "[!] Advertencia: No se encontró ni Podman ni Docker en el PATH."
fi

# 4. Check Ollama and model tags
if command -v ollama >/dev/null 2>&1; then
  echo "[3/4] Verificando modelos en Ollama..."
  export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
  if ollama list >/dev/null 2>&1; then
    if ! ollama list | grep -q "hermes3:8b"; then
      echo "  -> Para descargar hermes3:8b ejecuta: ollama pull hermes3:8b"
    fi
    if ! ollama list | grep -q "gemma:e4b"; then
      if ollama list | grep -q "gemma3:4b"; then
        echo "  -> Creando alias gemma:e4b desde gemma3:4b..."
        ollama cp gemma3:4b gemma:e4b || true
      elif ollama list | grep -q "gemma4:e4b"; then
        echo "  -> Creando alias gemma:e4b desde gemma4:e4b..."
        ollama cp gemma4:e4b gemma:e4b || true
      else
        echo "  -> Nota: Puedes descargar Gemma y etiquetarlo como gemma:e4b con: ollama pull gemma3:4b && ollama cp gemma3:4b gemma:e4b"
      fi
    fi
  else
    echo "  -> Nota: El servidor Ollama no está corriendo actualmente (inícialo con: OLLAMA_HOST=0.0.0.0:11434 ollama serve)."
  fi
else
  echo "[3/4] Ollama no detectado en el PATH."
fi

echo "[4/4] Entorno listo. Para levantar los 5 contenedores ejecuta:"
echo "      docker compose up --build -d   (o: podman-compose up --build -d)"
