import torch
import torchaudio.pipelines
from fastapi import FastAPI

# Use GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Fetch pre-trained EMFORMER_RNNT_BASE_LIBRISPEECH model
bundle = torchaudio.pipelines.EMFORMER_RNNT_BASE_LIBRISPEECH

# Move model to device
model = bundle._get_model().to(device)

app = FastAPI()

@app.get("/transcribe")
async def transcribe():
    # Take audio from user

    # Feed the model

    # Return result
    return {"message": "Placeholder"}

