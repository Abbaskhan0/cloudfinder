class BaseExtractor:
    def extract(self, file_path):
        raise NotImplementedError("Extractor must implement `extract()`")

import pytesseract
from PIL import Image
# from .base_extractor import BaseExtractor

import csv
# from extractor import BaseExtractor


class TxtExtractor(BaseExtractor):
    def extract(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

class PngExtractor(BaseExtractor):
    def extract(self, file_path):
        return pytesseract.image_to_string(Image.open(file_path))



class CsvExtractor(BaseExtractor):
    def extract(self, file_path):
        content = []
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                content.append(" ".join(row))
        return "\n".join(content)


from PyPDF2 import PdfReader
# from .base_extractor import BaseExtractor

class PdfExtractor(BaseExtractor):
    def extract(self, file_path):
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
