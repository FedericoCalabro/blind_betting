from PyPDF2 import PdfReader
from downloader import DOWNLOAD_PATH

class PalinsestoPdfReader:
    def __init__(self):
        reader = PdfReader(DOWNLOAD_PATH)
        self.data = [] 
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            lines = text.split("\n")
            lines = lines[9:-1]
            self.data.extend(lines)