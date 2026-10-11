import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent import build_research_agent
from callbacks.research_stream import ResearchStreamHandler
from tools.extraction import clear_evidence_ledger, evidence_snapshot

load_dotenv()

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    model: Optional[str] = Field(default=None, min_length=1)
    max_iterations: int = Field(default=8, ge=4, le=16)


class ResearchJob(BaseModel):
    id: str
    question: str
    status: Literal["queued", "running", "completed", "failed"]
    created_at: str
    updated_at: str
    events: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    report: Optional[str] = None
    error: Optional[str] = None


app = FastAPI(title="Research Agent API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: Dict[str, ResearchJob] = {}
_jobs_lock = threading.Lock()
_research_lock = threading.Lock()
_dashboard = Path(__file__).parent / "dashboard" / "index.html"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _add_event(job_id: str, event_type: str, payload: Any) -> None:
    with _jobs_lock:
        job = _jobs[job_id]
        job.events.append({"type": event_type, "timestamp": _now(), "data": payload})
        job.updated_at = _now()
        job.evidence = evidence_snapshot()


def _run_job(job_id: str, request: ResearchRequest) -> None:
    with _jobs_lock:
        _jobs[job_id].status = "running"
        _jobs[job_id].updated_at = _now()

    try:
        # The current evidence tools use a process-level ledger, so serialize jobs.
        with _research_lock:
            clear_evidence_ledger()
            executor = build_research_agent(
                model_name=request.model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
                max_iterations=request.max_iterations,
                max_execution_time=180,
            )
            result = executor.invoke(
                {"input": request.question, "chat_history": []},
                config={
                    "callbacks": [
                        ResearchStreamHandler(
                            event_sink=lambda kind, data: _add_event(job_id, kind, data)
                        )
                    ]
                },
            )
            output = result.get("output", "")
            if not output or output == "Agent stopped due to max iterations.":
                output = (
                    "The research run reached its tool-call budget before the "
                    "report could be finalized. Increase Research depth and retry."
                )
        with _jobs_lock:
            job = _jobs[job_id]
            job.status = "completed"
            job.report = output
            job.evidence = evidence_snapshot()
            job.updated_at = _now()
    except Exception as exc:
        with _jobs_lock:
            job = _jobs[job_id]
            job.status = "failed"
            job.error = str(exc)
            job.report = f"Research failed: {exc}"
            job.evidence = evidence_snapshot()
            job.updated_at = _now()
        _add_event(job_id, "job_failed", {"error": str(exc)})


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(_dashboard)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "groq_configured": str(bool(os.getenv("GROQ_API_KEY"))).lower()}


@app.post("/api/research", response_model=ResearchJob, status_code=202)
def start_research(request: ResearchRequest) -> ResearchJob:
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured.")
    job_id = uuid.uuid4().hex
    timestamp = _now()
    job = ResearchJob(
        id=job_id,
        question=request.question,
        status="queued",
        created_at=timestamp,
        updated_at=timestamp,
    )
    with _jobs_lock:
        _jobs[job_id] = job
    threading.Thread(target=_run_job, args=(job_id, request), daemon=True).start()
    return job


@app.get("/api/research/{job_id}", response_model=ResearchJob)
def get_research(job_id: str) -> ResearchJob:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Research job not found.")
        return job


@app.get("/api/research/{job_id}/events")
def get_events(job_id: str) -> Dict[str, Any]:
    job = get_research(job_id)
    return {"job_id": job_id, "status": job.status, "events": job.events}
