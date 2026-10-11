# SiftAI Architecture

## 1. Architectural principles

1. **Evidence before synthesis**: the writer can only cite recorded evidence.
2. **Explicit state**: research progress lives in a typed per-job state object.
3. **Bounded autonomy**: every loop has time, iteration, source, and token limits.
4. **Provider independence**: search and extraction providers are replaceable.
5. **Observable execution**: every meaningful stage emits a structured event.
6. **Graceful failure**: a provider failure is visible and recoverable when possible.
7. **Job isolation**: one research request must never reuse another request's ledger.

## 2. Target system

```text
┌───────────────────────┐
│ Browser research UI   │
│ answer + sources      │
└───────────┬───────────┘
            │ SSE / REST
┌───────────▼───────────┐
│ FastAPI application   │
│ auth, jobs, limits    │
└───────────┬───────────┘
            │
┌───────────▼───────────┐
│ LangGraph workflow    │
│ typed ResearchState   │
└──┬──────┬──────┬──────┘
   │      │      │
   │      │      └──────────────┐
   │      └─────────────┐       │
┌──▼────────┐  ┌────────▼────┐ ┌▼────────────┐
│ Groq LLM  │  │ Search      │ │ Retrieval   │
│ planning  │  │ Tavily/DDGS │ │ Jina/PDF    │
└───────────┘  └─────────────┘ └─────────────┘
            │
┌───────────▼───────────┐
│ Evidence persistence   │
│ PostgreSQL + cache     │
└───────────────────────┘
```

## 3. LangGraph workflow

### Nodes

- `plan`: decompose the question and define evidence requirements.
- `search`: execute bounded queries through the provider abstraction.
- `rank_sources`: deduplicate, score, and select sources.
- `fetch`: retrieve readable page or PDF content.
- `extract_claims`: create claims with exact supporting quotes.
- `verify`: validate claim-to-source relationships and identify conflicts.
- `evaluate`: score coverage, freshness, source quality, and citation support.
- `synthesize`: write the final cited report.
- `fail`: produce an explicit failure state and user-facing explanation.

### Edges

```text
plan -> search -> rank_sources -> fetch -> extract_claims -> verify -> evaluate
evaluate -- missing evidence --> search
evaluate -- sufficient evidence --> synthesize
any node -- recoverable provider error --> retry or fallback
any node -- budget exhausted --> synthesize partial answer or fail
```

The workflow must use conditional edges instead of relying on an unconstrained
LLM tool loop to decide whether it is finished.

## 4. Research state

The canonical state is defined in `schemas/research.py` and includes:

- Job identity and question
- Model and execution budgets
- Current status and iteration
- Sub-questions and search queries
- Source records
- Citation records
- Missing evidence and contradictions
- Partial/final answer
- Error and cancellation state

The current code contains this typed foundation. The API still uses the legacy
`AgentExecutor`; migrating it to the graph is the next implementation step.

## 5. Source and citation model

### Source

A source has:

- Stable ID
- Title and canonical URL
- Snippet and fetched content
- Publication date when available
- Source type
- Quality score
- Fetch status and error

### Citation

A citation has:

- Stable ID
- Source ID
- Claim text
- Exact supporting quote
- Confidence
- Verification status

The final renderer should cite citation IDs rather than reconstructing URLs from
untrusted model output.

## 6. Search and retrieval providers

### Search

The current provider order is:

1. Tavily when `TAVILY_API_KEY` is configured
2. DDGS fallback

The provider layer must return a common result shape and handle retries,
timeouts, empty results, and provider-specific errors.

### Retrieval

The target MVP should use a readable-content provider such as Jina Reader or
Firecrawl, with direct HTTP/PDF extraction as a fallback. Retrieved content
must be bounded before entering the LLM context.

## 7. API and events

The API should expose:

- `POST /api/research` — create a job
- `GET /api/research/{id}` — current job snapshot
- `GET /api/research/{id}/events` — event history
- `GET /api/research/{id}/stream` — SSE stream
- `POST /api/research/{id}/cancel` — request cancellation
- `POST /api/research/{id}/retry` — retry a failed job
- `GET /health` — service health

Event examples:

```json
{"type": "search_started", "query": "VLA models 2025"}
{"type": "source_found", "source_id": "src-03", "title": "VLA survey"}
{"type": "claim_verified", "citation_id": "cit-04", "confidence": "high"}
{"type": "answer_ready", "citation_count": 12}
```

## 8. Persistence evolution

### Prototype

- In-memory jobs
- In-memory evidence
- One serialized research job

### MVP

- SQLite or PostgreSQL job records
- Per-job source and citation records
- Event history
- Research-session retrieval

### Production

- PostgreSQL for durable state
- Redis for queueing and transient events
- Background workers
- Object storage for large source documents
- Checkpointed LangGraph state

## 9. Security boundaries

- `.env` is server-only and ignored by Git.
- Browser clients receive job data, never provider secrets.
- URL fetching requires scheme and host validation.
- Retrieved content is data, not instructions.
- HTML/Markdown output is sanitized before rendering.
- CORS is restricted by deployment configuration.
