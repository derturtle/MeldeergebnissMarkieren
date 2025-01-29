import os
from Class_Clubs import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

from pypdf import PdfReader, PdfWriter, PageObject

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
    
    clubs : dict = {}
    competitions : dict = {}
    sections : dict = {}
    
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
                    self.clubs[club.name] = club
                # decrement counter
                end -= 2
        
        return end
    
    def get_justing_panel(self, start_index: int, start_value: str, end_value: str) -> int:
        end = start_index
        # Find start of 'Judge panel'
        while end < len(self._pdf_texts):
            end+=1
            # Found 'Kampfgericht'
            if self._pdf_texts[end].text == start_value:
                break
        # Loop over 'Judge panel'
        while end < len(self._pdf_texts):
            end+=1
            # Found 'Kampfgericht'
            if self._pdf_texts[end].text.startswith(end_value):
                end -=1
                break
            if self._pdf_texts[end].text == 'Verein':
                # Check not for 'Verein' because it will appear later again
                exclude = ['Verein', 'noch ' + start_value, 'Name']
                while self._pdf_texts[end+1].text not in exclude and not self._pdf_texts[end+1].text.startswith(end_value):
                    end += 1
                    if self._pdf_texts[end].text in list(self.clubs.keys()):
                        self.clubs[self._pdf_texts[end].text].occurrence.append(self._pdf_texts[end])
                    else:
                        print(fr'Found club "{self._pdf_texts[end].text}" which does not start')
        return end
    
    def get_competitions(self, start_index: int, section: int):
        end = start_index
        
        if not section in self.sections.keys():
            self.sections[section] = []
        
        # Find start of 'Judge panel'
        while end < len(self._pdf_texts):
            end += 1
            # Found x
            if self._pdf_texts[end].text == fr'Wettkampffolge für Abschnitt {section}':
                break
        # Loop over x
        while end < len(self._pdf_texts):
            end += 1
            tmp = Competition.from_string(self._pdf_texts[end].text)
            if not tmp or tmp.name() in list(self.competitions.keys()):
                break
            else:
                self.competitions[tmp.name()] = tmp
                self.sections[section].append(tmp)
        return end
    
    def get_competitions_info(self, start_index: int, section: int):
        end = start_index
        
        # Find start of first competition
        while end < len(self._pdf_texts):
            if self._pdf_texts[end].text == self.sections[section][0].name():
                break
            end += 1
        # debug...
        self.process_competition(end, 1)
        
        pass
    
    def process_competition(self, start_index: int, competition_no: int):
        end = start_index
        rows: dict = {}
        while True:
        
            while not fr'Wettkampf {competition_no}' in self._pdf_texts[end].text:
                end += 1
                # end function if file end is reached
                if end >= len(self._pdf_texts):
                    return end
                    
            page = self._pdf_texts[end].page_no
            left = self._pdf_texts[end].x
            
            # next entry
            end += 1
            # First value is competition with number
            while page == self._pdf_texts[end].page_no:
                if self._pdf_texts[end].x == left:
                    if fr'Wettkampf {competition_no+1}' in self._pdf_texts[end].text or fr'Kampfgericht' in self._pdf_texts[end].text:
                        self.process_competition_rows(rows)
                        return end
                
                key = page * 1000 + self._pdf_texts[end].y
                
                if key in list(rows.keys()):
                    rows[key].append(self._pdf_texts[end])
                else:
                    rows[key] = [self._pdf_texts[end]]
                
                end += 1
                # end function if file end is reached
                if end >= len(self._pdf_texts):
                    self.process_competition_rows(rows)
                    return end
            
            
    
    def process_competition_rows(self, rows: dict):
        
        pass
        

        
        
                        
        
    @staticmethod
    def read_pdf(pdf_file):
        new_class = PDFFile(pdf_file)
        new_class.read()
        return new_class
        
