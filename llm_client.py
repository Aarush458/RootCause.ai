"""
Step 4: LLM reasoning
Step 5: Structured output
----------------------------
Builds the prompt (log + KB grounding), calls Gemini with a forced
JSON response schema, and parses the result into a plain dict.

Uses the current `google-genai` SDK (`pip install google-genai`).
The older `google-generativeai` package is deprecated — don't use it.
"""

import json
import os
from google import genai
from google.genai import types


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_summary": {"type": "string"},
        "root_cause": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "recommended_steps": {"type": "array", "items": {"type": "string"}},
        "related_log_lines": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["issue_summary", "root_cause", "confidence", "recommended_steps"],
}


def build_prompt(cleaned_text: str, signals: dict, kb_match: dict | None) -> str:
    kb_context = (
        f"Known pattern match:\ncause: {kb_match['cause']}\nsuggested fix: {kb_match['fix']}"
        if kb_match else "No known pattern match found — reason from the log itself."
    )
    exceptions = ", ".join(signals.get("exception_names", [])) or "none detected"
    exit_codes = ", ".join(signals.get("exit_codes", [])) or "none detected"

    return f"""You are a DevOps troubleshooting assistant helping an engineer
understand a deployment failure quickly. Be specific and actionable.

Log excerpt (timestamps stripped):
{cleaned_text}

Detected exception/error types: {exceptions}
Detected exit codes: {exit_codes}
{kb_context}

Respond with a concise, human-readable root cause analysis and 2-4 ranked,
actionable next steps an engineer can take right now."""


def call_gemini(prompt: str, api_key: str, model_name: str = "gemini-3.8-flash") -> dict:
    """Call Gemini with forced JSON output. Returns a parsed dict.

    On failure (rate limit, network, bad parse) returns a dict with an
    "error" key instead of raising, so the UI can degrade gracefully.
    """
    try:
        client = genai.Client(api_key= api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                max_output_tokens=500,
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
    except Exception as exc:  # noqa: BLE001 - want to surface any failure to the UI
        return {"error": str(exc)}


if __name__ == "__main__":
    # Manual smoke test — requires GEMINI_API_KEY env var set
    from sample_logs import SAMPLE_LOGS
    from preprocessor import parse_log
    from kb import match_kb

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY env var to run this smoke test.")
    else:
        log = SAMPLE_LOGS["Missing Environment Variable"]
        signals = parse_log(log)
        kb = match_kb(log)
        prompt = build_prompt(signals["cleaned_text"], signals, kb)
        result = call_gemini(prompt, api_key)
        print(json.dumps(result, indent=2))
