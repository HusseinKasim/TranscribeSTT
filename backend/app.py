import torch
import torchaudio.pipelines
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Use GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Fetch pre-trained EMFORMER_RNNT_BASE_LIBRISPEECH model
bundle = torchaudio.pipelines.EMFORMER_RNNT_BASE_LIBRISPEECH

# Move model to device
model = bundle._get_model().to(device)

app = FastAPI()

# Temp for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins = "http://127.0.0.1:8000/",
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/transcribe")
async def transcribe():
   # Take audio from frontend

    # Resample audio from 48kHz to 16kHz

    # Feed the model

    # Return result
    return {"message": "Placeholder"}

@app.websocket("/api/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        print(data)