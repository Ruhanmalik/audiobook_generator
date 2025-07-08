import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re


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




book = epub.read_epub(r'C:\Users\Ruhan Malik\Desktop\Projects\Python\audiobook_generator\LOTM_vol1.epub')
scrape(book)

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