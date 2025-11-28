# 📚🎧 EPUB to Audiobook Generator

A modern desktop application that converts EPUB ebooks into high-quality audiobooks using Kokoro TTS with GPU acceleration. Features a beautiful Electron-based UI with real-time progress tracking.

## ✨ Features

- 🚀 **GPU Accelerated** - Utilizes NVIDIA GPUs for fast processing
- 🎨 **Modern Desktop UI** - Beautiful Electron app with React frontend
- 📖 **EPUB Support** - Direct upload and conversion from EPUB files
- ✏️ **Text Editing** - Review and edit extracted text before conversion
- 📊 **Real-Time Progress** - Track conversion progress with live updates
- 🔧 **Smart Chunking** - Handles large books by splitting into manageable chunks
- 🎵 **MP3 Output** - Creates compressed audiobook files
- 📥 **File Management** - Download audio files or open file location
- 🧹 **Auto Cleanup** - Removes temporary files after processing

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - Handles EPUB extraction and TTS conversion
- **Frontend**: Electron + React - Modern desktop application
- **TTS Engine**: Kokoro TTS with PyTorch
- **Audio Processing**: FFmpeg for audio combination

## 📋 Requirements

### System Requirements

- **Windows** (tested), Linux, or macOS
- **NVIDIA GPU** (recommended) with CUDA support
- **FFmpeg** installed and in PATH
- **Python 3.8+**
- **Node.js 16+** (for Electron frontend)

### Hardware Recommendations

- **GPU**: NVIDIA RTX 3060 or better
- **RAM**: 8GB+ (16GB+ recommended for large books)
- **Storage**: 2-3GB free space per book

## ⚙️ Installation

### 1. Clone or Download

```bash
git clone <repository-url>
cd audiobook_generator
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

#### Install PyTorch with CUDA (for GPU acceleration)

```bash
# For CUDA 12.1 (check your CUDA version with: nvidia-smi)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Install FFmpeg

**Windows:**

1. Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install ffmpeg`
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

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## 🚀 Usage

### Starting the Application

#### Step 1: Start the Backend Server

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

#### Step 2: Start the Electron Frontend

```bash
cd frontend
npm start
```

### Using the Application

#### Step 1: Upload EPUB File

1. Click "Choose EPUB File" to select your EPUB book
2. Click "Extract Text" to extract and process the text content
3. The extracted text will be saved to the `output/` folder

#### Step 2: Review and Edit Text

1. Review the extracted text in the text editor
2. Make any edits or corrections as needed
3. Optionally download the `.txt` file
4. Click "Continue to Convert" when ready

#### Step 3: Convert to Audiobook

1. Watch the real-time progress bar as your audiobook is generated
2. Progress updates show:
   - Current chunk being processed
   - Overall completion percentage
   - Status messages
3. When complete, you can:
   - **Download Audio**: Download the MP3 file directly
   - **Open File Location**: Open the file in your system file manager
   - **Convert Another File**: Start a new conversion

## 📁 Project Structure

```
audiobook_generator/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── frontend/               # Electron frontend
│   ├── src/
│   │   ├── main.js        # Electron main process
│   │   ├── preload.js     # Preload script (IPC)
│   │   ├── renderer.jsx   # React entry point
│   │   ├── pages/
│   │   │   └── Home.jsx   # Main application page
│   │   ├── components/    # React components
│   │   └── css/           # Stylesheets
│   └── package.json       # Node.js dependencies
├── uploads/               # Temporary EPUB storage
└── output/               # Generated files (txt, mp3)
```

## 🔌 API Endpoints

### POST `/extract`

Upload and extract text from an EPUB file.

**Request:**

- `file`: EPUB file (multipart/form-data)

**Response:**

```json
{
  "message": "EPUB extracted successfully",
  "output": "book_name.txt",
  "text": "Full extracted text content..."
}
```

### POST `/convert`

Convert text to audiobook.

**Request:**

```json
{
  "text": "Text content to convert...",
  "filename": "book_name.epub"
}
```

**Response:**

```json
{
  "message": "Conversion started",
  "task_id": "uuid-here"
}
```

### GET `/progress/{task_id}`

Get conversion progress.

**Response:**

```json
{
  "status": "processing",
  "progress": 45,
  "current_chunk": 10,
  "total_chunks": 25,
  "message": "Processing chunk 10 of 25...",
  "output_file": null
}
```

### GET `/download/{filename}`

Download the generated audio file.

## ⚡ Performance Tips

### GPU Optimization

- The application automatically detects and uses your GPU
- Larger chunks use more GPU memory but process faster
- RTX 4070 users: Can process chunk sizes up to 150,000 characters

### Speed Expectations

| Hardware | Processing Speed  | 2.4M Character Book |
| -------- | ----------------- | ------------------- |
| RTX 4070 | ~400+ chars/sec   | ~19 minutes         |
| RTX 3070 | ~300+ chars/sec   | ~25 minutes         |
| CPU only | ~50-100 chars/sec | 2-4 hours           |

## 🔧 Configuration

### Backend Configuration

Edit `main.py` to customize:

```python
# Voice selection (line ~213)
voice = 'af_sarah'    # Options: 'af_sarah', 'af_heart', etc.

# Speech speed (line ~214)
speed = 1.0           # 0.8 = slower, 1.2 = faster

# Chunk size (line ~216)
chunk_size = 100000   # Larger = fewer files, more GPU memory usage
```

### Frontend Configuration

Edit `frontend/src/pages/Home.jsx` to change the backend URL:

```javascript
const CONST_BASE_URL = "http://localhost:8000";
```

## 🐛 Troubleshooting

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

**Backend connection errors**

- Ensure the FastAPI server is running on port 8000
- Check that CORS is properly configured
- Verify the backend URL in the frontend matches your server

**Progress bar not updating**

- Check browser console for errors
- Verify the task_id is being received from the convert endpoint
- Ensure the polling interval is working (check Network tab)

**File download not working**

- Check that the file exists in the `output/` folder
- Verify file permissions
- Check Electron IPC handlers are properly set up

### Performance Issues

- **Slow processing**: Ensure GPU is being used (check backend console output)
- **High memory usage**: Reduce chunk_size in main.py
- **Frontend lag**: Close DevTools if open, reduce polling frequency

## 📖 How It Works

1. **Text Extraction**:

   - User uploads EPUB file via the frontend
   - Backend parses EPUB and extracts clean text
   - Text is cleaned and formatted
   - Extracted text is returned to frontend and saved to `output/` folder

2. **Text Review**:

   - User can review and edit the extracted text
   - Edits are stored in memory (not saved to file)
   - User can download the original extracted text

3. **TTS Conversion**:

   - User submits text for conversion
   - Backend creates a unique task ID
   - Text is split into GPU-manageable chunks
   - Each chunk is processed with Kokoro TTS
   - Progress is tracked and updated in real-time

4. **Audio Combination**:

   - Individual audio chunks are combined using FFmpeg
   - Final MP3 file is created in `output/` folder
   - Temporary files are cleaned up

5. **File Access**:
   - User can download the MP3 file directly
   - Or open the file location in system file manager (Electron only)

## 🎛️ Customization

### Voice and Speed Settings

Edit `main.py` around line 213:

```python
# Voice Options
voice = 'af_sarah'    # Default female voice
voice = 'af_heart'    # Alternative female voice

# Speed Control
speed = 0.8          # Slower, more deliberate
speed = 1.0          # Normal speed (default)
speed = 1.2          # Faster narration
```

### GPU Memory Optimization

Edit `main.py` around line 216:

```python
# Chunk Size (characters per processing chunk)
chunk_size = 50000   # Conservative (4GB+ GPU)
chunk_size = 100000  # Balanced (8GB+ GPU, like RTX 4070)
chunk_size = 150000  # Maximum (12GB+ GPU, like RTX 4080/4090)
```

### Text Cleaning

Edit the `clean_text()` function in `main.py`:

```python
def clean_text(text):
    # Basic cleanup
    text = re.sub(r'\s+', ' ', text.strip())

    # Handle censored words
    text = re.sub(r'F\s*\*\s*ck', 'Fuck', text)

    # Custom replacements
    text = re.sub(r'Dr\.', 'Doctor', text)
    text = re.sub(r'Mr\.', 'Mister', text)

    return text
```

## 📄 License

This project uses:

- **Kokoro TTS**: Apache 2.0 License
- **FastAPI**: MIT License
- **Electron**: MIT License
- **React**: MIT License
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
5. Review browser/Electron console for errors

## 🙏 Acknowledgments

- **Kokoro TTS** team for the excellent TTS model
- **PyTorch** for GPU acceleration framework
- **FastAPI** for the modern Python web framework
- **Electron** for cross-platform desktop app framework
- **FFmpeg** for audio processing
- **ebooklib** for EPUB parsing

---

**Happy audiobook generation!** 🎧📚
