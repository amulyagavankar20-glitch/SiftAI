# SiftAI

Evidence-first autonomous research for Perplexity-style answers.

SiftAI plans a research question, searches the web, retrieves sources, extracts
verifiable claims, checks coverage and contradictions, and synthesizes a cited
report with visible research activity.

## Documentation

- [Product requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Development guide](docs/DEVELOPMENT.md)

## Current status

The repository currently contains a working Groq/FastAPI/dashboard prototype,
typed research-state foundations, and a replaceable search-provider layer. The
next implementation step is migrating the legacy tool loop to the documented
LangGraph workflow.

## Run locally

```powershell
conda activate agentic
cd "C:\Amulya\Projects\New folder"
pip install -r requirements.txt
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Configure secrets in `.env`; never commit that file.
