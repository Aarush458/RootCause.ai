# RootCause.ai: Deployment issue troubleshooting assistant

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

## IMPORTANT 
Installing Tesseract OCR

Depending on your operating system, follow the instructions below to install the Tesseract OCR engine:

### macOS
If you're on macOS, you can install the Tesseract package directly via requirements.txt

### Windows
If you are on Windows, you will need to install the software manually and configure your system path. Follow these steps:
1. **Download the installer:** Get the latest `.exe` installer from the [UB Mannheim Tesseract wiki](https://github.com/UB-Mannheim/tesseract/wiki).
2. **Run the setup:** Execute the downloaded file and follow the on-screen prompts. Note your installation directory (by default, it is usually `C:\Program Files\Tesseract-OCR`).
3. **Add to PATH:** To ensure Tesseract works properly in your command line or scripts, you must add its folder to your environment variables:
   - Open the Windows start menu, search for **Environment Variables**, and select **Edit the system environment variables**.
   - Click the **Environment Variables...** button at the bottom.
   - In the **System variables** section, find and select the `Path` variable, then click **Edit**.
   - Click **New** and paste the path to your Tesseract installation folder (e.g., `C:\Program Files\Tesseract-OCR`).
   - Click **OK** on all the windows to apply the changes. 

*(Alternatively, you can install it via the command line using Windows Package Manager by running `winget install --id UB-Mannheim.TesseractOCR`.)*

### Other Operating Systems (Linux)
For Linux distributions, Tesseract is available natively and can be installed via your default package manager. 
* **Ubuntu:** 
  `sudo apt update`
  `sudo apt install tesseract-ocr`
   

## Input format
- Screenshots of error logs
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
3. **LLM reasoning (Gemini 3.6 Flash)** — the model receives the
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


