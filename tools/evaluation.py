from typing import Any, Dict, List

from langchain_core.tools import tool

from tools.extraction import GLOBAL_EVIDENCE_LEDGER


@tool("evaluate_answer")
def evaluate_answer(draft_summary: str, sub_questions_covered: List[str]) -> Dict[str, Any]:
    """Check whether the evidence ledger supports a complete comparative answer."""
    missing = []
    if len(GLOBAL_EVIDENCE_LEDGER) < 3:
        missing.append("At least three distinct source-backed claims are required.")
    text = " ".join(
        f"{record.claim} {record.methodology}" for record in GLOBAL_EVIDENCE_LEDGER
    ).lower()
    if not any(term in text for term in ("transformer", "attention")):
        missing.append("Missing evidence about transformer or attention-based models.")
    if not any(term in text for term in ("classical", "random forest", "svm", "xgboost")):
        missing.append("Missing evidence about classical ML models.")
    return {
        "verdict": "pass" if not missing else "revise",
        "missing_evidence": missing,
        "unsupported_claims": [] if draft_summary else ["Draft summary is empty."],
        "covered_sub_questions": sub_questions_covered,
        "total_evidence_claims": len(GLOBAL_EVIDENCE_LEDGER),
    }


@tool("finalize_report")
def finalize_report(
    synthesis: str,
    comparison_table_markdown: str,
    limitations_analysis: str,
) -> str:
    """Assemble a cited report from the current evidence ledger."""
    evidence = []
    sources = []
    for index, record in enumerate(GLOBAL_EVIDENCE_LEDGER, 1):
        evidence.append(
            f"[{index}] **Claim:** {record.claim}\n"
            f"    - **Quote:** \"{record.quote}\"\n"
            f"    - **Methodology:** {record.methodology} | "
            f"**Dataset:** {record.sample_size_or_dataset}\n"
            f"    - **Limitations:** {record.limitations}\n"
            f"    - **Source:** {record.source_url} ({record.publication_date})"
        )
        if record.source_url not in sources:
            sources.append(record.source_url)
    return (
        "# Systematic Comparative Analysis\n\n"
        f"## Executive Synthesis\n{synthesis}\n\n"
        f"## Quantitative Benchmark Comparison\n{comparison_table_markdown}\n\n"
        f"## Methodological Limitations\n{limitations_analysis}\n\n"
        "## Verified Evidence Ledger\n" + "\n\n".join(evidence) + "\n\n"
        "## Primary References\n" + "\n".join(f"- {url}" for url in sources)
    )
