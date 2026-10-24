#!/usr/bin/env bash
set -euo pipefail

echo "🐞 Inyectando bug deliberado en /workspace/checkout.js ($30 de descuento en vez de 20% = $70) y disparando validación QA (Playwright MCP)..."

curl -s -X POST http://localhost:3000/api/demo/inject-bug \
  -H "Content-Type: application/json"

echo ""
echo "✅ Rebote autónomo en curso. Observa en http://localhost:3000 cómo QA detecta Expected: \$80, Received: \$70 y el Developer Agent lo repara."
