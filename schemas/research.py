from datetime import datetime
from typing import Dict, List, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


ResearchStatus = Literal[
    "queued",
    "planning",
    "searching",
    "fetching",
    "verifying",
    "synthesizing",
    "completed",
    "failed",
    "cancelled",
]


class SourceRecord(BaseModel):
    id: str
    title: str
    url: str
    snippet: str = ""
    content: str = ""
    published: Optional[str] = None
    source_type: Literal["web", "pdf", "api"] = "web"
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    fetched: bool = False
    error: Optional[str] = None


class CitationRecord(BaseModel):
    id: str
    source_id: str
    claim: str
    quote: str
    confidence: Literal["high", "medium", "low"] = "medium"
    verified: bool = False


class ResearchState(TypedDict, total=False):
    job_id: str
    question: str
    model: str
    status: ResearchStatus
    sub_questions: List[str]
    search_queries: List[str]
    sources: List[SourceRecord]
    citations: List[CitationRecord]
    missing_evidence: List[str]
    contradictions: List[str]
    answer: str
    error: Optional[str]
    iteration: int
    max_iterations: int
    started_at: datetime
    updated_at: datetime
    cancelled: bool


def new_research_state(
    job_id: str,
    question: str,
    model: str,
    max_iterations: int,
) -> ResearchState:
    now = datetime.now()
    return {
        "job_id": job_id,
        "question": question,
        "model": model,
        "status": "queued",
        "sub_questions": [],
        "search_queries": [],
        "sources": [],
        "citations": [],
        "missing_evidence": [],
        "contradictions": [],
        "answer": "",
        "error": None,
        "iteration": 0,
        "max_iterations": max_iterations,
        "started_at": now,
        "updated_at": now,
        "cancelled": False,
    }


def state_snapshot(state: ResearchState) -> Dict[str, object]:
    return {
        "job_id": state.get("job_id"),
        "question": state.get("question"),
        "status": state.get("status"),
        "sub_questions": state.get("sub_questions", []),
        "search_queries": state.get("search_queries", []),
        "sources": [source.model_dump() for source in state.get("sources", [])],
        "citations": [
            citation.model_dump() for citation in state.get("citations", [])
        ],
        "missing_evidence": state.get("missing_evidence", []),
        "contradictions": state.get("contradictions", []),
        "answer": state.get("answer", ""),
        "error": state.get("error"),
        "iteration": state.get("iteration", 0),
        "max_iterations": state.get("max_iterations", 0),
        "cancelled": state.get("cancelled", False),
    }
