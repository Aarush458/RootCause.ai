"""
Step 3: Pattern match + knowledge base
----------------------------------------
A lightweight dict lookup — not a vector DB, no embeddings needed for
a 2-hour build. If the log text matches a known signature, we hand
that grounding context to the LLM in step 4 so it doesn't have to
guess the root cause from scratch.
"""

KB_PATTERNS = [
    {
        "match": ["CrashLoopBackOff", "Liveness probe failed", "Readiness probe failed"],
        "cause": "Container is failing its health checks and Kubernetes is repeatedly restarting it.",
        "fix": "Check the readiness/liveness probe config (path, port, timeout) and confirm the app is actually listening on that port at startup.",
    },
    {
        "match": ["OOMKilled", "exit code 137", "Memory usage at"],
        "cause": "Container exceeded its memory limit and was killed by the OOM killer.",
        "fix": "Increase the memory limit/request, or investigate a memory leak in the workload.",
    },
    {
        "match": ["KeyError", "environ", "not set", "JWT_SECRET"],
        "cause": "A required environment variable is missing from the deployment config.",
        "fix": "Add the missing environment variable to the deployment manifest / secret store and redeploy.",
    },
    {
        "match": ["PermissionDenied", "does not have permission", "PermissionDenied desc"],
        "cause": "The service account or IAM role lacks the required permission for this action.",
        "fix": "Grant the service account the missing IAM role/permission (least-privilege scoped to the needed resource).",
    },
    {
        "match": ["Connection timed out", "Max retries exceeded", "could not connect to server"],
        "cause": "The service cannot reach a downstream dependency (likely DB) — network policy, wrong host, or the dependency is down.",
        "fix": "Verify the host/port is correct, check network policies/security groups, and confirm the downstream service is running.",
    },
]


def match_kb(raw_text: str) -> dict | None:
    """Return the first KB entry whose keywords appear in the raw log text."""
    text_lower = raw_text.lower()
    for entry in KB_PATTERNS:
        if any(keyword.lower() in text_lower for keyword in entry["match"]):
            return {"cause": entry["cause"], "fix": entry["fix"]}
    return None


if __name__ == "__main__":
    from sample_logs import SAMPLE_LOGS
    for name, log in SAMPLE_LOGS.items():
        print(name, "->", match_kb(log))
