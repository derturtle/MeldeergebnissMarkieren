import datetime
import os
from math import trunc

from Class_Clubs import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

from pypdf import PdfReader, PdfWriter, PageObject

CLUB_STR: str = 'Verein'
CNT_ENTRIES_STR: str = 'Anzahl Meldungen'
JUDGING_PANEL_STR: str = 'Kampfgericht'
SECTION_STR: str = 'Abschnitt'
COMPETITION_SEQUENCE: str = 'Wettkampffolge'
HEAT_STR: str = 'Lauf'
LANE_STR: str = 'Bahn'

COMPARE_ENTRIES: list = [
    CNT_ENTRIES_STR,        #0
    JUDGING_PANEL_STR,      #1
    SECTION_STR,            #2 -
    COMPETITION_SEQUENCE,   #3
    HEAT_STR + ' 1/',       #4
    HEAT_STR + ' 1/'        #5
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
    class __FileInfo:
        HEADER_MAX = 10000.0
        def __init__(self):
            self.__state: int = 0
            self.__page_no: int = -1
            self.pages_data: dict = {}
            self.page_index: int = 0
            self.page_header: float = self.HEADER_MAX
            self.__last_repetition: int = 0
            self.__repetition: int = 0
        
        @property
        def page_no(self) -> int:
            return self.__page_no
        
        @page_no.setter
        def page_no(self, value: int):
            if self.__page_no != value:
                self.page_index = 0
                self.__page_no = value
        
        def get_compare_value(self) -> str:
            return COMPARE_ENTRIES[self.get_state()]
        
        def get_state(self) -> int:
            return self.__state
        
        def next_state(self) -> int:
            if self.__state == len(COMPARE_ENTRIES) -1 and self.__last_repetition > 0:
                # count down last repetition
                self.__last_repetition -= 1
            elif self.__state == len(COMPARE_ENTRIES) -1 and self.__repetition > 0:
                # set state to two
                self.__state = 2
                # count down repetition
                self.__repetition -= 1
            else:
                self.__state += 1
            # clear data of pages
            self.pages_data = {}
            
            # return state
            return self.get_state()
        
        def header_set(self) -> bool:
            return self.page_header != self.HEADER_MAX
        
        def set_last_state_repetition(self, value: int):
            self.__last_repetition = value
            
        def set_state_repetition(self, value: int):
            self.__repetition = value
        
    _pdf_file: str
    _pdf_texts: list[PDFText]
    
    clubs : dict = {}
    competitions : dict = {}
    sections : dict = {}
    athletes: dict = {}
    
    
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
         # Create file in class
        file_info: PDFFile.__FileInfo = PDFFile.__FileInfo()
        #e extract pages
        pdf_pages = extract_pages(self._pdf_file)
         
        print(fr'Starte verarbeitung')
        # Loop through each page in the PDF
        for page_no, page_layout in enumerate(pdf_pages, start=0):
            # Get the current page from the PDF
            print(fr'Page {page_no+1:02d}: analyse')
            # Set page no
            file_info.page_no = page_no
            # go to next page
            next_page = False
            # Set competition no
            competition_no = 1
            # Check for next page
            while True:
                next_page = self.__create_pages_data(list(page_layout), file_info)
                # in case of next page
                if next_page:
                    # end "while True" loop
                    break
                else:
                    #-- do analyse page
                    # Check for club entries
                    if file_info.get_state() == 5:
                        competition_no = self.__analyse_competition(file_info, competition_no)
                        # increase index because state 4  and 5 end on the same value
                        file_info.page_index += 1
                        # output - for info
                        if competition_no in list(self.competitions.keys()):
                            print(fr'Verarbeite Wettkampf {competition_no}')
                        else:
                            print(fr'Verarbeite Kampfgericht')
                    elif file_info.get_state() == 4:
                        competition_no = self.__analyse_sequenz(file_info)
                        # increase index because state 4  and 5 end on the same value
                        file_info.page_index += 1
                        # output - for info
                        print(fr'Verarbeite Wettkampf {competition_no}')
                    elif file_info.get_state() == 2:
                        self.__analyse_judging_panel(file_info)
                        # output - for info
                        print(fr'Verarbeite Wettkampffolge')
                    elif file_info.get_state() == 1:
                        self.__analyse_clubs(file_info)
                        # output - for info
                        print(fr'Verarbeite Kampfgericht')
                    elif file_info.get_state() == 0:
                        # output - for info
                        print(fr'Verarbeite Anzahl der Meldungen')
                    
                    # set next state
                    file_info.next_state()
        
    @staticmethod
    def __create_pages_data(page_elements: list, file_info: __FileInfo) -> bool:
        next_page: bool = True
        # Process each element in the layout of the page
        for index, element in enumerate(page_elements[file_info.page_index:], start=file_info.page_index):
            if element.bbox[3] < file_info.page_header and isinstance(element, LTTextContainer):  # Check if the element is a text container
                for text_line in element:
                    txt_obj = PDFText(text_line, file_info.page_no)
                    # -- Check for match - to end scan
                    if txt_obj.text.startswith(file_info.get_compare_value()):
                        # Match page
                        if not file_info.header_set():
                            # Get header - increase to 1 to make sure for test for <
                            file_info.page_header = txt_obj.bbox[3] + 1
                        # Set index
                        file_info.page_index = index
                        # Indicate to work on this page
                        next_page = False

                    # -- Add entry to page data (no end occurred)
                    # Create an individual key
                    y_pos = file_info.page_no * 1000.0 + txt_obj.y
                    # Check if key still on page data
                    if not y_pos in file_info.pages_data.keys():
                        # If not create list
                        file_info.pages_data[y_pos] = []
                    # Add page data to list
                    file_info.pages_data[y_pos].append(txt_obj)
        return next_page
        
    def __analyse_clubs(self, file_info: __FileInfo):
        association: [Association, None] = None
        club_index: int = -1
        length : int= 0
        index: int = 0
        keys: list = list(file_info.pages_data.keys())[:-3]
        # get correct cnt and index of club
        while index < len(keys) and club_index == -1:
            entries = file_info.pages_data[keys[index]]
            for i in range(len(entries)):
                entry = entries[i]
                if entry.text == CLUB_STR:
                    length = len(entries)
                    association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                    club_index = i
                    break
            index += 1
       
        while index < len(keys):
            # Create Clubs
            for index in range(index,len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                if len(file_info.pages_data[keys[index]]) == length:
                    club = self.__create_club(text_list[club_index:], association)
                    self.clubs[club.name] = club
                else:
                    break
            # Find new association
            for index in range(index, len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                if len(text_list) == length and text_list[club_index].text == CLUB_STR:
                    association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                    break
            # increment not to stop on last value
            index += 1
        
        # Set for every segment a repetition
        file_info.set_state_repetition(len(list(self.clubs.values())[0].segments) - 1)
                    
    @staticmethod
    def __create_club(text_obj_line: list, association: Association) -> Club:
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
        return club
        
        
    def __analyse_judging_panel(self, file_info: __FileInfo):
        empty_clubs: dict = {}
        for entry in file_info.pages_data.values():
            if len(entry) > 1 and entry[len(entry)-1].text != CLUB_STR:
                last = entry[len(entry)-1]
                if last.text in self.clubs.keys():
                    self.clubs[last.text].occurrence.append(last)
                else:
                    club = Club(last.text, '-')
                    if club.name in list(empty_clubs.keys()):
                        empty_clubs[club.name].occurrence.append(last)
                    else:
                        empty_clubs[club.name] = club
                        #self.clubs[club.name] = club
                        print(fr'{club} has no swimmer')
    
    def __analyse_sequenz(self, file_info: __FileInfo) -> int:
        competition_cnt = 0
        next_competition = 0
        for entry in file_info.pages_data.values():
            competition = Competition.from_string(entry[0].text)
            if competition and not competition.no in list(self.competitions.keys()):
                self.competitions[competition.no] = competition
                if competition_cnt == 0:
                    next_competition = competition.no
                # In case of final didn't count it has no run
                if competition.is_final():
                    print(fr'Finale Wettkampf {competition.no} gefunden')
                else:
                    competition_cnt += 1
        # Set for every
        file_info.set_last_state_repetition(competition_cnt - 1)
        return next_competition
            
    def __analyse_competition(self, file_info: __FileInfo, competition_no: int) -> int:
        competition = self.competitions[competition_no]
        # still found heat 1 so crete it here
        heat = Heat(1, competition)
        
        for entry in file_info.pages_data.values():
            if len(entry) == 5 and entry[3].text != CLUB_STR:
                # Create athlete
                athlete_text = ' '.join(map(str, entry[1:4]))
                if not athlete_text in list(self.athletes.keys()):
                    self.athletes[athlete_text] = Athlete(entry[1].text, int(entry[2].text), self.clubs[entry[3].text])
                self.athletes[athlete_text].occurrence.append(entry[1])
                # add year
                
                # Create lane
                lane_no = int(entry[0].text.replace(LANE_STR, '').strip())
                time = datetime.time.fromisoformat(fr'00:{entry[4].text}')
                lane = Lane(lane_no, time, self.athletes[athlete_text], heat)
            elif len(entry) == 1:
                heat = Heat.from_string(entry[0].text)
                if heat:
                    if competition:
                        heat.competition = competition
                else:
                    tmp_obj = Competition.from_string(entry[0].text)
                    if tmp_obj and tmp_obj.no in list(self.competitions.keys()):
                        competition = self.competitions[tmp_obj.no]
            else:
                pass
        
        if competition_no == competition.no:
            return competition_no + 1
        else:
            return competition.no
        
    
    
                        
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
            if self._pdf_texts[end].text == 'Nr.' or self._pdf_texts[end].text == CLUB_STR:
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
            # Check for match "CLUB_STR" for sub because
            if self._pdf_texts[end].text == CLUB_STR:
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
            if self._pdf_texts[end].text == CLUB_STR:
                # Check not for CLUB_STR because it will appear later again
                exclude = [CLUB_STR, 'noch ' + start_value, 'Name']
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
        
