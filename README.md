# 📚🎧 EPUB to Audiobook Generator

Convert any EPUB ebook into a high-quality audiobook using Kokoro TTS with GPU acceleration.

## ✨ Features

- 🚀 **GPU Accelerated** - Utilizes NVIDIA GPUs for fast processing
- 🎭 **Multiple Voices** - Choose from different AI voices
- 📖 **EPUB Support** - Direct conversion from EPUB files
- 🔧 **Smart Chunking** - Handles large books by splitting into manageable chunks
- 🎵 **MP3 Output** - Creates compressed audiobooks (no 4GB WAV limit)
- 🧹 **Auto Cleanup** - Removes temporary files after processing

## 🎯 Results

- **Input**: EPUB file (any size)
- **Output**: High-quality MP3 audiobook
- **Speed**: With RTX 4070, processes ~2.4M characters in ~19 minutes
- **Quality**: Natural-sounding speech with proper punctuation handling

## 📋 Requirements

### System Requirements
- **Windows** (tested), Linux, or macOS
- **NVIDIA GPU** (recommended) with CUDA support
- **FFmpeg** installed and in PATH
- **Python 3.8+**

### Hardware Recommendations
- **GPU**: NVIDIA RTX 3060 or better
- **RAM**: 8GB+ (16GB+ recommended for large books)
- **Storage**: 2-3GB free space per book

## ⚙️ Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd audiobook-generator
```

### 2. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Install PyTorch with CUDA (for GPU acceleration)
```bash
# For CUDA 12.1 (check your CUDA version with: nvidia-smi)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Install FFmpeg
**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html) or winget ffmpeg in terminal
2. Extract and add to PATH
3. Test: `ffmpeg -version`

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 5. Install espeak-ng (for text processing)
**Windows:**
1. Download from [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)
2. Install the `.msi` file

**Linux:**
```bash
sudo apt install espeak-ng
```

**macOS:**
```bash
brew install espeak-ng
```

## 🚀 Usage

### Step-by-Step Guide

#### Step 1: Prepare Your EPUB
1. **Get the full path** of your EPUB file:
   - **Windows**: Right-click the EPUB → "Copy as path"
   - **macOS**: Right-click → "Get Info" → copy the path
   - **Linux**: Use `realpath yourbook.epub`

#### Step 2: Configure the Script
1. **Open `main.py`** in a text editor
2. **Find this line** (around line 131):
   ```python
   path = r'C:\Users\Ruhan Malik\Desktop\Projects\Python\audiobook_generator\LOTM_vol1.epub'
   ```
3. **Replace with your EPUB path**:
   ```python
   path = r'C:\Users\YourName\Documents\your_book.epub'
   ```
   ⚠️ **Keep the `r` before the quotes** - this handles Windows backslashes correctly

#### Step 3: Test and Troubleshoot (Optional)
**Before processing the entire book**, run the troubleshoot script:
```bash
python test.py
```
This will:
- ✅ Check GPU availability
- ✅ Test TTS pipeline
- ✅ Verify FFmpeg installation
- ✅ Test with sample text

#### Step 4: Run the Main Script
```bash
python main.py
```

#### Step 5: Monitor Progress
Watch the console output:
```
GPU detected: NVIDIA GeForce RTX 4070
Extracted 45 chapters
Split into 25 chunks
Processing chunk 1 / 25 - Done in 2.1s (1250 chars/sec)
Processing chunk 2 / 25 - Done in 1.9s (1315 chars/sec)
...
Combining audio chunks...
✅ SUCCESS! Audiobook created as audiobook.mp3
```

### Quick Start (TL;DR)
```bash
# 1. Copy your EPUB path
# 2. Edit path in main.py
# 3. Run
python main.py
```

### Configuration Options
Edit these variables in `main.py`:

```python
# Voice selection
voice = 'af_sarah'    # Options: 'af_sarah', 'af_heart', etc.

# Speech speed
speed = 1.0           # 0.8 = slower, 1.2 = faster

# Chunk size (characters per chunk)
chunk_size = 100000   # Larger = fewer files, more GPU memory usage
```

### Available Voices
- `af_sarah` - Female voice (default)
- `af_heart` - Alternative female voice
- More voices available in Kokoro documentation

## 📁 Output

The script generates:
- `audiobook.mp3` - Your final audiobook
- `output.txt` - Extracted and cleaned text (temporary)
- Progress information in the console

## ⚡ Performance Tips

### GPU Optimization
- **Check GPU usage**: The script will automatically detect and use your GPU
- **Memory management**: Larger chunks use more GPU memory but process faster
- **RTX 4070 users**: Can use chunk sizes up to 150,000 characters

### Speed Expectations
| Hardware | Processing Speed | 2.4M Character Book |
|----------|------------------|---------------------|
| RTX 4070 | ~400+ chars/sec  | ~19 minutes        |
| RTX 3070 | ~300+ chars/sec  | ~25 minutes        |
| CPU only | ~50-100 chars/sec| 2-4 hours          |

## 🔧 Troubleshooting

### Common Issues

**"CUDA not available"**
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

**"FFmpeg not found"**
- Ensure FFmpeg is installed and in your system PATH
- Test: `ffmpeg -version`

**"Text too long" error**
- Reduce chunk_size in the script
- For very large books, try chunk_size = 50000

**"WAV file too large"**
- The script now outputs MP3 by default
- MP3 files have no size limit and are much smaller

**GPU memory errors**
- Reduce chunk_size
- Clear GPU cache: add `torch.cuda.empty_cache()` calls

### Performance Issues
- **Slow processing**: Ensure GPU is being used (check console output)
- **High memory usage**: Reduce chunk_size
- **FFmpeg slow**: Try different audio codecs

## 📖 How It Works

1. **Text Extraction**: Parses EPUB and extracts clean text
2. **Chunking**: Splits large text into GPU-manageable pieces
3. **TTS Generation**: Uses Kokoro TTS to generate audio for each chunk
4. **Audio Combination**: FFmpeg combines all chunks into final MP3
5. **Cleanup**: Removes temporary files

## 🎛️ Customization Guide

### Voice and Speed Settings
**Location**: `main.py`, lines ~140-145

```python
# Voice Options
voice = 'af_sarah'    # Default female voice
voice = 'af_heart'    # Alternative female voice
# More voices: Check Kokoro documentation

# Speed Control
speed = 0.8          # Slower, more deliberate
speed = 1.0          # Normal speed (default)
speed = 1.2          # Faster narration
speed = 1.5          # Very fast (may affect quality)
```

### GPU Memory Optimization
**Location**: `main.py`, line ~143

```python
# Chunk Size (characters per processing chunk)
chunk_size = 50000   # Conservative (4GB+ GPU)
chunk_size = 75000   # Balanced (6GB+ GPU) 
chunk_size = 100000  # Aggressive (8GB+ GPU, like RTX 4070)
chunk_size = 150000  # Maximum (12GB+ GPU, like RTX 4080/4090)
```

### Text Filtering and Cleanup

#### Exclude Specific Chapters/Sections
**Location**: `main.py`, `scrape()` function, lines ~115-120

```python
# Current exclusions
skip_files = ['index_split_004.html']

# Add more exclusions:
skip_files = [
    'index_split_004.html',    # Table of contents
    'index_split_001.html',    # Title page
    'index_split_002.html',    # Copyright page
    'cover.html',              # Cover page
    'acknowledgments.html',    # Acknowledgments
]

# Advanced: Skip by content
def scrape(book):
    # ... existing code ...
    
    # Skip chapters with unwanted content
    if any(skip_word in text.lower() for skip_word in ['bibliography', 'index', 'glossary']):
        print(f"Skipping reference section: {item_name}")
        continue
```

#### Custom Text Cleaning
**Location**: `main.py`, `clean_text()` function, lines ~95-110

```python
def clean_text(text):
    # Basic cleanup
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Handle censored words
    text = re.sub(r'F\s*\*\s*ck', 'Fuck', text)
    text = re.sub(r'S\s*\*\s*it', 'Shit', text)  # Add more
    
    # Custom replacements for your specific books
    text = re.sub(r'\[Author Note:.*?\]', '', text)  # Remove author notes
    text = re.sub(r'\*\*.*?\*\*', '', text)         # Remove bold markdown
    text = re.sub(r'Chapter \d+', '', text)         # Remove chapter headers
    
    # Fix pronunciation issues
    text = re.sub(r'Dr\.', 'Doctor', text)          # "Dr." → "Doctor"
    text = re.sub(r'Mr\.', 'Mister', text)          # "Mr." → "Mister" 
    text = re.sub(r'Mrs\.', 'Missus', text)         # "Mrs." → "Missus"
    text = re.sub(r'vs\.', 'versus', text)          # "vs." → "versus"
    
    # Handle special characters
    text = re.sub(r'[^\w\s.,!?;:()\'"—\-–]', '', text)
    
    return text
```

### Audio Output Settings

#### Different Audio Formats
**Location**: `main.py`, `tts()` function, line ~85

```python
# Current (MP3, 128k bitrate)
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a libmp3lame -b:a 128k -y audiobook.mp3')

# High Quality MP3 (192k bitrate)
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a libmp3lame -b:a 192k -y audiobook.mp3')

# Smaller file size (96k bitrate)
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a libmp3lame -b:a 96k -y audiobook.mp3')

# Lossless FLAC (larger file)
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a flac -y audiobook.flac')

# M4A/AAC (good compatibility)
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a aac -b:a 128k -y audiobook.m4a')
```

#### Add Metadata to Audio File
```python
# Add after the FFmpeg command
metadata_cmd = f'''ffmpeg -i audiobook.mp3 -i cover.jpg \\
    -map 0:0 -map 1:0 -c copy -id3v2_version 3 \\
    -metadata title="Your Book Title" \\
    -metadata artist="Author Name" \\
    -metadata album="Book Series" \\
    -metadata date="2025" \\
    -metadata genre="Audiobook" \\
    audiobook_with_metadata.mp3'''
os.system(metadata_cmd)
```

### Performance Tweaks

#### Batch Processing Multiple Books
**Create a new file**: `batch_process.py`

```python
import os
from main import main

books = [
    r'C:\Books\book1.epub',
    r'C:\Books\book2.epub', 
    r'C:\Books\book3.epub',
]

for i, book_path in enumerate(books):
    print(f"Processing book {i+1}/{len(books)}: {book_path}")
    
    # Update the path in main.py (or modify main() to accept path parameter)
    # Process the book
    # Rename output file
    if os.path.exists('audiobook.mp3'):
        book_name = os.path.basename(book_path).replace('.epub', '')
        os.rename('audiobook.mp3', f'{book_name}_audiobook.mp3')
```

#### CPU-Only Mode (No GPU)
**Location**: `main.py`, `check_gpu()` function

```python
def check_gpu():
    # Force CPU mode (comment out for normal GPU detection)
    # return torch.device('cpu')
    
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"GPU detected: {torch.cuda.get_device_name(0)}")
        return device
    else:
        device = torch.device('cpu')
        print("No GPU detected, using CPU")
        return device
```

### Debugging and Troubleshooting

#### Enable Verbose Logging
**Add at the top of `main.py`**:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add progress tracking
def tts(text, voice, speed, max_chunk_size, device):
    # ... existing code ...
    
    for chunk_id, text_chunk in enumerate(text_chunks):
        print(f"Chunk {chunk_id + 1}: {len(text_chunk)} chars")
        print(f"GPU Memory: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
        # ... rest of processing
```

#### Test Individual Chapters
**Modify `scrape()` to process specific chapters only**:

```python
def scrape(book):
    # Test with just first 3 chapters
    chapter_limit = 3
    chapter_count = 0
    
    with open('output.txt', 'w', encoding='utf-8') as f:
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if chapter_count >= chapter_limit:
                break
            # ... rest of processing
```

### File Management

#### Organize Output Files
```python
# Create organized output structure
import datetime

def organize_output():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    book_name = "your_book_name"  # Extract from EPUB metadata
    
    output_dir = f"output/{book_name}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Move files
    if os.path.exists('audiobook.mp3'):
        os.rename('audiobook.mp3', f'{output_dir}/audiobook.mp3')
    if os.path.exists('output.txt'):
        os.rename('output.txt', f'{output_dir}/extracted_text.txt')
```

## 📄 License

This project uses:
- **Kokoro TTS**: Apache 2.0 License
- **Other dependencies**: Various open-source licenses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 📞 Support

For issues:
1. Check the troubleshooting section
2. Ensure all dependencies are installed
3. Verify GPU/CUDA setup
4. Check FFmpeg installation

## 🙏 Acknowledgments

- **Kokoro TTS** team for the excellent TTS model
- **PyTorch** for GPU acceleration framework
- **FFmpeg** for audio processing
- **ebooklib** for EPUB parsing

---

**Happy audiobook generation!** 🎧📚