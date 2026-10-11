# SiftAI Roadmap

## Current baseline

- Groq model integration
- FastAPI service
- Browser dashboard
- Bounded search and retrieval output
- Evidence-ledger prototype
- Typed research state
- Search provider abstraction with Tavily and DDGS

## MVP phase 1: controlled research engine

**Goal:** replace the legacy free-form tool loop with a predictable workflow.

- Build LangGraph nodes and conditional edges
- Move evidence into per-job state
- Add source ranking and deduplication
- Add citation records and verification
- Preserve bounded time and iteration budgets

## MVP phase 2: reliable retrieval

- Add Tavily credentials and test provider fallback
- Add Jina Reader or Firecrawl
- Improve PDF extraction
- Add retries, timeouts, and canonical URL handling
- Add source quality and recency scoring

## MVP phase 3: streaming product surface

- Add SSE event streaming
- Add cancellation and retry endpoints
- Render inline citations and source cards
- Display partial answer and evidence updates
- Add useful error and empty-result states

## MVP phase 4: persistence and evaluation

- Persist jobs, sources, citations, and events
- Create a fixed evaluation question set
- Measure citation quality and runtime
- Add token and provider usage tracking
- Add regression tests for failure paths

## Production hardening

- Authentication and user isolation
- PostgreSQL and Redis
- Background worker queue
- LangGraph checkpoints and resume
- SSRF protection and content sanitization
- Rate limiting and usage quotas
- Observability, alerts, and backups
- CI/CD and deployment

## Definition of done for the MVP

- A user can submit a question and receive a cited report.
- At least one search provider failure can recover through fallback or retry.
- Every displayed factual claim has a source relationship.
- An incomplete run is explicitly labeled incomplete.
- The UI shows live workflow stages and source evidence.
- Research jobs do not share evidence.
- The system respects configured time, iteration, and content budgets.
