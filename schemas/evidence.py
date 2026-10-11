from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(min_length=1, description="Focused research search query.")
    max_results: int = Field(default=4, ge=1, le=5)
    recency_days: Optional[int] = Field(default=None, ge=1)
    allowed_domains: Optional[List[str]] = None


class PageFetchInput(BaseModel):
    url: str = Field(min_length=1, description="HTTP(S) URL to fetch.")


class PDFParseInput(BaseModel):
    url_or_path: str = Field(min_length=1, description="PDF URL or local path.")


class ClaimRecord(BaseModel):
    claim: str = Field(min_length=1)
    quote: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    publication_date: Optional[str] = "Unknown"
    methodology: Optional[str] = "N/A"
    sample_size_or_dataset: Optional[str] = "N/A"
    limitations: Optional[str] = "N/A"
    confidence: Literal["high", "medium", "low"] = "medium"


class ResearchSubQuestion(BaseModel):
    sub_question: str
    required_evidence_type: str


class ResearchPlan(BaseModel):
    main_query: str
    sub_questions: List[ResearchSubQuestion]
    target_domains: List[str] = Field(default_factory=list)


class AnswerEvaluation(BaseModel):
    verdict: Literal["pass", "revise"]
    missing_evidence: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
