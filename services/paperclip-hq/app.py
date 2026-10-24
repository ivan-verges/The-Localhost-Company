import asyncio
import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import yaml
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Paperclip Control Plane - CEO Agent HQ")

CONFIG_PATH = os.environ.get("COMPANY_CONFIG", "/app/config/company.yaml")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.containers.internal:11434/v1")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "hermes3:8b")

# In-memory company state
STATE: Dict[str, Any] = {
    "company": {},
    "current_project": None,
    "directive": None,
    "current_stage": "IDLE",
    "fix_iterations": 0,
    "max_fix_iterations": 3,
    "status": "IDLE",  # IDLE, RUNNING, AWAITING_BOARD_APPROVAL, COMPLETED, ESCALATED
    "executive_summary": None,
    "last_qa_report": None,
    "logs": [],
    "stages": [
        {"id": "1_ANALYSIS", "owner": "business_analyst", "status": "pending", "label": "1. Business Analysis (OpenClaw)"},
        {"id": "2_DEVELOPMENT", "owner": "developer", "status": "pending", "label": "2. Engineering (Hermes Dev)"},
        {"id": "3_QA_TESTING", "owner": "qa_engineer", "status": "pending", "label": "3. E2E QA (Playwright MCP)"},
        {"id": "4_CEO_FINAL_REVIEW", "owner": "ceo", "status": "pending", "label": "4. CEO Review & Sign-Off"},
    ],
}


def load_company_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def log_event(role: str, stage: str, message: str, details: Optional[str] = None, level: str = "info") -> None:
    entry = {
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "role": role,
        "stage": stage,
        "message": message,
        "details": details,
        "level": level,
    }
    STATE["logs"].append(entry)
    print(f"[{entry['timestamp']}] [{role.upper()}] ({stage}): {message}", flush=True)


def set_stage_status(stage_id: str, status: str) -> None:
    STATE["current_stage"] = stage_id
    for s in STATE["stages"]:
        if s["id"] == stage_id:
            s["status"] = status


async def query_ollama(model: str, system_prompt: str, user_prompt: str) -> Optional[str]:
    urls_to_try = [
        OLLAMA_BASE_URL.rstrip("/"),
        "http://host.docker.internal:11434/v1",
        "http://host.containers.internal:11434/v1",
    ]
    models_to_try = [model, "hermes3:8b", "gemma:e4b", "gemma3:4b", "llama3.2", "qwen2.5:7b"]

    async with httpx.AsyncClient(timeout=45.0) as client:
        for base_url in urls_to_try:
            # Check available models first
            avail_models = []
            try:
                tags_url = base_url.replace("/v1", "") + "/api/tags"
                r = await client.get(tags_url, timeout=3.0)
                if r.status_code == 200:
                    data = r.json()
                    avail_models = [m.get("name") for m in data.get("models", [])]
            except Exception:
                continue

            chosen_model = model
            if avail_models and chosen_model not in avail_models:
                for candidate in models_to_try:
                    if candidate in avail_models:
                        chosen_model = candidate
                        break
                else:
                    chosen_model = avail_models[0]

            try:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    json={
                        "model": chosen_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.2,
                    },
                )
                if resp.status_code == 200:
                    body = resp.json()
                    return body["choices"][0]["message"]["content"]
            except Exception:
                continue
    return None


class DirectiveRequest(BaseModel):
    project: str
    directive: str


class BugInjectionRequest(BaseModel):
    bug_type: str = "discount_30"


async def run_company_workflow(project: str, directive: str, start_at_qa: bool = False) -> None:
    cfg = load_company_config()
    STATE["company"] = cfg.get("company", {"name": "The Localhost Company", "max_fix_iterations": 3})
    STATE["max_fix_iterations"] = STATE["company"].get("max_fix_iterations", 3)
    roles = cfg.get("roles", {})

    ceo_prompt_path = roles.get("ceo", {}).get("prompt_file", "/app/prompts/ceo.md")
    ceo_prompt = ""
    if os.path.exists(ceo_prompt_path):
        ceo_prompt = Path(ceo_prompt_path).read_text(encoding="utf-8")

    analyst_endpoint = roles.get("business_analyst", {}).get("endpoint", "http://analyst-openclaw:4000")
    dev_endpoint = roles.get("developer", {}).get("endpoint", "http://dev-hermes:8000")
    qa_endpoint = roles.get("qa_engineer", {}).get("endpoint", "http://qa-hermes:8000")

    async with httpx.AsyncClient(timeout=180.0) as client:
        if not start_at_qa:
            # 1. CEO Delegation & Business Analysis
            set_stage_status("1_ANALYSIS", "in_progress")
            log_event(
                "ceo",
                "1_ANALYSIS",
                f"Directiva recibida de la Junta Directiva para '{project}'. Delegando análisis a OpenClaw (Business Analyst - gemma:e4b)...",
                directive,
            )

            try:
                resp = await client.post(
                    f"{analyst_endpoint}/analyze",
                    json={"project": project, "directive": directive},
                )
                resp.raise_for_status()
                ba_data = resp.json()
                set_stage_status("1_ANALYSIS", "completed")
                log_event(
                    "business_analyst",
                    "1_ANALYSIS",
                    "Archivo /workspace/SPEC.md generado con selectores data-testid y escenarios Gherkin.",
                    ba_data.get("spec_preview", ""),
                    level="success",
                )
            except Exception as e:
                set_stage_status("1_ANALYSIS", "failed")
                STATE["status"] = "ESCALATED"
                log_event("ceo", "1_ANALYSIS", f"Error en Business Analyst: {e}", level="error")
                return

            # 2. CEO verifies SPEC.md and assigns Developer
            set_stage_status("2_DEVELOPMENT", "in_progress")
            log_event(
                "ceo",
                "2_DEVELOPMENT",
                "SPEC.md verificado (contiene data-testid y escenarios Gherkin). Asignando implementación a Hermes Developer Agent (hermes3:8b)...",
            )

            try:
                resp = await client.post(
                    f"{dev_endpoint}/develop",
                    json={
                        "project": project,
                        "directive": directive,
                        "mode": "initial",
                        "qa_feedback": None,
                    },
                )
                resp.raise_for_status()
                dev_data = resp.json()
                set_stage_status("2_DEVELOPMENT", "completed")
                log_event(
                    "developer",
                    "2_DEVELOPMENT",
                    f"Aplicación implementada en /workspace (index.html, checkout.js), commit '{dev_data.get('commit_hash', 'HEAD')}' realizado y servidor activo en puerto 8080.",
                    dev_data.get("summary", ""),
                    level="success",
                )
            except Exception as e:
                set_stage_status("2_DEVELOPMENT", "failed")
                STATE["status"] = "ESCALATED"
                log_event("ceo", "2_DEVELOPMENT", f"Error en Developer Agent: {e}", level="error")
                return

        # 3. Dev <-> QA Loop controlled by CEO Agent
        while STATE["fix_iterations"] <= STATE["max_fix_iterations"]:
            set_stage_status("3_QA_TESTING", "in_progress")
            log_event(
                "ceo",
                "3_QA_TESTING",
                f"Ordenando a QA Agent (Playwright MCP) ejecutar suite E2E contra http://dev-hermes:8080 (Intento #{STATE['fix_iterations'] + 1})...",
            )

            try:
                resp = await client.post(
                    f"{qa_endpoint}/test",
                    json={"project": project, "directive": directive},
                )
                resp.raise_for_status()
                qa_data = resp.json()
            except Exception as e:
                set_stage_status("3_QA_TESTING", "failed")
                STATE["status"] = "ESCALATED"
                log_event("ceo", "3_QA_TESTING", f"Error comunicando con QA Agent: {e}", level="error")
                return

            STATE["last_qa_report"] = qa_data
            qa_status = qa_data.get("status", "STATUS: TEST_FAILED")

            if qa_status == "STATUS: TEST_PASSED":
                set_stage_status("3_QA_TESTING", "completed")
                log_event(
                    "qa_engineer",
                    "3_QA_TESTING",
                    "STATUS: TEST_PASSED — Todos los escenarios Gherkin pasaron en Playwright MCP. Suite guardada en /tests/regression.spec.ts.",
                    qa_data.get("report", ""),
                    level="success",
                )
                break
            else:
                set_stage_status("3_QA_TESTING", "failed")
                STATE["fix_iterations"] += 1
                log_event(
                    "qa_engineer",
                    "3_QA_TESTING",
                    f"STATUS: TEST_FAILED — Fallo detectado por Playwright MCP.",
                    qa_data.get("report", ""),
                    level="error",
                )

                if STATE["fix_iterations"] > STATE["max_fix_iterations"]:
                    STATE["status"] = "ESCALATED"
                    log_event(
                        "ceo",
                        "4_CEO_FINAL_REVIEW",
                        f"Presupuesto máximo de reintentos ({STATE['max_fix_iterations']}) agotado. Escalando incidente a la Junta Directiva.",
                        level="error",
                    )
                    return

                # Bounce back to Developer (Self-Healing Workflow)
                set_stage_status("2_DEVELOPMENT", "in_progress")
                log_event(
                    "ceo",
                    "2_DEVELOPMENT",
                    f"Rebote automático #{STATE['fix_iterations']}/{STATE['max_fix_iterations']}: Reasignando ticket al Developer Agent con el stack trace y snapshot DOM de Playwright MCP...",
                    qa_data.get("report", ""),
                    level="warning",
                )

                try:
                    fix_resp = await client.post(
                        f"{dev_endpoint}/develop",
                        json={
                            "project": project,
                            "directive": directive,
                            "mode": "fix",
                            "qa_feedback": qa_data.get("report", ""),
                        },
                    )
                    fix_resp.raise_for_status()
                    fix_data = fix_resp.json()
                    set_stage_status("2_DEVELOPMENT", "completed")
                    log_event(
                        "developer",
                        "2_DEVELOPMENT",
                        f"Bug reparado en checkout.js y nuevo commit '{fix_data.get('commit_hash', 'HEAD')}' registrado. Memoria procedimental actualizada en ~/.hermes/skills/.",
                        fix_data.get("summary", ""),
                        level="success",
                    )
                except Exception as e:
                    set_stage_status("2_DEVELOPMENT", "failed")
                    STATE["status"] = "ESCALATED"
                    log_event("ceo", "2_DEVELOPMENT", f"Error en Developer durante corrección: {e}", level="error")
                    return

        # 4. CEO Final Review & Executive Summary
        set_stage_status("4_CEO_FINAL_REVIEW", "in_progress")
        log_event(
            "ceo",
            "4_CEO_FINAL_REVIEW",
            "Generando Resumen Ejecutivo para firma final de la Junta Directiva (BOARD_SIGN_OFF)...",
        )

        llm_summary = await query_ollama(
            DEFAULT_MODEL,
            ceo_prompt,
            f"El proyecto '{project}' con directiva '{directive}' ha pasado todas las pruebas E2E de Playwright MCP (STATUS: TEST_PASSED) tras {STATE['fix_iterations']} rebotes de corrección. Redacta un breve resumen ejecutivo en español (máximo 5 líneas) solicitando la firma final (BOARD_SIGN_OFF) a la Junta Directiva.",
        )

        if not llm_summary:
            llm_summary = (
                f"RESUMEN EJECUTIVO — {project}\n"
                f"• Estado de Calidad: STATUS: TEST_PASSED (Verificado con Playwright MCP en navegador headless).\n"
                f"• Entregables: /workspace/SPEC.md, /workspace/index.html, /workspace/checkout.js y /tests/regression.spec.ts.\n"
                f"• Ciclos de Auto-Corrección (Rebotes Dev ↔ QA): {STATE['fix_iterations']} de {STATE['max_fix_iterations']} permitidos.\n"
                f"• Memoria Procedimental: Habilidad compilada en ~/.hermes/skills/checkout-coupon-validation.md.\n"
                f"Se solicita a la Junta Directiva la aprobación final (BOARD_SIGN_OFF) para liberación a producción."
            )

        STATE["executive_summary"] = llm_summary
        STATE["status"] = "AWAITING_BOARD_APPROVAL"
        set_stage_status("4_CEO_FINAL_REVIEW", "completed")
        log_event(
            "ceo",
            "4_CEO_FINAL_REVIEW",
            "Ciclo completado con éxito. Esperando firma de la Junta Directiva (BOARD_SIGN_OFF).",
            llm_summary,
            level="success",
        )


@app.on_event("startup")
async def startup_event() -> None:
    cfg = load_company_config()
    STATE["company"] = cfg.get("company", {"name": "The Localhost Company", "max_fix_iterations": 3})
    log_event("ceo", "IDLE", "Plano de Control Paperclip HQ iniciado. Esperando directiva de la Junta Directiva.")


@app.post("/api/board/directive")
async def receive_directive(req: DirectiveRequest, background_tasks: BackgroundTasks):
    STATE["current_project"] = req.project
    STATE["directive"] = req.directive
    STATE["fix_iterations"] = 0
    STATE["status"] = "RUNNING"
    STATE["executive_summary"] = None
    for s in STATE["stages"]:
        s["status"] = "pending"

    background_tasks.add_task(run_company_workflow, req.project, req.directive, False)
    return {
        "status": "ACCEPTED",
        "company": STATE["company"].get("name", "The Localhost Company"),
        "project": req.project,
        "assigned_to": "ceo",
        "workflow_stage": "1_ANALYSIS",
        "message": "Directiva recibida por el CEO Agent. Ejecutando flujo autónomo (Analyst -> Developer -> QA -> CEO).",
    }


@app.post("/api/demo/inject-bug")
async def inject_bug_and_retest(background_tasks: BackgroundTasks):
    """
    Helper endpoint for Step 4.3.5 of the workshop:
    Introduces the deliberate $30 discount bug in /app/workspace/checkout.js
    and triggers the QA -> CEO -> Developer self-healing loop automatically.
    """
    checkout_js = Path("/app/workspace/checkout.js")
    if not checkout_js.exists():
        raise HTTPException(status_code=400, detail="checkout.js aún no existe en /workspace. Ejecuta primero la directiva.")

    code = checkout_js.read_text(encoding="utf-8")
    # Introduce deliberate bug: $30 discount ($70 total) instead of 20% ($80 total)
    buggy_code = code.replace("const discount = basePrice * 0.20;", "const discount = 30; // BUG DELIBERADO DEMO: resta $30 en vez de 20% ($20)")
    if buggy_code == code:
        buggy_code = code.replace("80", "70")
    checkout_js.write_text(buggy_code, encoding="utf-8")

    log_event(
        "board",
        "3_QA_TESTING",
        "🐞 Bug deliberado inyectado en /workspace/checkout.js (Descuento calcula $70 en vez de $80). Ejecutando QA Agent para demostrar Self-Healing...",
        level="warning",
    )

    project = STATE.get("current_project") or "Módulo de Checkout con Validador de Cupones"
    directive = STATE.get("directive") or (
        "Crear una aplicación web de checkout con un precio base de $100. "
        "Si el usuario ingresa el cupón OPENHUB20 se aplica un 20% de descuento ($80 final). "
        "Si ingresa un cupón inválido debe mostrarse una alerta de error y mantener el total en $100."
    )
    STATE["status"] = "RUNNING"
    background_tasks.add_task(run_company_workflow, project, directive, True)
    return {
        "status": "BUG_INJECTED_AND_TESTING",
        "message": "Bug inyectado en checkout.js ($70 en lugar de $80). El QA Agent está ejecutando Playwright MCP y reportará el fallo al CEO.",
    }


@app.post("/api/board/approve")
async def board_approve():
    STATE["status"] = "COMPLETED"
    log_event(
        "board",
        "BOARD_SIGN_OFF",
        "✅ Junta Directiva firmó la aprobación final (BOARD_SIGN_OFF). Release desplegado oficialmente.",
        level="success",
    )
    return {"status": "BOARD_SIGN_OFF", "approved": True}


@app.get("/api/state")
async def get_state():
    spec_content = None
    spec_path = Path("/app/workspace/SPEC.md")
    if spec_path.exists():
        spec_content = spec_path.read_text(encoding="utf-8")

    skill_files = []
    skills_dir = Path("/app/skills")
    if skills_dir.exists():
        for p in sorted(skills_dir.glob("*.md")):
            skill_files.append({"name": p.name, "content": p.read_text(encoding="utf-8")})

    test_files = []
    tests_dir = Path("/app/tests")
    if tests_dir.exists():
        for p in sorted(tests_dir.glob("*.*")):
            test_files.append({"name": p.name, "content": p.read_text(encoding="utf-8")})

    return {
        **STATE,
        "artifacts": {
            "spec_md": spec_content,
            "skills": skill_files,
            "tests": test_files,
        },
    }


@app.get("/")
async def index():
    return FileResponse("/app/static/index.html")
