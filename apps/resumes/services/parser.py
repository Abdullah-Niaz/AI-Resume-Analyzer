from pathlib import Path
from docx import Document
from pypdf import PdfReader

def extract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        reader = PdfReader(str(path))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    if suffix == '.docx':
        doc = Document(str(path))
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError('Unsupported file type')

def clean_text(text: str) -> str:
    lines = [' '.join(line.split()) for line in text.splitlines()]
    return '\n'.join(line for line in lines if line).strip()
