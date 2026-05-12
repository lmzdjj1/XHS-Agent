from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from xhs_agent import run_xhs_workflow


app = FastAPI(title="XHS Content Agent", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


class WorkflowRequest(BaseModel):
    instruction: str | None = Field(default=None, description="Plain text instruction.")
    openclaw: dict[str, Any] | None = Field(default=None, description="OpenClaw command payload.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/invoke")
def invoke_workflow(request: WorkflowRequest) -> dict[str, Any]:
    payload: str | dict[str, Any]
    if request.openclaw is not None:
        payload = request.openclaw
    elif request.instruction:
        payload = request.instruction
    else:
        raise HTTPException(status_code=400, detail="Either instruction or openclaw is required.")

    try:
        result = run_xhs_workflow(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "source": result.get("source"),
        "framework": result.get("framework"),
        "titles": result.get("titles"),
        "selected_title": result.get("selected_title"),
        "keywords": result.get("keywords"),
        "final_copy": result.get("final_copy"),
        "cover_prompt": result.get("cover_prompt"),
    }


app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
