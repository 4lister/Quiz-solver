# Real-Time Quiz Solver (M1–M2 Prototype)

This is a Python implementation of the **Real-Time Quiz Solver** described in the provided technical specification.  
The current version focuses on the first milestones:

- M1: **Захват + OCR** — screen capture → pre-processing → text via Tesseract
- M2 (partial): **LLM интеграция** — a simple CLI client for sending recognized text to an LLM API

Higher-level UI features (overlay window, tray icon, settings UI, history panel, hotkeys configuration) are scaffolded in the package layout and can be implemented incrementally.

## Project layout

- `main.py` — entry point (CLI demo for capture + OCR + optional LLM)
- `capture/screen.py` — screen/ROI capture via `mss`/Pillow
- `ocr/processor.py` — image pre-processing + OCR (Tesseract / EasyOCR)
- `ocr/parser.py` — parsing quiz question + answer options from raw OCR text
- `llm/client.py` — abstraction over Claude / OpenAI / Ollama via env-configured API keys
- `llm/prompt.py` — prompt templates and formatting utilities
- `core/pipeline.py` — orchestration from capture → OCR → LLM
- `utils/logger.py` — loguru-based logging setup
- `config/settings.py` — `config.yaml` loading plus runtime settings model

## Quick start

```bash
cd quiz-solver
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt
python main.py
```

By default, `main.py` will:

1. Capture the primary screen once (full-screen).
2. Run the pre-processing + OCR pipeline.
3. Print the recognized text.

To use LLM answering, set the corresponding API key in your environment (e.g. `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`) and enable the `--llm` flag in `main.py` (see inline help).

