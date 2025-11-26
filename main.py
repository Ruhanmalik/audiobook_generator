from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

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

                # Write with spacing between chapters
                f.write(text + "\n\n")

    return {"message": "EPUB extracted successfully", "output": txt_filename}

@app.get("/")
def read_root():
    return {"message": "Hola Clase"}
