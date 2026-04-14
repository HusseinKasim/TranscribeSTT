# TranscribeSTT
A real-time speech-to-text transcription application built with FastAPI, WebSockets, PyTorch, and Docker.
The frontend of this website streams audio (captured by a microphone) to the backend, which processes it using the pre-trained **WAV2VEC2_ASR_BASE_960H** PyTorch model and returns live transcription results (as text).

-----

## Tech Stack
  - Frontend: HTML, CSS, JavaScript
  - Backend: FastAPI
  - Real-Time Communication: WebSockets
  - Machine Learning: PyTorch / Torchaudio
  - Containerization: Docker (+ Docker Compose)

-----

## How to Run
### Frontend

```bash
python -m http.server 8000
```

### Backend
#### Option 1: Docker Compose (Recommended)
```bash
docker compose up --build
```
This option will run the backend at:
`http://localhost:8003`

This option will also run the Websocket at:
`ws://localhost:8003/ws/transcription`

#### Option 2: Run Backend Manually
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8003
```

-----

## API Endpoints

### REST API
  - `GET /api/health` -> checks if server is running
  - `GET /api/model` -> returns information about the **WAV2VEC2_ASR_BASE_960H** model

### WebSocket
  - `ws://localhost:8003/ws/transcription` -> real-time audio transcription streaming

-----

## Features
- Real-time WebSocket streaming from microphone
- Live speech-to-text transcription processing
- PyTorch-based **WAV2VEC2_ASR_BASE_960H** model
- REST API for health checks and model information
- Docker containerization support
