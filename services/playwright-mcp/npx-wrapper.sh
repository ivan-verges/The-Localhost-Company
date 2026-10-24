#!/bin/sh
# Intercepts `npx @playwright/mcp@latest --headless --port 8931` from podman-compose.yml
exec node /app/server.js "$@"
