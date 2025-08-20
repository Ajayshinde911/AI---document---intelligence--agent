# reader.py - OCR helpers
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# If you installed Tesseract in default Windows path, set this:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(path: str) -> str:
    """Convert PDF pages to images and run OCR on each page."""
    text = ""
    pages = convert_from_path(path)
    for page in pages:
        text += pytesseract.image_to_string(page)
        text += "\n"
    return text

def extract_text_from_image(path: str) -> str:
    """Run OCR on an image and return extracted text."""
    img = Image.open(path)
    return pytesseract.image_to_string(img)
