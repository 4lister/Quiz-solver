# 🧠 Real-Time Quiz Solver

A Python tool that solves quizzes in real time: captures your screen, extracts text via OCR, and sends the question to an LLM (Claude / OpenAI / Ollama) to get an answer.

> **Status:** M1 fully implemented, M2 partially done (CLI mode). UI overlay, tray icon, and hotkeys are in progress.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Using with LLM](#using-with-llm)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)

---

## Features

- 📸 **Screen capture** — full screen or selected region (ROI)
- 🔍 **OCR** — image pre-processing + text recognition via Tesseract or EasyOCR
- 🤖 **LLM integration** — supports Claude (Anthropic), OpenAI, and local models via Ollama
- 📋 **Quiz parsing** — automatically extracts the question and answer options from raw OCR text
- 📝 **Logging** — structured logs via `loguru`

---

## Architecture

```
Screenshot → Pre-processing → OCR → Parsing → LLM → Answer
   (mss)       (Pillow/cv2)  (Tess)  (parser)  (API)
```

The pipeline is orchestrated by `core/pipeline.py`.

---

## Requirements

### Python
- Python 3.9+

### System Dependencies

**Tesseract OCR** is required and must be installed separately from pip:

| OS | Command |
|---|---|
| Windows | Download the installer from [tesseract-ocr.github.io](https://tesseract-ocr.github.io/tessdoc/Downloads.html) |
| macOS | `brew install tesseract` |
| Ubuntu/Debian | `sudo apt install tesseract-ocr` |

After installation, verify that `tesseract` is available in your PATH:
```bash
tesseract --version
```

---

## Installation

```bash
git clone https://github.com/4lister/Quiz-solver.git
cd Quiz-solver

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` and fill in the relevant API keys:

```bash
cp .env.example .env
```

```env
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OLLAMA_BASE_URL=http://localhost:11434   # if using a local model
```

---

## Quick Start

Basic run — screen capture + OCR, no LLM:

```bash
python main.py
```

The program will:
1. Capture the primary screen
2. Pre-process the image and run OCR
3. Print the recognized text to the console

---

## Using with LLM

Add the `--llm` flag and set the appropriate API key in your environment:

```bash
# Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-... python main.py --llm

# OpenAI
OPENAI_API_KEY=sk-... python main.py --llm

# Ollama (local, no key needed)
python main.py --llm
```

The program will additionally:

4. Parse the question and answer options from the OCR text
5. Send a formatted prompt to the LLM
6. Print the recommended answer

---

## Project Structure

```
quiz-solver/
├── main.py               # Entry point (CLI)
├── requirements.txt
├── .env.example
│
├── capture/
│   └── screen.py         # Screen / ROI capture (mss + Pillow)
│
├── ocr/
│   ├── processor.py      # Image pre-processing + OCR
│   └── parser.py         # Question and answer option extraction
│
├── llm/
│   ├── client.py         # Abstraction over Claude / OpenAI / Ollama
│   └── prompt.py         # Prompt templates and formatting utilities
│
├── core/
│   └── pipeline.py       # Orchestration: capture → OCR → LLM
│
├── config/
│   ├── settings.py       # config.yaml loader + runtime settings model
│   └── config.yaml       # Configuration (OCR engine, LLM model, etc.)
│
├── utils/
│   └── logger.py         # loguru logging setup
│
└── logs/                 # Log files (gitignored)
```

---

## Roadmap

| Milestone | Status | Description |
|---|---|---|
| M1 | ✅ Done | Screen capture + OCR (Tesseract / EasyOCR) |
| M2 | 🔄 Partial | CLI client for LLM (Claude / OpenAI / Ollama) |
| M3 | ⏳ Planned | Answer overlay window rendered on top of screen |
| M4 | ⏳ Planned | System tray + configurable hotkeys |
| M5 | ⏳ Planned | Settings UI + question/answer history panel |
