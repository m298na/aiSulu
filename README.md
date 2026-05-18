# AI.Sulu MVP

AI.Sulu is a kiosk-style AI assistant for a university lobby. This MVP runs fully in mock mode by default, answers from a local FAQ knowledge base, logs every question, provides an admin panel, and includes scaffolding for OpenAI, Whisper, ElevenLabs, and avatar-provider integrations.

## Architecture

### 1. Runtime modes

- `Idle mode`: avatar stays on screen, rotating greeting text is shown.
- `Trigger mode`: visitor starts interaction and chooses text or voice flow.
- `Dialog mode`: visitor asks a question, AI.Sulu answers from the local knowledge base, OpenAI, or fallback.
- `Fallback mode`: if confidence is low and no external model is available, AI.Sulu returns a safe handoff phrase.

### 2. Backend

- `FastAPI` serves chat, knowledge base, logs, admin, and voice scaffold endpoints.
- `SQLite` stores FAQ records and user question logs.
- `JSON seed file` provides the starter knowledge base and can be reloaded from admin.
- `Service layer` separates retrieval, chat orchestration, OpenAI integration, voice stubs, and log persistence.

### 3. Frontend

- `React + Vite` renders the kiosk screen and admin panel.
- `Avatar component` is lightweight and animated, but the code is isolated so D-ID, HeyGen, or Unreal integration can replace it later.
- `Admin panel` supports FAQ CRUD, knowledge-base reload, and log viewing.

### 4. Deployment

- `Dockerfile` for backend.
- `Dockerfile + Nginx` for frontend.
- `docker-compose.yml` to run both services together.

## Project structure

```text
ai-sulu/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── data/
│   │   └── logs/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   ├── styles/
│   │   └── App.jsx
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Main files and what they do

### Backend

- `backend/app/main.py`
  Starts FastAPI, enables CORS, creates tables, seeds FAQ data, and mounts routers.
- `backend/app/config.py`
  Central settings from environment variables and filesystem paths.
- `backend/app/models.py`
  SQLAlchemy models for FAQs and user question logs.
- `backend/app/routes/chat.py`
  Chat endpoint plus STT/TTS scaffolding endpoints.
- `backend/app/routes/knowledge_base.py`
  Public FAQ listing and search endpoints.
- `backend/app/routes/logs.py`
  Question-log listing and usage statistics.
- `backend/app/routes/admin.py`
  Admin CRUD for FAQs and seed reload.
- `backend/app/services/chat_service.py`
  Core answer pipeline: retrieval, OpenAI attempt, mock answer, fallback, DB log, JSONL log.
- `backend/app/services/kb_service.py`
  FAQ search, similarity scoring, JSON seed import, CRUD helpers.
- `backend/app/data/seed_faq.json`
  Starter local knowledge base. Replace with real AIU information for production use.

### Frontend

- `frontend/src/pages/KioskPage.jsx`
  Main vertical-screen experience and interaction-mode switching.
- `frontend/src/components/Avatar.jsx`
  Temporary visual avatar with animated rings and facial expression.
- `frontend/src/components/IdleMode.jsx`
  Idle welcome state.
- `frontend/src/components/TriggerMode.jsx`
  Interaction-entry state.
- `frontend/src/components/DialogMode.jsx`
  Text input, mock voice trigger, answer area, recent history, suggestion chips.
- `frontend/src/components/AdminPanel.jsx`
  FAQ CRUD, reload action, usage stats, and question logs.
- `frontend/src/api/client.js`
  Frontend API wrapper for backend endpoints.
- `frontend/src/styles/base.css`
  Kiosk and admin visual system.

## Local run without Docker

### 1. Create environment file

```bash
cd ai-sulu
cp .env.example .env
```

### 2. Start backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app

- Kiosk screen: `http://localhost:3000`
- Admin panel: `http://localhost:3000/admin`
- Backend docs: `http://localhost:8000/docs`

## Docker run

### 1. Prepare env file

```bash
cd ai-sulu
cp .env.example .env
```

### 2. Start containers

```bash
docker compose up --build
```

### 3. Open services

- Frontend: `http://localhost:3000`
- Admin: `http://localhost:3000/admin`
- Backend API: `http://localhost:8000`

## Key API endpoints

- `POST /api/chat/ask`
- `POST /api/chat/transcribe`
- `POST /api/chat/speak`
- `GET /api/knowledge-base/faqs`
- `GET /api/knowledge-base/search?q=...`
- `GET /api/logs/questions`
- `GET /api/logs/stats`
- `GET /api/admin/status`
- `GET /api/admin/faqs`
- `POST /api/admin/faqs`
- `PUT /api/admin/faqs/{faq_id}`
- `DELETE /api/admin/faqs/{faq_id}`
- `POST /api/admin/knowledge-base/reload`

## Mock mode

The project works immediately with:

- local FAQ retrieval from SQLite
- mock voice transcription
- mock TTS response metadata
- safe fallback if the system cannot answer confidently

Default configuration keeps `USE_MOCK_SERVICES=true`.

## How to connect OpenAI

1. Copy `.env.example` to `.env`.
2. Set:

```env
USE_MOCK_SERVICES=false
OPENAI_ENABLED=true
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

3. Restart backend.
4. The backend will try FAQ retrieval first, then use OpenAI with FAQ context in `backend/app/services/llm_service.py`.

## How to connect Whisper

Current file: `backend/app/services/voice_service.py`

1. Set:

```env
USE_MOCK_SERVICES=false
WHISPER_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
```

2. Replace the placeholder branch inside `transcribe_audio()` with the provider call you want to use.
3. Keep the endpoint contract unchanged: `POST /api/chat/transcribe` returns transcript text for the frontend.

## How to connect ElevenLabs or Azure TTS

Current file: `backend/app/services/voice_service.py`

### ElevenLabs

```env
USE_MOCK_SERVICES=false
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Azure TTS

```env
USE_MOCK_SERVICES=false
TTS_PROVIDER=azure
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=your_region
```

Then replace the `synthesize_speech()` placeholder with real provider calls and return an audio URL or audio-stream reference.

## How to connect D-ID, HeyGen, or Unreal avatar

The current avatar is isolated in:

- `frontend/src/components/Avatar.jsx`

To upgrade the avatar:

1. Keep the kiosk page state and API flow unchanged.
2. Replace `Avatar.jsx` with a web player or embedded render surface from D-ID, HeyGen, or Unreal Pixel Streaming.
3. Drive speaking and thinking states using the existing props:
   - `mode`
   - `isSpeaking`
   - `isThinking`

## Production notes

- Replace seed FAQ entries with real university data.
- Add authentication to `/api/admin/*` before public deployment.
- Move SQLite to PostgreSQL for multi-user production use.
- Add real STT/TTS providers and audio pipeline.
- Add observability and structured application logs if the kiosk goes live.
