# SiftAI Development Guide

## Local setup

Use the existing Conda environment:

```powershell
conda activate agentic
cd "C:\Amulya\Projects\New folder"
pip install -r requirements.txt
```

Do not commit `.env`. Configure:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
TAVILY_API_KEY=optional_tavily_key
```

## Run the application

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Development rules

- Keep research state typed and serializable.
- Do not add another process-global evidence ledger.
- Keep provider-specific code behind an adapter.
- Bound all external calls with timeouts.
- Never pass unbounded page content to the model.
- Emit structured events for user-visible stages.
- Return explicit errors; do not silently manufacture sources or answers.
- Keep the CLI working while the API evolves.

## Validation checklist

Before considering a workflow change complete:

1. Run Python syntax validation.
2. Test provider success, empty results, timeout, and fallback behavior.
3. Test a short factual question.
4. Test a multi-part comparison question.
5. Confirm citations point to retrieved sources.
6. Confirm a failed job is visible in the dashboard.
7. Confirm cancellation and budget exhaustion are explicit.
8. Check that no API key appears in logs or responses.

## Important architectural boundary

The current application is a prototype. `api.py` still invokes the legacy
`AgentExecutor`. The target architecture in `ARCHITECTURE.md` is authoritative
for new work: implement the LangGraph workflow before adding more autonomous
tool behavior.
