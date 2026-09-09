"""
Step 6: UI + feedback loop
----------------------------
Ties steps 1-5 together into a simple Streamlit app, and captures
thumbs up/down feedback to a CSV — your evidence for the "80%+
usefulness" success metric in the problem statement.

Run with:  streamlit run app.py
"""

import csv
import os
from datetime import datetime
from dotenv import load_dotenv

import streamlit as st

from sample_logs import SAMPLE_LOGS
from preprocessor import parse_log
from kb import match_kb
from llm_client import build_prompt, call_gemini

FEEDBACK_FILE = "feedback.csv"

load_dotenv()

def _log_feedback(verdict: str) -> None:
    file_exists = os.path.exists(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "verdict"])
        writer.writerow([datetime.now().isoformat(), verdict])


st.set_page_config(page_title="Deployment Troubleshooting Assistant", layout="centered")
st.title("RootCause.ai")
st.caption("Paste a deployment log or pick a sample. The assistant analyzes it and suggests fixes.")

# --- Step 1: Input ---
api_key = st.sidebar.text_input(
    "Gemini API key", value=os.environ.get("GEMINI_API_KEY", ""), type="password"
)

source = st.radio("Input method", ["Pick a sample log", "Paste my own log"], horizontal=True)

if source == "Pick a sample log":
    sample_name = st.selectbox("Sample log", list(SAMPLE_LOGS.keys()))
    log_text = SAMPLE_LOGS[sample_name]
    st.code(log_text.strip(), language="text")
else:
    log_text = st.text_area("Paste log/error text here", height=220)

analyze_clicked = st.button("Analyze", type="primary", disabled=not log_text or not api_key)

if not api_key:
    st.info("Enter your Gemini API key in the sidebar to run analysis.")

# --- Steps 2-5: run pipeline ---
if analyze_clicked and log_text and api_key:
    with st.spinner("Parsing log and consulting the model..."):
        signals = parse_log(log_text)                       # Step 2
        kb_hit = match_kb(log_text)                          # Step 3
        prompt = build_prompt(signals["cleaned_text"], signals, kb_hit)  # Step 4 (prep)
        result = call_gemini(prompt, api_key)                # Step 4 (call) + Step 5 (parsed JSON)

    st.session_state["last_result"] = result
    st.session_state["last_log_name"] = source

# --- Display result ---
result = st.session_state.get("last_result")
if result:
    st.divider()
    if "error" in result:
        st.error(f"Analysis failed: {result['error']}")
    else:
        st.subheader("Issue summary")
        st.write(result.get("issue_summary", "—"))

        conf = result.get("confidence", "unknown")
        badge = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(conf, "⚪")
        st.markdown(f"**Root cause** ({badge} confidence: {conf})")
        st.write(result.get("root_cause", "—"))

        st.markdown("**Recommended next steps**")
        for i, step in enumerate(result.get("recommended_steps", []), 1):
            st.markdown(f"{i}. {step}")

        related = result.get("related_log_lines", [])
        if related:
            with st.expander("Related log lines"):
                for line in related:
                    st.code(line, language="text")

        # --- Feedback loop ---
        st.divider()
        st.write("Was this useful?")
        col1, col2 = st.columns(2)
        if col1.button("👍 Useful"):
            _log_feedback("useful")
            st.success("Thanks for the feedback!")
        if col2.button("👎 Not useful"):
            _log_feedback("not_useful")
            st.info("Thanks — noted for improvement.")
