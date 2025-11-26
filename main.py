from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import torch
import torch.version
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    print(f"Received file: {file.filename}, size: {len(contents)} bytes")
    if not file.filename.endswith('.epub'):
        raise HTTPException(status_code=400, detail="Only EPUB files are supported")
    with open("temp.txt", "wb") as f:
        content = await file.read()
        f.write(content)
    return {"message": "File uploaded successfully"}

@app.get("/")
def read_root():
    return {"message": "Hola Clase"}
    


