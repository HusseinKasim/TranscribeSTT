import torch
import torchaudio.pipelines
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Use GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Fetch pre-trained WAV2VEC2_ASR_BASE_960H model
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model()

# Get labels
labels = bundle.get_labels()

app = FastAPI()

# Temp for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins = "http://127.0.0.1:8000/",
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

data_store = asyncio.Queue()

@app.get("/transcribe")
async def transcribe():
    # Receive audio from frontend
    if data_store.empty():
        return {'data': None}
    
    data = await asyncio.wait_for(data_store.get(), timeout=1)

    # ADD BUFFER TO TAKE UP TO 14400 CHUNKS (which will then be converted to 4800 chunks after resampling to 16kHZ)

    # Store audio values (PCM) in list
    data_list = list(data['msg'].values())

    # Fetch input sample rate
    input_sample_rate = data['sample_rate']

    # Store data in tensor
    data_tensor = torch.tensor(data_list)

    # Prepare tensor for resampling (update shape [128] -> [1, 128])
    if data_tensor.dim() == 1:
        data_tensor = data_tensor.unsqueeze(0)
    
    # Resample data from 48kHz to 16kHz
    resampler = torchaudio.transforms.Resample(orig_freq=input_sample_rate, new_freq=bundle.sample_rate)
    data_tensor = resampler(data_tensor.float())
    
    # Pass data into model
    emissions, _ = model(data_tensor)

    # Feed output of decoder to token processor
    tokens = torch.argmax(emissions, dim=-1)

    # Build transcription
    transcript = "".join([labels[i] for i in tokens[0]])

    # Print result
    print(transcript.strip())

@app.websocket("/api/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await data_store.put(data)
        await transcribe()