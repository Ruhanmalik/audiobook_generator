from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import re
import soundfile as sf
import numpy as np
import torch
import torch.version
from kokoro import KPipeline

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

def tts_from_text(text_content, output_filename, voice, speed, max_chunk_size, device):
    """Convert text content to audio using Kokoro TTS"""
    print("Converting text to audio...")

    pipeline = KPipeline(lang_code='a', device=device)
    try:
        text_chunks = chunk(text_content, max_chunk_size)
        print(f"Split into {len(text_chunks)} chunks")
        all_audio_files = []

        for chunk_id, text_chunk in enumerate(text_chunks):
            print(f"Processing chunk {chunk_id + 1} / {len(text_chunks)}")

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
                
                return True
            else:
                print("FFmpeg failed")
                return False
        else:
            print("No audio files were generated successfully.")
            return False
                
    except Exception as e:
        print(f"Error in TTS conversion: {e}")
        return False

@app.post("/convert")
async def convert_text(request: ConvertRequest):
    """Convert the edited text to audiobook"""
    device = check_gpu()
    
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
        
        # Convert text to audio
        success = tts_from_text(text_content, output_filename, voice, speed, chunk_size, device)
        
        if success:
            return {
                "message": "Text converted successfully", 
                "output": output_filename,
                "path": f"output/{output_filename}"
            }
        else:
            raise HTTPException(status_code=500, detail="Audio conversion failed")
            
    except Exception as e:
        print(f"Error in convert endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))