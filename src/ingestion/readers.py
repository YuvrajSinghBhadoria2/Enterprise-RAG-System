from pathlib import Path
from typing import List, Dict

class DocumentReader:
    def read(self, file_path: Path) -> str:
        raise NotImplementedError

class TextReader(DocumentReader):
    def read(self, file_path: Path) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

def get_reader(file_path: Path) -> DocumentReader:
    ext = file_path.suffix.lower()
    if ext in ['.txt', '.md']:
        return TextReader()
    # Add PDF/Docx support here later
    raise ValueError(f"Unsupported file type: {ext}")
