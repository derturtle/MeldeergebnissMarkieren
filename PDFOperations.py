import os
from math import trunc

from Class_Clubs import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

from pypdf import PdfReader, PdfWriter, PageObject

STARTVALUE: str = 'Anzahl Meldungen'

ENDCLUB: str = 'Gesamtzahl der Meldungen'


MYVALUES: list = [
    'Kampfgericht Abschnitt',
    'Abschnitt',
    'Wettkampffolge für Abschnitt',
    'Wettkampf'
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
        self.header: float = 0.0
        
        self.analyse: dict = {}
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
        
        start: bool = False
        act_page = 0
        index = 0
        #
        pdf_pages = extract_pages(self._pdf_file)
        page_list = []
        for page in pdf_pages:
            page_list.append(page)
            print(fr'len {len(page_list)}')
            if len(page_list) == 12:
                print(fr'Break at {len(page_list)} for debug purpose')
                break
        
        # try to find start
        for page_no, page_layout in enumerate(page_list, start=act_page):
            if self._read_to_start(list(page_layout), page_no):
                act_page = page_no
                break
                
        # Get count of clubs and starts
        for page_no, page_layout in enumerate(page_list[act_page:], start=act_page):
            next_page, index = self._read_by_pages(list(page_layout), page_no, MYVALUES[0])
            if not next_page:
                self._get_clubs(self.analyse)
                act_page = page_no
                break
        
        # Create list to loop over other stuff
        end_values: list = []
        for i in range(len(self.clubs[list(self.clubs.keys())[0]].segments)):
            for entry in MYVALUES:
                end_values.append(fr'{entry} {i+1}')

        end_index = 1
        while end_index < len(end_values):

            self.analyse = {}
            # Create justing pannel
            for page_no, page_layout in enumerate(page_list[act_page:], start=act_page):
                next_page, index = self._read_by_pages(list(page_layout), page_no, end_values[end_index], index)
                if next_page:
                    #clear index again so that page starts with 0
                    index = 0
                else:
                    act_page = page_no
                    mod = end_index % len(MYVALUES)
                    end_index += 1
                    match mod:
                        case 1:
                            self._get_justing_panel(self.analyse)
                        case 2:
                            # do nothing ignore that
                            pass
                        case 3:
                            self._get_competition(self.analyse)
                            if end_index + len(MYVALUES) - 1 < len(end_values):
                                end_values[end_index + len(MYVALUES) -1] = fr'{MYVALUES[len(MYVALUES) - 1]} {len(self.competitions)}'
                        case _:
                            pass
                    break
        
  
            
    
    def _read_to_start(self, page_elements: list, page_no) -> bool:
        start_found: bool = False
        # Process each element in the layout of the page
        for element in page_elements:
            if isinstance(element, LTTextContainer):  # Check if the element is a text container
                for text_line in element:
                    if STARTVALUE in text_line.get_text():
                        # Match page
                        # Get header - increase to 1 to make sure for test for <
                        self.header = PDFText(text_line, page_no).bbox[3] + 1
                        start_found = True
                        break
        return start_found
    
    def _read_by_pages(self, page_elements: list, page_no, end_entry, start_index = 0) -> tuple[bool, int]:
        index = start_index
        for index, element in enumerate(page_elements[start_index:], start=start_index):
            if element.bbox[3] < self.header and isinstance(element, LTTextContainer):
                for text_line in element:
                    txt_obj = PDFText(text_line, page_no)
                    if txt_obj.text.startswith(end_entry):
                        return False, index
                    y_pos = page_no*1000.0 + txt_obj.y
                    if not y_pos in self.analyse.keys():
                        self.analyse[y_pos] = []
                    self.analyse[y_pos].append(txt_obj)
        return True, index
        
    def _get_clubs(self, page: dict):
        association: [Association, None] = None
        club_index: int = -1
        length : int= 0
        index: int = 0
        keys: list = list(page.keys())[:-3]
        # get correct cnt and index of club
        while index < len(keys) and club_index == -1:
            for i in range(len(page[keys[index]])):
                entry = page[keys[index]][i]
                if entry.text == 'Verein':
                    length = len(page[keys[index]])
                    association = Association.from_string(page[keys[index - 1]][0].text)
                    club_index = i
                    break
            index += 1
        
        while index < len(keys):
            # Create Clubs
            for index in range(index,len(keys)):
                text_list: list = page[keys[index]]
                if len(page[keys[index]]) == length:
                    self._create_club(text_list[club_index:], association)
                else:
                    break
            # Find new association
            for index in range(index, len(keys)):
                text_list: list = page[keys[index]]
                if len(text_list) == length and text_list[club_index].text == 'Verein':
                    association = Association.from_string(page[keys[index - 1]][0].text)
                    break
            # increment not to stop on last value
            index += 1
                    
    def _create_club(self, text_obj_line: list, association: Association):
        # Create club
        club = Club(text_obj_line[0].text, text_obj_line[1].text)
        # add occurrence
        club.occurrence.append(text_obj_line[0])
        # add association
        if association:
            club.association = association
        # Create participants
        tmp = []
        for part in text_obj_line[2].text.split('/'):
            tmp.append(int(part.strip()))
        club.participants = Participants(tmp)
        # Add segments
        for i in range(3, len(text_obj_line) - 1):
            tmp = []
            for part in text_obj_line[i].text.split('/'):
                tmp.append(int(part.strip()))
            club.segments.append(Participants(tmp))
        self.clubs[club.name] = club
        
        
    def _get_justing_panel(self, page: dict):
        for entry in page.values():
            if len(entry) > 1 and entry[len(entry)-1].text != 'Verein':
                last = entry[len(entry)-1]
                if last.text in self.clubs.keys():
                    self.clubs[last.text].occurrence.append(last)
                else:
                    club = Club(last.text, '-')
                    club.occurrence.append(last)
                    #self.clubs[club.name] = club
                    print(fr'{club} has no swimmer')
    
    def _get_competition(self, page: dict):
        for entry in page:
            com = Competition.from_string(entry.text)
            if com and not com.name() in list(self.competitions.keys()):
                self.competitions[com.name()] = com
            
    
    
                        
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
        
