# VidScope AI

**VidScope AI** is a multimodal video Q&A application. Upload a video, let the pipeline transcribe its audio and index its visual keyframes, and ask questions grounded in both spoken transcript excerpts and visual frames—with clickable timestamps that seek the video player to the exact supporting moments.

## Features

- **Audio & Transcript Pipeline:** Extracts 16 kHz mono audio with `FFmpeg`, transcribes speech with timestamps via `faster-whisper`, chunks passages with pause-aware merging, and indexes `MiniLM` embeddings in `FAISS`.
- **Visual Frame Pipeline:** Samples representative keyframes with `OpenCV` scene-change detection, embeds frames and text queries into a shared vector space using `CLIP` (`openai/clip-vit-base-patch32`), and indexes visual vectors in a separate `FAISS` index.
- **Multimodal RAG & Vision-Language Grounding:** Combines top-k transcript passages with matched video frame images for vision-language answer generation (supporting Groq, OpenAI, and xAI).
- **Interactive Two-Panel Workspace:** React + Vite + Tailwind CSS frontend with live processing status polling, clickable timestamp chips (`03:42`), and visual frame evidence cards that seek the video player on click.

## Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **AI / ML:** PyTorch, `faster-whisper`, `sentence-transformers` (`all-MiniLM-L6-v2`), Hugging Face `transformers` (`CLIP`), `FAISS`, `OpenCV`, `FFmpeg`

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- `FFmpeg` installed and available on `PATH`

### 1. Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Set your `LLM_PROVIDER`, `LLM_MODEL`, and `LLM_API_KEY` in `backend/.env`, then start the API server:
```bash
uvicorn app.main:app --port 8000 --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.
