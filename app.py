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
import pytesseract
from PIL import Image
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


st.set_page_config(page_title="RootCause.ai: Deployment Troubleshooting Assistant", layout="centered")
st.title("RootCause.ai")
st.caption("Paste a deployment log or pick a sample. The assistant analyzes it and suggests fixes.")

api_key = st.sidebar.text_input(
    "Gemini API keyThanks for the hackathon project we were building. I'm going to share with you a file of app.py, and there's an error that's appearing. I want you to correct it. Simple error. ", value=os.environ.get("GEMINI_API_KEY", ""), type="password"
)

source = st.radio("Input method", ["Pick a sample log", "Paste my own log", "Upload a log screenshot"], horizontal=True)
if source == "Pick a sample log":
    sample_name = st.selectbox("Sample log", list(SAMPLE_LOGS.keys()))
    log_text = SAMPLE_LOGS[sample_name]
    st.code(log_text.strip(), language="text")
elif source == "Paste my own log":
    log_text = st.text_area("Paste log/error text here", height=220)
else:
    uploaded_image = st.file_uploader("Upload a log screenshot", type=["png", "jpg", "jpeg"])
    log_text = ""
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded screenshot", use_container_width=True)
        with st.spinner("Extracting text via OCR..."):
            log_text = pytesseract.image_to_string(image)
        st.text_area("Extracted text (edit if OCR made mistakes)", value=log_text, height=220, key="ocr_output")
        log_text = st.session_state.get("ocr_output", log_text)

if not api_key:
    st.info("Enter your Gemini API key in the sidebar to run analysis.")
analyze_clicked = st.button("🔍 Analyze")
if analyze_clicked and log_text and api_key:
    with st.spinner("Parsing log and consulting the model..."):
        signals = parse_log(log_text)                  
        kb_hit = match_kb(log_text)                          
        prompt = build_prompt(signals["cleaned_text"], signals, kb_hit)  
        result = call_gemini(prompt, api_key)               

    st.session_state["last_result"] = result
    st.session_state["last_log_name"] = source
    st.session_state["last_log_text"] = log_text

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
         # --- Regenerate ---
        st.divider()
        if st.button("🔄 Not satisfied? Regenerate response"):
            stored_log = st.session_state.get("last_log_text", "")
            with st.spinner("Regenerating..."):
                signals = parse_log(stored_log)
                kb_hit = match_kb(stored_log)
                prompt = build_prompt(signals["cleaned_text"], signals, kb_hit)
                new_result = call_gemini(prompt, api_key)
            st.session_state["last_result"] = new_result
            st.rerun()

        st.divider()
        st.write("Was this useful?")
        col1, col2 = st.columns(2)
        if col1.button("👍 Useful"):
            _log_feedback("useful")
            st.success("Thanks for the feedback!")
        if col2.button("👎 Not useful"):
            _log_feedback("not_useful")
            st.info("Thanks — noted for improvement.")
