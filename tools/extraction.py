from typing import Any, Dict, List

from langchain_core.tools import tool

from schemas.evidence import ClaimRecord

GLOBAL_EVIDENCE_LEDGER: List[ClaimRecord] = []


def clear_evidence_ledger() -> None:
    GLOBAL_EVIDENCE_LEDGER.clear()


def evidence_snapshot() -> List[Dict[str, Any]]:
    return [record.model_dump() for record in GLOBAL_EVIDENCE_LEDGER]


@tool("extract_claims")
def extract_claims(claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Record source-backed claims in the evidence ledger."""
    added = []
    for item in claims:
        try:
            record = ClaimRecord.model_validate(item)
        except ValueError as exc:
            return {"status": "error", "error": f"Invalid claim record: {exc}"}
        GLOBAL_EVIDENCE_LEDGER.append(record)
        added.append(record.model_dump())
    return {
        "status": "success",
        "added_claims": len(added),
        "total_ledger_entries": len(GLOBAL_EVIDENCE_LEDGER),
        "recorded_claims": [
            {
                "claim": record.claim,
                "source_url": record.source_url,
                "confidence": record.confidence,
            }
            for record in added
        ],
    }


@tool("check_contradictions")
def check_contradictions() -> Dict[str, Any]:
    """Group collected claims by methodology for manual contradiction review."""
    if not GLOBAL_EVIDENCE_LEDGER:
        return {"status": "empty", "message": "No claims in evidence ledger."}
    grouped: Dict[str, int] = {}
    for record in GLOBAL_EVIDENCE_LEDGER:
        methodology = record.methodology or "General"
        grouped[methodology] = grouped.get(methodology, 0) + 1
    return {"ledger_size": len(GLOBAL_EVIDENCE_LEDGER), "evidence_by_methodology": grouped}
