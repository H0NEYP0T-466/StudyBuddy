import os
import re
from typing import Union
from pathlib import Path
import aiofiles
from PyPDF2 import PdfReader
from pypdf import PdfReader as PyPdfReader
from docx import Document
from PIL import Image
import io


async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        try:
            # Fallback to pypdf
            reader = PyPdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e2:
            print(f"Fallback PDF extraction failed: {e2}")
            return ""


async def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""


async def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            text = await f.read()
        return text.strip()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""


async def extract_text_from_md(file_path: str) -> str:
    """Extract text from Markdown file."""
    return await extract_text_from_txt(file_path)


async def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats."""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return await extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return await extract_text_from_docx(file_path)
    elif ext == '.txt':
        return await extract_text_from_txt(file_path)
    elif ext in ['.md', '.markdown']:
        return await extract_text_from_md(file_path)
    else:
        return ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into chunks with overlap."""
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def clean_filename(filename: str) -> str:
    """Clean filename for safe storage."""
    # Remove special characters
    cleaned = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.lower()
