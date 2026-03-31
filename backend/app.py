import torch
import torchaudio.pipelines
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Fetch pre-trained WAV2VEC2_ASR_BASE_960H model
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model()

# Get labels
labels = bundle.get_labels()

app = FastAPI()
buffer = []

# Temp for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

data_store = asyncio.Queue()

@app.get("/transcribe")
async def transcribe():
    global buffer

    # Receive audio from frontend
    if data_store.empty():
        return {'message': '""'}
    
    data = await asyncio.wait_for(data_store.get(), timeout=1)

    # Store audio values (PCM) in list
    data_list = list(data['msg'].values())

    # Fetch input sample rate
    input_sample_rate = data['sample_rate']

    # Max chunks of buffer 
    max_chunks = int(input_sample_rate * 4)
    
    # Fill buffer
    for sample in data_list:
        buffer.append(sample)

    # Limit buffer to max
    if len(buffer) > max_chunks:
        buffer = buffer[-max_chunks:]
     
    if len(buffer) == max_chunks:
        # Store data in tensor and convert to float
        data_tensor = torch.tensor(buffer, dtype=torch.float32)
        
        # Prepare tensor for resampling (update shape E.g. [128] -> [1, 128])
        if data_tensor.dim() == 1:
            data_tensor = data_tensor.unsqueeze(0)

        # Resample data from 48kHz to 16kHz
        data_tensor = torchaudio.functional.resample(data_tensor, input_sample_rate, bundle.sample_rate)

        # Check for silence
        if torch.sqrt(torch.mean(data_tensor ** 2)) < 0.005:
            return {'message': ''}
        
        # Pass data into model  
        with torch.inference_mode():
            emissions, _ = model(data_tensor)

        # Feed output of decoder to token processor
        decoder = GreedyCTCDecoder(labels)

        # Build transcription
        transcript = decoder(emissions[0])

        buffer.clear()

        return {'message': transcript}
    
    return {'message': ''}


@app.websocket("/api/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await data_store.put(data)
        response = await transcribe()
        await websocket.send_json(response)


class GreedyCTCDecoder(torch.nn.Module):
    def __init__(self, labels, blank=0):
        super().__init__()
        self.labels = labels
        self.blank = blank

    def forward(self, emission: torch.Tensor) -> str:
        indices = torch.argmax(emission, dim=-1) 
        indices = torch.unique_consecutive(indices, dim=-1)
        indices = [i for i in indices if i != self.blank]
        return "".join([self.labels[i] for i in indices])