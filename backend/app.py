import torch
import torchaudio.pipelines
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Fetch pre-trained WAV2VEC2_ASR_BASE_960H model
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model()
labels = bundle.get_labels()

# Constants
SILENCE_THRESHOLD = 0.005
BUFFER_SECONDS = 4
MODEL_SAMPLE_RATE = bundle.sample_rate

app = FastAPI()

# Temp for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

# Data queue
data_store = asyncio.Queue()

# Websocket endpoint
@app.websocket("/ws/transcription")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    buffer = []

    # Initialize decoder
    decoder = GreedyCTCDecoder(labels)

    while True:
        data = await websocket.receive_json()
        
        # Store audio values (PCM) in list
        data_list = list(data['msg'].values())

        # Fetch input sample rate
        input_sample_rate = data['sample_rate']

        # Max chunks of buffer 
        max_chunks = int(input_sample_rate * BUFFER_SECONDS)
        
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
            data_tensor = torchaudio.functional.resample(data_tensor, input_sample_rate, MODEL_SAMPLE_RATE)

            # Check for silence
            if torch.sqrt(torch.mean(data_tensor ** 2)) < SILENCE_THRESHOLD:
                await websocket.send_json({'message': ''})
                continue
            
            # Pass data into model  
            with torch.inference_mode():
                emissions, _ = model(data_tensor)

            # Build transcription
            transcript = decoder(emissions[0])

            buffer.clear()
            await websocket.send_json({'message': transcript})
        else:
            await websocket.send_json({'message': ''})


# Health check endpoint
@app.get("/api/health")
def health_check():
    return {'status': 'ok'}


# Model info endpoint
@app.get("/api/model")
def model_info():
    return {
        'model': 'WAV2VEC2_ASR_BASE_960H',
        'sample_rate': MODEL_SAMPLE_RATE,
        'labels': labels
            }


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