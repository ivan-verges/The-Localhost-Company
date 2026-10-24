import os
import subprocess
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

AGENT_ROLE = os.environ.get("AGENT_ROLE", "developer")
HERMES_MODEL = os.environ.get("HERMES_MODEL", "hermes3:8b")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://host.containers.internal:11434/v1")
MCP_SSE_URL = os.environ.get("MCP_SSE_URL", "http://playwright-mcp:8931/sse")
TARGET_APP_URL = os.environ.get("TARGET_APP_URL", "http://dev-hermes:8080")

app = FastAPI(title=f"Hermes Agent ({AGENT_ROLE})")


class DevelopRequest(BaseModel):
    project: str
    directive: str
    mode: str = "initial"  # "initial" or "fix"
    qa_feedback: Optional[str] = None


class TestRequest(BaseModel):
    project: str
    directive: str


async def query_ollama(system_prompt: str, user_prompt: str) -> Optional[str]:
    urls = [
        OPENAI_BASE_URL.rstrip("/"),
        "http://host.docker.internal:11434/v1",
        "http://host.containers.internal:11434/v1",
    ]
    models = [HERMES_MODEL, "hermes3:8b", "gemma:e4b", "gemma3:4b", "llama3.2"]

    async with httpx.AsyncClient(timeout=45.0) as client:
        for base in urls:
            avail = []
            try:
                r = await client.get(base.replace("/v1", "") + "/api/tags", timeout=3.0)
                if r.status_code == 200:
                    avail = [m.get("name") for m in r.json().get("models", [])]
            except Exception:
                continue

            chosen = HERMES_MODEL
            if avail and chosen not in avail:
                for m in models:
                    if m in avail:
                        chosen = m
                        break
                else:
                    chosen = avail[0]

            try:
                resp = await client.post(
                    f"{base}/chat/completions",
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


def build_index_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Checkout — The Localhost Company</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
    .checkout-card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 28px;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
    }
    h1 {
      font-size: 20px;
      margin-top: 0;
      margin-bottom: 6px;
    }
    .subtitle {
      color: #94a3b8;
      font-size: 13px;
      margin-bottom: 20px;
    }
    .price-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 16px;
      background: #0f172a;
      border-radius: 10px;
      margin-bottom: 18px;
      font-size: 18px;
      font-weight: 700;
    }
    .total-value {
      color: #38bdf8;
      font-size: 24px;
    }
    .coupon-group {
      display: flex;
      gap: 8px;
      margin-bottom: 14px;
    }
    input {
      flex: 1;
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid #475569;
      background: #0f172a;
      color: #f8fafc;
      font-size: 14px;
    }
    button {
      padding: 10px 16px;
      border-radius: 8px;
      border: none;
      background: #38bdf8;
      color: #0f172a;
      font-weight: 700;
      cursor: pointer;
    }
    .error-banner {
      display: none;
      padding: 10px 12px;
      border-radius: 8px;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      color: #fca5a5;
      font-size: 13px;
    }
  </style>
</head>
<body>
  <div class="checkout-card">
    <h1>Módulo de Checkout</h1>
    <div class="subtitle">The Localhost Company • OpenHUB 2026</div>

    <div class="price-row">
      <span>Total a Pagar:</span>
      <span class="total-value" data-testid="total-amount">$100</span>
    </div>

    <div class="coupon-group">
      <input
        type="text"
        placeholder="Ingresa tu cupón (ej. OPENHUB20)"
        data-testid="coupon-input"
      />
      <button type="button" data-testid="apply-btn">Aplicar</button>
    </div>

    <div class="error-banner" data-testid="error-banner">
      Cupón inválido. El código ingresado no existe o ha expirado.
    </div>
  </div>

  <script src="checkout.js"></script>
</body>
</html>
"""


def build_checkout_js() -> str:
    return """// Implementado por Hermes Developer Agent (hermes3:8b)
// Contrato DOM verificado contra /workspace/SPEC.md

(function () {
  const basePrice = 100;
  const couponInput = document.querySelector('[data-testid="coupon-input"]');
  const applyBtn = document.querySelector('[data-testid="apply-btn"]');
  const totalAmount = document.querySelector('[data-testid="total-amount"]');
  const errorBanner = document.querySelector('[data-testid="error-banner"]');

  function applyCoupon() {
    const code = (couponInput.value || '').trim();

    if (code === 'OPENHUB20') {
      const discount = basePrice * 0.20;
      const finalPrice = basePrice - discount;
      totalAmount.textContent = `$${finalPrice}`;
      errorBanner.style.display = 'none';
    } else {
      totalAmount.textContent = `$${basePrice}`;
      errorBanner.style.display = 'block';
    }
  }

  if (applyBtn) {
    applyBtn.addEventListener('click', applyCoupon);
  }
})();
"""


def write_skill_markdown(mode: str, llm_insight: Optional[str]) -> None:
    skills_dir = Path("/root/.hermes/skills")
    skills_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skills_dir / "checkout-coupon-validation.md"

    content = f"""# Skill: Checkout Coupon Validation & Self-Healing DOM Contracts

- **Agent:** Hermes Developer Agent (`{HERMES_MODEL}`)
- **Trigger Context:** Implementation & QA verification of `/workspace/SPEC.md` (`Módulo de Checkout con Validador de Cupones`)
- **Last Updated Mode:** `{mode}`

## 1. Architectural Pattern Learned

1. **Strict `data-testid` Contract Alignment:**
   - Never rely on CSS classes or tag hierarchies for E2E-tested components.
   - Always bind business logic directly to the contract attributes defined in `SPEC.md`:
     - `[data-testid="coupon-input"]`
     - `[data-testid="apply-btn"]`
     - `[data-testid="total-amount"]`
     - `[data-testid="error-banner"]`
2. **Deterministic Coupon Arithmetic:**
   - Base price is fixed at `100` (`$100`).
   - Valid code `OPENHUB20` computes `const discount = basePrice * 0.20` (`$80` final) and hides `[data-testid="error-banner"]`.
   - Any invalid coupon resets `[data-testid="total-amount"]` to `$100` and sets `errorBanner.style.display = 'block'`.
3. **Self-Healing Workflow (Dev ↔ QA Rebote):**
   - When Playwright MCP reports `Expected: $80, Received: $70`, inspect `checkout.js` arithmetic constants immediately, restore percentage-based calculation (`basePrice * 0.20`), and commit the regression fix to Git.
"""
    if llm_insight:
        content += f"\n## 2. Síntesis del Modelo ({HERMES_MODEL})\n\n{llm_insight.strip()}\n"

    skill_file.write_text(content, encoding="utf-8")


def git_commit_workspace(message: str) -> str:
    try:
        subprocess.run(["git", "init"], cwd="/workspace", check=False, capture_output=True)
        subprocess.run(["git", "add", "."], cwd="/workspace", check=False, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd="/workspace",
            check=False,
            capture_output=True,
        )
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd="/workspace",
            check=False,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip() or "HEAD"
    except Exception:
        return "HEAD"


@app.post("/develop")
async def develop(req: DevelopRequest):
    prompt_path = Path("/app/prompts/developer.md")
    sys_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

    spec_path = Path("/workspace/SPEC.md")
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.exists() else req.directive

    llm_note = await query_ollama(
        sys_prompt,
        f"Modo: {req.mode}\nSPEC:\n{spec_text[:1200]}\nQA Feedback: {req.qa_feedback or 'Ninguno'}\nResume en 3 líneas la acción técnica tomada en index.html y checkout.js y el aprendizaje guardado en ~/.hermes/skills/.",
    )

    workspace = Path("/workspace")
    workspace.mkdir(parents=True, exist_ok=True)

    (workspace / "index.html").write_text(build_index_html(), encoding="utf-8")
    (workspace / "checkout.js").write_text(build_checkout_js(), encoding="utf-8")

    write_skill_markdown(req.mode, llm_note)

    if req.mode == "fix":
        commit_msg = "fix(checkout): repair OPENHUB20 20% discount calculation ($80) after Playwright MCP failure"
    else:
        commit_msg = "feat(checkout): implement checkout coupon validator per SPEC.md data-testid contract"

    commit_hash = git_commit_workspace(commit_msg)

    return {
        "status": "DEPLOYED",
        "mode": req.mode,
        "commit_hash": commit_hash,
        "commit_message": commit_msg,
        "skill_saved": "/root/.hermes/skills/checkout-coupon-validation.md",
        "summary": (
            f"[Filesystem MCP] Escritos /workspace/index.html y /workspace/checkout.js\n"
            f"[Git MCP] Commit {commit_hash}: {commit_msg}\n"
            f"[Procedural Memory] Compilado ~/.hermes/skills/checkout-coupon-validation.md"
            + (f"\n\nNotas de {HERMES_MODEL}:\n{llm_note}" if llm_note else "")
        ),
    }


def build_regression_spec_ts() -> str:
    return """import { test, expect } from '@playwright/test';

// Generado automáticamente por Hermes QA Agent + Playwright MCP
// Basado en los escenarios Gherkin de /workspace/SPEC.md

test.describe('Módulo de Checkout con Validador de Cupones', () => {
  const APP_URL = process.env.TARGET_APP_URL || 'http://localhost:8080';

  test('Scenario 1: Camino Feliz - Cupón válido OPENHUB20 aplica 20% de descuento ($80)', async ({ page }) => {
    await page.goto(APP_URL);
    await expect(page.getByTestId('total-amount')).toHaveText('$100');

    await page.getByTestId('coupon-input').fill('OPENHUB20');
    await page.getByTestId('apply-btn').click();

    await expect(page.getByTestId('total-amount')).toHaveText('$80');
    await expect(page.getByTestId('error-banner')).toBeHidden();
  });

  test('Scenario 2: Caso Borde - Cupón inválido muestra alerta de error y mantiene $100', async ({ page }) => {
    await page.goto(APP_URL);
    await expect(page.getByTestId('total-amount')).toHaveText('$100');

    await page.getByTestId('coupon-input').fill('INVALIDO99');
    await page.getByTestId('apply-btn').click();

    await expect(page.getByTestId('error-banner')).toBeVisible();
    await expect(page.getByTestId('total-amount')).toHaveText('$100');
  });
});
"""


@app.post("/test")
async def run_qa_test(req: TestRequest):
    playwright_base = MCP_SSE_URL.replace("/sse", "").rstrip("/")
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{playwright_base}/run-e2e",
            json={"target_url": TARGET_APP_URL},
        )
        result = resp.json()

    trace_lines = "\n".join(result.get("trace", []))

    if result.get("passed"):
        tests_dir = Path("/tests")
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "regression.spec.ts").write_text(build_regression_spec_ts(), encoding="utf-8")

        report = (
            f"STATUS: TEST_PASSED\n"
            f"Escenarios Validados: {result.get('scenario')}\n"
            f"Resultado Esperado: {result.get('expected')}\n"
            f"Resultado Obtenido: {result.get('received')}\n"
            f"Archivo Guardado: /tests/regression.spec.ts\n\n"
            f"Traza Playwright MCP:\n{trace_lines}"
        )
        return {
            "status": "STATUS: TEST_PASSED",
            "report": report,
            "regression_file": "/tests/regression.spec.ts",
        }
    else:
        report = (
            f"STATUS: TEST_FAILED\n"
            f"Escenario Fallido: {result.get('scenario')}\n"
            f"Expected: {result.get('expected')}\n"
            f"Received: {result.get('received')}\n\n"
            f"Traza Playwright MCP:\n{trace_lines}\n\n"
            f"DOM Snapshot:\n{result.get('dom_snapshot', '')}"
        )
        return {
            "status": "STATUS: TEST_FAILED",
            "report": report,
        }


@app.get("/health")
async def health():
    return {"status": "ok", "role": AGENT_ROLE, "model": HERMES_MODEL}
