"""
Step 2: Preprocessing
----------------------
Deterministic, no AI involved. Pulls structured signals out of raw
log text so the LLM prompt in step 4 has clean, high-signal input
instead of a huge noisy blob.
"""

import re


def parse_log(raw_text: str) -> dict:
    """Extract structured signals from a raw log string.

    Returns a dict with:
      - cleaned_text: whitespace-normalized log, capped in length
      - error_lines: lines that look like errors/warnings
      - exception_names: e.g. KeyError, PermissionDenied
      - exit_codes: numeric exit/status codes found
      - timestamps_stripped: cleaned_text with leading timestamps removed
    """
    lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]

    error_lines = [
        l for l in lines
        if re.search(r"\b(ERROR|FATAL|Exception|Traceback|CrashLoop|OOMKilled|PermissionDenied|Timed out|timeout)\b", l, re.IGNORECASE)
    ]

    exception_names = sorted(set(re.findall(
        r"\b([A-Z][a-zA-Z]*(?:Error|Exception|Denied|Killed|BackOff))\b", raw_text
    )))

    exit_codes = sorted(set(re.findall(r"exit code[:=]?\s*(\d+)", raw_text, re.IGNORECASE)))

    # Strip ISO timestamps from the front of each line for a cleaner view
    timestamps_stripped = "\n".join(
        re.sub(r"^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", "", l) for l in lines
    )

    cleaned_text = timestamps_stripped[:4000]  # cap length for prompt safety

    return {
        "cleaned_text": cleaned_text,
        "error_lines": error_lines,
        "exception_names": exception_names,
        "exit_codes": exit_codes,
    }


if __name__ == "__main__":
    # Quick manual test
    from sample_logs import SAMPLE_LOGS
    sample = SAMPLE_LOGS["Missing Environment Variable"]
    signals = parse_log(sample)
    for k, v in signals.items():
        print(f"{k}: {v}\n")
