from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import soundfile as sf
import numpy as np
import torch
import torch.version
from kokoro import KPipeline
import uuid
import threading
from typing import Dict

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'

app = FastAPI()

# Store progress for each conversion task
conversion_progress: Dict[str, dict] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add this model for the convert endpoint
class ConvertRequest(BaseModel):
    text: str
    filename: str

def clean_text(text):
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    # Replace censored words (e.g., "F * ck" -> "Fuck")
    text = re.sub(r'F\s*\*\s*ck', 'Fuck', text)
    # Remove or replace special characters that might disrupt TTS
    text = re.sub(r'[^\w\s.,!?]', '', text)
    # Normalize punctuation spacing (e.g., "Pain!So" -> "Pain! So")
    text = re.sub(r'([!?.])(\w)', r'\1 \2', text)  # Capture word character in group 2
    return text

@app.post("/extract")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    print(f"Received file: {file.filename}, size: {len(contents)} bytes")
    if not file.filename.endswith('.epub'):
        raise HTTPException(status_code=400, detail="Only EPUB files are supported")
    
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    epub_path = f"uploads/{file.filename}"
    with open(epub_path, "wb") as f:
        f.write(contents)

    # Load EPUB
    book = epub.read_epub(epub_path)
    
    # Output text file
    txt_filename = file.filename.replace(".epub", ".txt")
    txt_path = f"output/{txt_filename}"

    extracted_sections = []

    with open(txt_path, 'w', encoding='utf-8') as f:
        
        # Loop through spine for TRUE reading order
        for item_id, _ in book.spine:
            item = book.get_item_with_id(item_id)

            # Only process document (HTML/XHTML) items
            if item.get_type() == ebooklib.ITEM_DOCUMENT:

                soup = BeautifulSoup(item.get_content(), 'html.parser')

                # Remove unwanted script/style tags
                for tag in soup(["script", "style"]):
                    tag.decompose()

                # Clean text
                text = soup.get_text(separator=' ', strip=True)

                cleaned = clean_text(text)
                extracted_sections.append(cleaned)
                # Write with spacing between chapters
                f.write(cleaned + "\n\n")

    full_text = "\n\n".join(extracted_sections)

    return {"message": "EPUB extracted successfully", "output": txt_filename, "text": full_text}

def check_gpu():
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"GPU detected: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
        return device
    else:
        device = torch.device('cpu')
        print("No GPU detected, using CPU")
        return device

def chunk(text, max_length):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks =  []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_length and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
            
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def tts_from_text(text_content, output_filename, voice, speed, max_chunk_size, device, task_id: str):
    """Convert text content to audio using Kokoro TTS"""
    print("Converting text to audio...")
    
    # Initialize progress
    conversion_progress[task_id] = {
        "status": "processing",
        "progress": 0,
        "current_chunk": 0,
        "total_chunks": 0,
        "message": "Initializing...",
        "output_file": None,
        "error": None
    }

    pipeline = KPipeline(lang_code='a', device=device)
    try:
        text_chunks = chunk(text_content, max_chunk_size)
        total_chunks = len(text_chunks)
        conversion_progress[task_id]["total_chunks"] = total_chunks
        conversion_progress[task_id]["message"] = f"Processing {total_chunks} chunks..."
        print(f"Split into {total_chunks} chunks")
        all_audio_files = []

        for chunk_id, text_chunk in enumerate(text_chunks):
            conversion_progress[task_id]["current_chunk"] = chunk_id + 1
            progress = int(((chunk_id + 1) / total_chunks) * 90)  # Reserve 10% for combining
            conversion_progress[task_id]["progress"] = progress
            conversion_progress[task_id]["message"] = f"Processing chunk {chunk_id + 1} of {total_chunks}..."
            print(f"Processing chunk {chunk_id + 1} / {total_chunks}")

            try:
                if device.type == 'cuda':
                    with torch.cuda.amp.autocast():
                        generator = pipeline(text_chunk, voice=voice, speed=speed)
                        audio_segments = []
                else:
                    generator = pipeline(text_chunk, voice=voice, speed=speed)
                    audio_segments = []

                for i, (gs, ps, audio) in enumerate(generator):
                    audio_segments.append(audio)
                
                if audio_segments:
                    combined_audio = np.concatenate(audio_segments)
                    chunk_filename = f'output/chunk_{chunk_id + 1:04d}.wav'
                    sf.write(chunk_filename, combined_audio, 24000)
                    all_audio_files.append(chunk_filename)

                    if device.type == 'cuda' and chunk_id % 10 == 0:
                        torch.cuda.empty_cache()

            except Exception as e:
                print(f"Error in processing chunks: {e}")
                continue

        if all_audio_files:
            # Combine all chunks into one file using FFmpeg
            conversion_progress[task_id]["progress"] = 95
            conversion_progress[task_id]["message"] = "Combining audio chunks..."
            print("Combining audio chunks...")
                
            # Create a file list for FFmpeg
            with open('output/filelist.txt', 'w') as f:
                for audio_file in all_audio_files:
                    f.write(f"file '{os.path.basename(audio_file)}'\n")
                
            # Use FFmpeg to concatenate all chunks
            output_path = f'output/{output_filename}'
            result = os.system(f'ffmpeg -f concat -safe 0 -i output/filelist.txt -c:a libmp3lame -b:a 128k -y {output_path}')
                
            if result == 0:
                print(f"Audio successfully combined into {output_path}")  

                # Clean up temporary files
                for audio_file in all_audio_files:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                
                if os.path.exists('output/filelist.txt'):
                    os.remove('output/filelist.txt')
                
                conversion_progress[task_id]["status"] = "completed"
                conversion_progress[task_id]["progress"] = 100
                conversion_progress[task_id]["message"] = "Conversion complete!"
                conversion_progress[task_id]["output_file"] = output_filename
                return True
            else:
                print("FFmpeg failed")
                conversion_progress[task_id]["status"] = "failed"
                conversion_progress[task_id]["error"] = "FFmpeg failed to combine audio files"
                return False
        else:
            print("No audio files were generated successfully.")
            conversion_progress[task_id]["status"] = "failed"
            conversion_progress[task_id]["error"] = "No audio files were generated"
            return False
                
    except Exception as e:
        print(f"Error in TTS conversion: {e}")
        conversion_progress[task_id]["status"] = "failed"
        conversion_progress[task_id]["error"] = str(e)
        return False

@app.post("/convert")
async def convert_text(request: ConvertRequest, background_tasks: BackgroundTasks):
    """Convert the edited text to audiobook"""
    device = check_gpu()
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    try:
        # Use the text directly from the request
        text_content = request.text
        
        # Generate output filename
        base_filename = request.filename.replace(".epub", "").replace(".txt", "")
        output_filename = f"{base_filename}_audiobook.mp3"
        
        # TTS settings
        voice = 'af_sarah'
        speed = 1.0
        print(f"Starting TTS conversion with voice: {voice} at speed {speed}.")
        chunk_size = 100000 if device.type == 'cuda' else 50000
        
        # Run conversion in background thread
        def run_conversion():
            tts_from_text(text_content, output_filename, voice, speed, chunk_size, device, task_id)
        
        thread = threading.Thread(target=run_conversion)
        thread.start()
        
        return {
            "message": "Conversion started",
            "task_id": task_id
        }
            
    except Exception as e:
        print(f"Error in convert endpoint: {e}")
        conversion_progress[task_id] = {
            "status": "failed",
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """Get the progress of a conversion task"""
    if task_id not in conversion_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return conversion_progress[task_id]

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download the generated audio file"""
    file_path = f"output/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )