import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def scrape(book):

    chapters = []

    with open('output.txt', 'w', encoding='utf-8') as f:
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                f.write(f"NAME: , {item.get_name()}")
                f.write(item.get_content().decode('utf-8'))

book = epub.read_epub(r'C:\Users\Ruhan Malik\Desktop\Projects\Python\audiobook_generator\venv\LOTM_vol1.epub')
scrape(book)