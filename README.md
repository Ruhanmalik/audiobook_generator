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

### Basic Usage
1. Place your EPUB file in the project directory
2. Edit the `path` variable in `main.py`:
   ```python
   path = r'your_book.epub'
   ```
3. Run the script:
   ```bash
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

## 🎛️ Advanced Configuration

### Custom Text Cleaning
Modify the `clean_text()` function to handle specific formatting issues in your books.

### Different Output Formats
Change the FFmpeg command in `tts()` function:
```python
# For different quality MP3
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a libmp3lame -b:a 192k audiobook.mp3')

# For FLAC (lossless)
result = os.system('ffmpeg -f concat -safe 0 -i filelist.txt -c:a flac audiobook.flac')
```

### Batch Processing Multiple Books
Create a loop around the main processing logic to handle multiple EPUB files.

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