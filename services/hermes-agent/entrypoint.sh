#!/bin/sh
set -e

mkdir -p /workspace /root/.hermes/skills /tests

# Ensure git safe.directory and identity are configured for Developer Agent commits
git config --global --add safe.directory /workspace
git config --global user.name "Hermes Developer Agent"
git config --global user.email "dev-hermes@localhost.company"

if [ "$AGENT_ROLE" = "developer" ]; then
  if [ ! -d "/workspace/.git" ]; then
    git init /workspace
  fi
  # Start static HTTP server on port 8080 serving /workspace in background
  python3 -m http.server 8080 --directory /workspace &
fi

exec uvicorn agent:app --host 0.0.0.0 --port 8000
