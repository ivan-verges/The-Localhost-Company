#!/usr/bin/env bash
set -euo pipefail

echo "Enviando Directiva desde la Junta Directiva al CEO Agent (http://localhost:3000/api/board/directive)..."

curl -s -X POST http://localhost:3000/api/board/directive \
  -H "Content-Type: application/json" \
  -d '{
    "project": "Módulo de Checkout con Validador de Cupones",
    "directive": "Crear una aplicación web de checkout con un precio base de $100. Si el usuario ingresa el cupón OPENHUB20 se aplica un 20% de descuento ($80 final). Si ingresa un cupón inválido debe mostrarse una alerta de error y mantener el total en $100."
  }'

echo ""
echo "✅ Directiva enviada. Abre http://localhost:3000 para ver el progreso en vivo."
