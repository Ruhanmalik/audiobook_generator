import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import os
from kokoro import KPipeline
import soundfile as sf
import numpy as np

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

def tts(text ,voice, speed, max_chunk_size):
    #Convert text file to audio using Kokoro TTS
    print("Converting text to audio...")

    pipeline = KPipeline(lang_code='a')
    try:
        # Read the text file
        with open(text, "r", encoding="utf-8") as f:
            text = f.read()

            text_chunks = chunk(text, max_chunk_size)
            print(f"Split into {len(text_chunks)} chunks")
            all_audio_files = []

            for chunk_id, text_chunk in enumerate(text_chunks):
                print(f"Processing chunk {chunk_id + 1} / {len(text_chunks)}")

                try:
                    generator = pipeline(text_chunk, voice=voice, speed=speed)
                    audio_segments = []

                    for i, (gs, ps, audio) in enumerate(generator):
                        audio_segments.append(audio)
                    
                    if audio_segments:
                        combined_audio = np.concatenate(audio_segments)
                        chunk_filename = f'chunk_{chunk_id + 1:04d}.wav'
                        sf.write(chunk_filename, combined_audio, 24000)
                        all_audio_files.append(chunk_filename)

                except Exception as e:
                    print(f"Error in processing chunks: {e}")
                    continue

            if all_audio_files:
                # Combine all chunks into one file using FFmpeg
                print("Combining audio chunks...")
                    
                # Create a file list for FFmpeg
                with open('filelist.txt', 'w') as f:
                    for audio_file in all_audio_files:
                        f.write(f"file '{audio_file}'\n")
                    
                    # Use FFmpeg to concatenate all chunks
                result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c copy audiobook.wav')
                    
                if result == 0:
                    print("Audio succesfully combined into audiobook.wav")  

                    # Clean up temporary files
                    for audio_file in all_audio_files:
                        if os.path.exists(audio_file):
                            os.remove(audio_file)
                    
                    if os.path.exists('filelist.txt'):
                        os.remove('filelist.txt')
                else:
                    print("FFmpeg failed")
            else:
                print("No audio files were generated successfully.")
                    
        
    except Exception as e:
        print(f"Error in TTS conversion: {e}")
        return None


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


def scrape(book):

    with open('output.txt', 'w', encoding='utf-8') as f:

        chapter_count = 0
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if item.get_name() == 'index_split_004.html':
                continue
    
            soup = BeautifulSoup(item.get_content(), 'html.parser')

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ', strip=True)
            cleaned = clean_text(text)

            if cleaned:
                f.write(cleaned)
                chapter_count += 1


def main():
    
    path = r'C:\Users\Ruhan Malik\Desktop\Projects\Python\audiobook_generator\LOTM_vol1.epub'


    if not os.path.exists(path):
        print("EPUB not found")
        return
    book = epub.read_epub(r'C:\Users\Ruhan Malik\Desktop\Projects\Python\audiobook_generator\LOTM_vol1.epub')
    try:
        scrape(book)
    except Exception as e:
        print(f"Error reading EPUB: {e}")        
    if os.path.exists("output.txt"):
        voice = 'af_sarah'
        speed = 1.0
        print(f"Starting TTS conversion with voice: {voice} at speed {speed}.")
        chunk_size = 50000
        tts("output.txt", voice, speed, chunk_size)
    else:
        print("No output.txt file found. Text extraction may have failed.")

main()

