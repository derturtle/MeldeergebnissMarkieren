import os
from Class_Clubs import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

from PyPDF2 import PdfReader, PdfWriter, PageObject

MYVALUES: list = [
    'Anzahl Meldungen',
    'Gesamtzahl der Meldungen'
    'Kampfgericht Abschnitt 1'
    'Abschnitt 1 - '
    'Kampfgericht Abschnitt 1'
    'Wettkampffolge für Abschnitt 1'
]


class PDFText:
    def __init__(self, text_container: LTTextContainer, page_no: int):
        self.text_container = text_container
        self.page_no = page_no
    
    def __str__(self):
        return self.text
    
    @property
    def text(self) -> str:
        return self.text_container.get_text().strip()
    
    @property
    def bbox(self) -> tuple:
        return self.text_container.bbox
    
    @property
    def x(self) -> float:
        return self.bbox[0]
    
    @property
    def y(self) -> float:
        return self.bbox[1]
    
    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]
    
    @property
    def hight(self) -> float:
        return self.bbox[3] - self.bbox[1]
    
class PDFFile:
    _pdf_file: str
    _pdf_texts: list[PDFText]
    
    clubs : list[Club] = []
    
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        pass
    
    @property
    def pdf_file(self) -> str:
        return  self._pdf_file
    
    @pdf_file.setter
    def pdf_file(self, value: str):
        if os.path.exists(value):
            self._pdf_file = os.path.abspath(value)
        else:
            raise ValueError
        
    def read(self):
        self._pdf_texts = []
        
        reader = PdfReader(self._pdf_file)
        # Loop through each page in the PDF
        for page_number, page_layout in enumerate(extract_pages(self._pdf_file), start=0):
            # Get the current page from the PDF
            page = reader.pages[page_number]
            
            # Process each element in the layout of the page
            for element in page_layout:
                if isinstance(element, LTTextContainer):  # Check if the element is a text container
                    for text_line in element:
                        self._pdf_texts.append(PDFText(text_line, page_number))
                        
    def get_clubs(self) -> int:
        match: str = ''
        cnt = 0
        end = -1
        # loop until CONST_01 found
        while end < len(self._pdf_texts):
            end += 1
            if self._pdf_texts[end].text == 'Anzahl Meldungen':
                break
        # analyse clubs
        # 1. Check match value
        while end < len(self._pdf_texts):
            end += 1
            # Check exit condition
            if self._pdf_texts[end].text == 'Gesamtzahl der Meldungen':
                break
            # Check what appears first
            if self._pdf_texts[end].text == 'Nr.' or self._pdf_texts[end].text == 'Verein':
                match = self._pdf_texts[end].text
                end -= 1
                break
        # 2. Get all
        while end < len(self._pdf_texts):
            end += 1
            # Check exit condition
            if self._pdf_texts[end].text == 'Gesamtzahl der Meldungen':
                break
            # Check for match to get Association
            if self._pdf_texts[end].text == match:
                if not self._pdf_texts[end-1].text.startswith('noch '):
                    association = Association.from_string(self._pdf_texts[end-1].text)
            # Check for match "Verein" for sub because
            if self._pdf_texts[end].text == 'Verein':
                end += 1
                pos_dict : dict = {}
                while self._pdf_texts[end].text != 'Gesamt für den Verband' and self._pdf_texts[end].text != 'Land' and self._pdf_texts[end].text != 'DSV-Id':
                    pos_dict[int(self._pdf_texts[end].y)] = [self._pdf_texts[end]]
                    end += 1
                while self._pdf_texts[end].text != match and self._pdf_texts[end-1].page_no == self._pdf_texts[end].page_no:
                    end += 1
                    if int(self._pdf_texts[end].y) in pos_dict.keys():
                        pos_dict[int(self._pdf_texts[end].y)].append(self._pdf_texts[end])
                
                # work over clubs
                for value in pos_dict.values():
                    club = Club(value[0].text, value[1].text)
                    # Add occurrence
                    club.occurrence.append(value[0])
                    # Add association
                    club.association = association
                    # Create participants
                    tmp = []
                    for part in value[2].text.split('/'):
                        tmp.append(int(part.strip()))
                    club.participants = Participants(tmp)
                    # Add segments
                    for i in range(3, len(value)-1):
                        tmp = []
                        for part in value[i].text.split('/'):
                            tmp.append(int(part.strip()))
                        club.segments.append(Participants(tmp))
                    self.clubs.append(club)
                # decrement counter
                end -= 2
        
        a = 1
                        
        
    @staticmethod
    def read_pdf(pdf_file):
        new_class = PDFFile(pdf_file)
        new_class.read()
        return new_class
        
