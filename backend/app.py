import torch
import torchaudio.pipelines
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Use GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Fetch pre-trained EMFORMER_RNNT_BASE_LIBRISPEECH model
bundle = torchaudio.pipelines.EMFORMER_RNNT_BASE_LIBRISPEECH

# Move model to device
model = bundle._get_model().to(device)

# Get decoder
decoder = bundle.get_decoder()

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

    # Take audio from frontend
    if data_store.empty():
        return {'data': None}
    
    data = await asyncio.wait_for(data_store.get(), timeout=1)

    # Store data in Tensor
    tensor = torch.tensor(data)
    print(data)

    # Feed the model the Tensor

    # Feed output of model to decoder 

    # Feed output of decoder to token processor

    # Combine result and result

@app.websocket("/api/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await data_store.put(data)
        await transcribe()