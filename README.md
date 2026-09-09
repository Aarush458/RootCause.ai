# Deployment issue troubleshooting assistant

A single-agent GenAI tool that takes a deployment log/error and returns a
human-readable root cause summary plus ranked, actionable next steps.

Built for TCS Technology Day — IT Application Maintenance track.

## Project structure

```
deployment_assistant/
├── sample_logs.py     # Step 1 — 5 synthetic sample logs for the demo
├── preprocessor.py     # Step 2 — regex parsing, no AI involved
├── kb.py                # Step 3 — small known-error-pattern lookup
├── llm_client.py         # Step 4/5 — Gemini prompt + structured JSON output
├── app.py                 # Step 6 — Streamlit UI + feedback capture
├── requirements.txt
└── README.md
```

## Setup

1. Get a free Gemini API key from https://aistudio.google.com/apikey
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```
4. Paste your Gemini API key into the sidebar field (or set it as an
   environment variable `GEMINI_API_KEY` before launching so it's
   pre-filled).

## Input format

- Plain text deployment/application logs (Kubernetes events, stack
  traces, container logs, CI/CD output).
- No strict schema required — the preprocessing step strips ISO
  timestamps and extracts exception names / exit codes with regex, so
  it tolerates messy real-world log formatting.
- Five ready-made sample logs are included covering: CrashLoopBackOff,
  OOMKilled, missing env var, IAM permission denied, and DB connection
  timeout — useful for demoing without needing a live cluster.

## AI approach

1. **Preprocessing (deterministic)** — regex extracts error lines,
   exception names, and exit codes; timestamps are stripped to reduce
   prompt noise.
2. **Knowledge base grounding (deterministic)** — a small hand-curated
   dict of ~5 common deployment failure signatures. If the log matches
   one, that known cause/fix is injected into the prompt as grounding
   context (a lightweight, non-vector form of retrieval-augmented
   generation).
3. **LLM reasoning (Gemini 2.5 Flash)** — the model receives the
   cleaned log, extracted signals, and any KB match, and is forced
   (via `response_schema`) to return strict JSON: issue summary, root
   cause, confidence level, and ranked next steps. Structured output
   removes the need for fragile text parsing.
4. **Feedback loop** — thumbs up/down on each result appends to
   `feedback.csv`, giving a measurable usefulness rate for the
   success metric (target: 80%+ marked useful).

## Notes

- If the Gemini call fails (bad key, rate limit, network), the UI
  shows a clear error instead of crashing.
