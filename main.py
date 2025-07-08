import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import os
from kokoro import KPipeline
import soundfile as sf

def tts(text):
    """
    Convert text file to audio using Kokoro TTS
    """
        
    print("Converting text to audio...")

    pipeline = KPipeline(lang_code='a')
    try:
        # Read the text file
        with open(text, "r", encoding="utf-8") as f:
            text = f.read()

            generator = pipeline(text, voice=voice, speed=speed)
            audio_segments = []

            for i, (gs, ps, audio) in enumerate(generator):
                audio_segments.append(audio)
                sf.write(f'chunk_{i}.wav', audio, 24000)

            # Combine all chunks into one file using FFmpeg
            print("Combining audio chunks...")
            
            # Create a file list for FFmpeg
            with open('filelist.txt', 'w') as f:
                for i in range(len(audio_segments)):
                    f.write(f"file 'chunk_{i}.wav'\n")
            
            # Use FFmpeg to concatenate all chunks
            os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c copy output_audio.wav')
            
            # Clean up temporary files
            for i in range(len(audio_segments)):
                if os.path.exists(f'chunk_{i}.wav'):
                    os.remove(f'chunk_{i}.wav')
            
            if os.path.exists('filelist.txt'):
                os.remove('filelist.txt')
            
            print("Audio successfully combined into output_audio.wav")
        
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
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if item.get_name == 'index_split_004.html':
                continue
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            cleaned = clean_text(text)
            if cleaned:
                f.write(cleaned)



def main():
    book = epub.read_epub(r'C:\Users\Ruhan Malik\Desktop\Projects\Python\audiobook_generator\LOTM_vol1.epub')

    if not os.path.exists(book):
        print("EPUB not found")
        return
    
    try:
        scrape(book)
    except Exception as e:
        print(f"Error reading EPUB: {e}")        
    if os.path.exists("output.txt"):
        print("Converting text to audio...")
        
        tts("output.txt")
    else:
        print("No output.txt file found. Please run the scraper first.")

main()

'''
def scrape(book):

    chapters = []
    
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content() ,'html.parser')
        content = soup.find_all('body', class_='block_' )

        for c in content:
            raw = c.get_text(separator=' ', string=True)
            clean = clean_text(raw)
            chapters.append(clean)

    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(chapters))
'''