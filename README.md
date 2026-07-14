<div align="center">

# 🎙️ Meeting Summarizer

**Turn meeting recordings into transcripts, summaries, and action items — automatically.**

[![CI](https://github.com/PranavB110/meeting-summarizer/actions/workflows/ci.yml/badge.svg)](https://github.com/PranavB110/meeting-summarizer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

[Demo Video](#-demo) • [Quick Start](#-getting-started) • [Architecture](#-architecture) • [API Docs](#-api-reference)

</div>

---

## 📌 Overview

Upload a meeting recording → get back a full **transcript**, an **executive summary**, **key decisions**, and **action items with owners** — in seconds, through a clean web UI or a REST API.

No manual note-taking. No re-listening to recordings to find who agreed to do what.

| Input | Output |
|---|---|
| 🎧 Meeting audio (MP3, WAV, M4A, MP4, WEBM, OGG) | 📝 Transcript · 📋 Summary · ✅ Action items · 🎯 Key decisions |

## 🎥 Demo

> 📹 *Demo video: [https://drive.google.com/drive/folders/1SJYEcvPkyIu1IYXikHgTesl1r896WzhE?usp=sharing]

## ✨ Features

- 🎧 **Accurate speech-to-text** — real transcription, not a toy demo
- 🧠 **AI-generated executive summaries** — concise, no fluff
- ✅ **Action item extraction** — owner + deadline pulled straight from the conversation
- 🎯 **Key decision tracking** — separated from general discussion
- 🖥️ **Drag-and-drop web UI** — live status updates while processing
- 🔌 **Full REST API** — usable independently of the UI, documented at `/docs`
- ⚙️ **Config-switchable AI providers** — swap ASR/LLM engines via `.env`, zero code changes
- 🐳 **One-command Docker deploy**
- ✅ **Automated tests + CI** — every push tested via GitHub Actions

## 🏗️ Architecture
```

Web UI / REST client
        |
        v
   FastAPI Backend
        |
        v
   ASR Provider  (faster-whisper)
        |
        v
   LLM Provider  (Groq)
        |
        v
  Structured JSON (summary, key_decisions, action_items)
        |
        v
   SQLite  (stores transcript, summary, status, metadata)
```   

Processing runs as a **background task** — uploads return instantly with a meeting ID, and the client polls for status/results. The API stays responsive no matter how long transcription takes.

### 🔀 Tiered provider architecture

Both ASR and LLM sit behind an abstract provider interface with a config-driven factory — swap engines per deployment tier without touching application code:

| Tier | ASR Engine | LLM Engine |
|---|---|---|
| **Free** *(this repo's default)* | `faster-whisper` — local, CPU-based, $0 cost | Groq (Llama 3.1 8B Instant) — free tier, cloud |
| **MVP** | OpenAI transcription API | GPT-5-mini (first pass) → GPT-5 (executive summary) |
| **Scale** | OpenAI transcription API | Chunked summarization: mini per chunk → merged by flagship model, with prompt caching |
| **Premium** | Same as MVP/Scale | + optional Claude-powered "Executive Summary" as a paid upgrade |

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite |
| ASR | faster-whisper (CTranslate2-optimized Whisper) |
| LLM | Groq API — Llama 3.1 8B Instant |
| Frontend | Vanilla HTML/CSS/JS — zero build step |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker |

## 📂 Project Structure
```
meeting-summarizer/
|-- backend/
|   |-- app/
|   |   |-- api/          FastAPI route handlers
|   |   |-- core/         Configuration (pydantic-settings)
|   |   |-- db/           SQLAlchemy session/engine
|   |   |-- models/       ORM models
|   |   |-- schemas/      Pydantic request/response schemas
|   |   |-- providers/
|   |   |   |-- asr/      ASR provider interface + implementations
|   |   |   `-- llm/      LLM provider interface + implementations
|   |   |-- services/     Business logic - pipeline orchestration
|   |   `-- main.py       App entrypoint
|   |-- tests/            pytest suite
|   |-- requirements.txt
|   `-- Dockerfile
|-- frontend/
|   `-- templates/
|       `-- index.html    Upload UI
|-- .github/
|   `-- workflows/
|       `-- ci.yml        GitHub Actions CI
`-- .env.example
```
## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com/keys) — no credit card required

### 1️⃣ Clone the repo

```bash
git clone https://github.com/PranavB110/meeting-summarizer.git
cd meeting-summarizer
```

### 2️⃣ Set up a virtual environment

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
# source venv/bin/activate     # macOS/Linux
```

### 3️⃣ Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

```bash
cd ..
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

### 5️⃣ Run it

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** for the web UI, or **http://127.0.0.1:8000/docs** for interactive API docs.

## 🐳 Running with Docker

```bash
docker build -t meeting-summarizer -f backend/Dockerfile .
docker run -d -p 8000:8000 --env-file .env meeting-summarizer
```

Visit **http://127.0.0.1:8000**.

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/meetings` | Upload audio, kicks off background processing |
| `GET` | `/api/meetings/{id}` | Poll for status and results |
| `GET` | `/api/meetings` | List all meetings |
| `GET` | `/api/health` | Liveness check |

```bash
curl -X POST http://127.0.0.1:8000/api/meetings -F "file=@meeting.wav"
# => {"id": "...", "status": "uploaded", "original_filename": "meeting.wav"}

curl http://127.0.0.1:8000/api/meetings/<id>
# => { "status": "completed", "transcript": "...", "summary": "...",
#      "key_decisions": [...], "action_items": [...] }
```

## 🧪 Running Tests

```bash
cd backend
pytest -v
```

Covers pipeline orchestration (status transitions, ASR/LLM failure handling) with mocked providers, plus API contract tests. Real ASR/LLM integrations are verified manually against live audio and the Groq API.

## 💡 Design Decisions

- **Provider pattern for ASR/LLM** — enables the tiered free → mvp → scale → premium architecture without rewriting application code.
- **Background task processing** — uploads return instantly; the client polls, keeping the API responsive regardless of processing time.
- **faster-whisper for the free tier** — zero cost, no API key, no rate limits; OpenAI's API is a drop-in swap for production tiers.
- **Explicit `language="en"` for ASR** — Whisper's auto-detection proved unreliable on short/quiet clips during testing (misdetected clear English speech as Telugu on one real recording); forcing the language fixed it reliably.

## 📄 License

MIT
