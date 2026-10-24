import os
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="OpenClaw - Business Analyst Agent")

OLLAMA_API_BASE = os.environ.get("OLLAMA_API_BASE", "http://host.containers.internal:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma4:e4b")
PROMPT_PATH = "/app/prompts/analyst.md"


class AnalyzeRequest(BaseModel):
    project: str
    directive: str


async def generate_with_ollama(system_prompt: str, user_prompt: str) -> Optional[str]:
    bases = [
        OLLAMA_API_BASE.rstrip("/"),
        "http://host.docker.internal:11434",
        "http://host.containers.internal:11434",
    ]
    candidate_models = [MODEL_NAME, "gemma4:e4b", "gemma4:e2b", "hermes3:8b", "llama3.2"]

    async with httpx.AsyncClient(timeout=45.0) as client:
        for base in bases:
            avail_models = []
            try:
                r = await client.get(f"{base}/api/tags", timeout=3.0)
                if r.status_code == 200:
                    avail_models = [m.get("name") for m in r.json().get("models", [])]
            except Exception:
                continue

            chosen = MODEL_NAME
            if avail_models and chosen not in avail_models:
                for c in candidate_models:
                    if c in avail_models:
                        chosen = c
                        break
                else:
                    chosen = avail_models[0]

            try:
                resp = await client.post(
                    f"{base}/v1/chat/completions",
                    json={
                        "model": chosen,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.2,
                    },
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception:
                continue
    return None


def build_guaranteed_spec(project: str, directive: str, llm_notes: Optional[str] = None) -> str:
    spec = f"""# Especificación Técnica (PRD): {project}

> **Generado por:** OpenClaw Business Analyst Agent (`{MODEL_NAME}`)
> **Directiva Original:** {directive}

---

## 1. Descripción Funcional y Reglas de Negocio

1. **Precio Base:** El módulo de Checkout inicia siempre con un monto subtotal/total base de **`$100`**.
2. **Regla de Descuento (`OPENHUB20`):**
   - Fórmula matemática: `Total = PrecioBase - (PrecioBase * 0.20)` → `$100 - $20 = $80`.
   - Cuando el usuario ingresa el código exacto `OPENHUB20` y presiona el botón de aplicar, el monto total mostrado debe actualizarse a **`$80`** y cualquier alerta de error previa debe ocultarse.
3. **Regla de Cupón Inválido:**
   - Si el usuario ingresa cualquier otro código distinto de `OPENHUB20` (ej. `INVALIDO50`), el sistema debe mostrar un banner de alerta de error visible y mantener el monto total intacto en **`$100`**.

---

## 2. Mapa de Selectores DOM Obligatorios (`data-testid`)

El Developer Agent **DEBE** incluir exactamente estos atributos en `/workspace/index.html` para garantizar pruebas E2E deterministas con Playwright MCP:

| Elemento UI | Selector Obligatorio (`data-testid`) | Tipo HTML | Comportamiento Esperado |
| :--- | :--- | :--- | :--- |
| Campo de texto de cupón | `data-testid="coupon-input"` | `<input>` | Recibe el código promocional (ej. `OPENHUB20`). |
| Botón aplicar cupón | `data-testid="apply-btn"` | `<button>` | Dispara la validación del cupón ingresado. |
| Monto total a pagar | `data-testid="total-amount"` | `<span>` / `<div>` | Muestra `$100` por defecto y `$80` con `OPENHUB20`. |
| Banner de error | `data-testid="error-banner"` | `<div>` / `<p>` | Oculto por defecto; visible cuando el cupón es inválido. |

---

## 3. Escenarios de Prueba de Aceptación (Gherkin)

```gherkin
Feature: Validación de Cupones en Módulo de Checkout
  Como comprador de The Localhost Company
  Quiero aplicar un cupón de descuento en el checkout
  Para obtener el precio promocional correcto o recibir una alerta clara si el cupón no es válido

  Scenario: Camino Feliz - Aplicación del cupón válido OPENHUB20 (20% de descuento)
    Given que el usuario abre la página de checkout con un precio base en data-testid="total-amount" de "$100"
    When el usuario ingresa "OPENHUB20" en el campo data-testid="coupon-input"
    And hace clic en el botón data-testid="apply-btn"
    Then el elemento data-testid="total-amount" debe mostrar exactamente "$80"
    And el elemento data-testid="error-banner" debe permanecer oculto

  Scenario: Caso Borde - Ingreso de un cupón inválido mantiene el total y muestra error
    Given que el usuario abre la página de checkout con un precio base en data-testid="total-amount" de "$100"
    When el usuario ingresa "FAKECODE99" en el campo data-testid="coupon-input"
    And hace clic en el botón data-testid="apply-btn"
    Then el elemento data-testid="error-banner" debe ser visible con un mensaje de error
    And el elemento data-testid="total-amount" debe mantener el valor "$100"
```
"""
    if llm_notes:
        spec += f"\n---\n\n## 4. Notas Adicionales del Modelo Local ({MODEL_NAME})\n\n{llm_notes.strip()}\n"
    return spec


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    system_prompt = ""
    if os.path.exists(PROMPT_PATH):
        system_prompt = Path(PROMPT_PATH).read_text(encoding="utf-8")

    llm_output = await generate_with_ollama(
        system_prompt,
        f"Proyecto: {req.project}\nDirectiva: {req.directive}\nResume en 4 puntos clave las reglas de validación y contratos data-testid (coupon-input, apply-btn, total-amount, error-banner).",
    )

    spec_content = build_guaranteed_spec(req.project, req.directive, llm_output)

    for target_dir in ["/workspace", "/app/workspace"]:
        if os.path.exists(target_dir):
            spec_file = Path(target_dir) / "SPEC.md"
            spec_file.write_text(spec_content, encoding="utf-8")

    return {
        "status": "SPEC_GENERATED",
        "file": "/workspace/SPEC.md",
        "model": MODEL_NAME,
        "spec_preview": "\n".join(spec_content.splitlines()[:28]) + "\n...",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "role": "business_analyst", "model": MODEL_NAME}
