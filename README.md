# The Localhost Company — OpenHUB 2026 Bootcamp

Repositorio oficial de implementación para el taller práctico **"The Localhost Company: Creating a Startup with your Favorite Local AI Models"** (OpenHUB 2026 - UNAPEC).

## Arquitectura de 5 Servicios

| Rol Corporativo | Contenedor | Puerto | Modelo en Ollama | Responsabilidad |
| :--- | :--- | :--- | :--- | :--- |
| **CEO Agent** | `paperclip-hq` (`localhost-ceo-hq`) | `:3000` | `hermes3:8b` | Plano de control, tablero Kanban en vivo, asignación de tickets y límite de 3 reintentos. |
| **Business Analyst** | `analyst-openclaw` (`localhost-analyst`) | `:4000` | `gemma:e4b` | Genera `/workspace/SPEC.md` con contratos `data-testid` y escenarios Gherkin. |
| **Developer Agent** | `dev-hermes` (`localhost-developer`) | `:8080` (App) / `:8000` (API) | `hermes3:8b` | Implementa `/workspace/index.html` y `checkout.js`, hace commits en Git y guarda skills en `./skills/`. |
| **Playwright MCP** | `playwright-mcp` (`localhost-playwright-mcp`) | `:8931` | — | Navegador Chromium Headless expuesto vía MCP para pruebas E2E reales. |
| **QA Agent** | `qa-hermes` (`localhost-qa`) | `:8000` (API) | `hermes3:8b` | Ejecuta las pruebas E2E contra `http://dev-hermes:8080` y emite `STATUS: TEST_PASSED` o `STATUS: TEST_FAILED`. |

---

## Inicio Rápido (Docker Compose o Podman Compose)

### 1. Preparar el entorno (Fase 0)
```bash
./scripts/setup.sh
```

### 2. Construir e iniciar los 5 contenedores (Fases 1 a 4)
Con **Docker Compose**:
```bash
docker compose up --build -d
docker ps
```

Con **Podman Compose**:
```bash
podman-compose up --build -d
podman ps
```

### 3. Enviar la directiva de negocio al CEO Agent (Paso 4.2)
Puedes abrir el dashboard interactivo en **http://localhost:3000** o ejecutar el comando `curl` de la guía:

```bash
curl -X POST http://localhost:3000/api/board/directive \
  -H "Content-Type: application/json" \
  -d '{
    "project": "Módulo de Checkout con Validador de Cupones",
    "directive": "Crear una aplicación web de checkout con un precio base de $100. Si el usuario ingresa el cupón OPENHUB20 se aplica un 20% de descuento ($80 final). Si ingresa un cupón inválido debe mostrarse una alerta de error y mantener el total en $100."
  }'
```
*(O simplemente ejecuta `./scripts/send-directive.sh`)*.

### 4. Demostrar el Rebote Autónomo / Self-Healing (Paso 4.3.5)
Para inyectar el bug deliberado en `workspace/checkout.js` (donde el descuento resta `$30` dando `$70` en lugar de `$80`) y ver cómo **Playwright MCP** devuelve `STATUS: TEST_FAILED` y el **CEO Agent** ordena al **Developer Agent** repararlo automáticamente:

```bash
./scripts/inject-bug.sh
```
*(También disponible como botón directo en el dashboard `http://localhost:3000`)*.

### 5. Inspeccionar la Memoria Procedimental y el Historial Git (Fase 5)
```bash
# Ver las habilidades compiladas automáticamente por Hermes Agent
ls -la ./skills/
cat ./skills/checkout-coupon-validation.md

# Ver la suite de regresión Playwright generada por el QA Agent
cat ./tests/regression.spec.ts

# Ver el historial de commits realizados por el Developer Agent
cd ./workspace && git log --oneline
```
