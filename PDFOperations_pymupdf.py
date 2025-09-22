import os
import pymupdf
from Class_Competition_Objects import *

class PDFText:
    
    def __init__(self, value: tuple, page_no: int = -1):
        self._value : tuple = value
        self._page_no : int = -1
    
    def __str__(self) -> str:
        return self.text
    
    @property
    def page_no(self) -> int:
        return self._page_no
    
    @property
    def value(self) -> tuple:
        return self._value
    
    @property
    def bbox(self) -> tuple:
        return self._value[0], self._value[1], self._value[2], self._value[3]
    
    @property
    def x(self) -> float:
        return self._value[0]
    
    @property
    def y(self) -> float:
        return self._value[1]
    
    @property
    def width(self) -> float:
        return self._value[2] - self._value[0]
    
    @property
    def height(self) -> float:
        return self._value[3] - self._value[1]
    
    @property
    def text(self) -> str:
        return self._value[4]
    
    @staticmethod
    def combine(pdftext_objects: list):
        x1: float = 10000.0
        y1: float = 10000.0
        x2: float = 0.0
        y2: float = 0.0
        text: str = ''
        for obj in pdftext_objects:
            if type(obj) is PDFText:
                text += obj.text + ' '
                if x1 > obj.bbox[0]:
                    x1 = obj.bbox[0]
                if y1 > obj.bbox[1]:
                    y1 = obj.bbox[1]
                if x2 < obj.bbox[2]:
                    x2 = obj.bbox[2]
                if y2 < obj.bbox[3]:
                    y2 = obj.bbox[3]
        return PDFText((x1, y1, x2, y2, text.strip()))
    
class PDFOperations:
    
    class _ReadPDF:
        
        def __init__(self, doc):
            self.pages: list = list(doc.pages())
            self.index: int = -1
            self._last_data = {}
            
        def next_page(self):
            if 0 <= self.index + 1 < len(self.pages):
                self.index += 1
                return self.pages[self.index]
            else:
                return None
        
        def next_textpage(self):
            page = self.next_page()
            if page:
                return page.get_textpage()
            return page
            
        def get_page(self):
            if 0 <= self.index < len(self.pages)-1:
                return self.pages[self.index]
            elif self.index == -1:
                return self.next_page()
            return None
        
        def get_textpage(self):
            page = self.get_page()
            if page:
                return page.get_textpage()
            return page
        
        def next_data(self, text: str, header: float = -1000000.0) -> tuple:
            
            def store_data(data: dict, y_key: float, pdf_obj: PDFText) -> float:
                """ Stores data into a different dictionary
                
                :param data: dictionary to store data in
                :param y_key: old value or key
                :param pdf_obj: object to be stored
                :return: y_key (updated)
                """
                if y_key != pdf_obj.y + ((self.index + 1) * 1000):
                    y_key = pdf_obj.y + ((self.index + 1) * 1000)
                    data[y_key] = []
                data[y_key].append(pdf_obj)
                return y_key
                
            
            page_data: dict = {}
            # Get starting point
            page = self.get_textpage()
            # Loop over pages
            while page:
                # Check if result in page
                result = page.search(text)
                # There is still old data
                if self._last_data:
                    page_data.update(self._last_data)
                    self._last_data = {}
                    
                    if result:
                        key = result[0].ul.y + ((self.index + 1) * 1000)
                        keys = list(page_data.keys())
                        cpy_keys = keys[keys[key]:]
                        for i in cpy_keys[1:]:
                            self._last_data[i] = page_data[i].copy()
                            del page_data[i]
                        return page_data[key].copy(), page_data, self.index
                else:
                    y_old: float = -1.0
                    key: float = y_old
                    # Get words
                    for entry in page.extractWORDS():
                        pdf_text = PDFText(entry)
                        # Add only if not in header
                        if pdf_text.y > header:
                            # In case there is no result or the object is bigger tha the result
                            if not result or pdf_text.y <= result[0].ul.y:
                                # Store in page data
                                y_old = store_data(page_data, y_old, pdf_text)
                                key = y_old
                            else:
                                # Otherwise store for next run
                                y_old = store_data(self._last_data, y_old, pdf_text)
                    if result:
                        if key > 0:
                            return page_data[key].copy(), page_data, self.index
                        else:
                            return [], {}, self.index
                # Next step
                page = self.next_textpage()
            # found nothing
            return [], {}, self.index
                
                
            
            
                
    
    def __init__(self, pdf_file: str = ''):
        # self._rd_index : int = 0
        self._header_pos = 0.0
        pass
    
    def read_pdf(self, pdf_file: str) -> bool:
        
        rd_index = -1
        
        def _next_textpage():
            if len(self._doc.pages()) < rd_index + 1:
                rd_index += 1
                return list(self._doc.pages())[rd_index].get_textpage()
            else:
                return None
        
        # ---- File checks -----
        # use full path
        pdf_file = os.path.abspath(pdf_file)
        # Check if file exist
        if not os.path.exists(pdf_file):
            return False

        
        # ---- Start reading -----
        # Generate local variables
        self._collection: SpecialCollection = SpecialCollection(os.path.abspath(pdf_file))
        # shortcut for pdf values
        self._pdf_values = self._collection.config.pdf_values
        
        self._doc = pymupdf.open(pdf_file)

        # ----- Work with reading object -----
        read_obj = self._ReadPDF(self._doc)
        
        # get header
        findings, page_dict, _ = read_obj.next_data(self._pdf_values.entry_cnt)
        if findings:
            self._header_pos = findings[0].y - 1.0
            
        # get competition information
        findings, page_dict, _ = read_obj.next_data(self._pdf_values.judging_panel, self._header_pos)
        
        page = read_obj.get_textpage()
        blocks = page.extractBLOCKS()
        
        self._analyse_result_report(page_dict)
        
        a=1
       
        
       
        
    def _analyse_result_report(self, page_dict: dict):
        

        parse_step: int = 0
        
        pdf_values = self._collection.config.pdf_values
        
        # Create variables
        association: [Association, None] = None
        
        entry_len: int = 0
        club_index: int = 0
        header_line: list = []
        
        keys = list(page_dict.keys())
        # Get entry len and club position
        for i, key in enumerate(keys, start=0):
            # Loop over list
            for j in range(len(page_dict[key])):
                if page_dict[key][j].text == pdf_values.club:
                    header_line = page_dict[key]
                    entry_len = len(page_dict[key])
                    club_index = j
                    break
            if entry_len != 0:
                break
        
        # Do a debug print
        if club_index != 1:
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | Clubs are not numbered')
        else:
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | Clubs are numbered')
        
        # Get first association an
        for i, key in enumerate(keys, start=0):
            # ----- Find assosiation
            if parse_step == 0:
                if page_dict[key][club_index].text == pdf_values.club:
                    association_text = ' '.join(obj.text for obj in page_dict[keys[i-1]])
                    association_text.replace(pdf_values.continue_value, '').strip()
                    
                    if association_text == pdf_values.no_of_entries:
                        # End loop found everything
                        break
                        
                    association = Association.from_string(association_text)
                    parse_step += 1
            # ----- Find clubs
            else:
                # Create text from object
                texts:  list = [obj.text for obj in page_dict[key]]
                # No. and Club are the same
                if club_index != 0 and len(page_dict[key]) == entry_len-1:
                    split = texts[0].split('.')
                    texts[0] = split[1]
                    texts.insert(0, f'{split[0]}.')
                
                if page_dict[keys[i+2]][club_index].text == pdf_values.club:
                    parse_step -= 1
                else:
                    self._extract_club(page_dict[key][club_index:], header_line[club_index + 1].x, association)
                # # if len(texts) == entry_len:
                #     self._extract_club(page_dict[key][club_index:], header_line[club_index+1].y, association, texts[club_index])
                # else:
                #     parse_step -= 1
    
    def _extract_club(self, text_obj_line: list, x_end: float, association: Association) -> Club:
        """ Extract the club from a text line
        :type text_obj_line: list
        :param text_obj_line: PDFtext object as list
        :type association: Association
        :param association: The club belongs to this association
        :type name: str
        :param name: Name of the Club
        :return: A club object
        """
        i = -1
        while i < len(text_obj_line):
            i+=1
            if text_obj_line[i].x >= x_end:
                break
        
        club_obj = PDFText.combine(text_obj_line[:i])
        
        # Create club
        club = self._generate_club(club_obj, text_obj_line[i].text, club_obj.text)
        # add association
        if association:
            club.association = association
        
        # Create participants
        participants = [int(str(text_obj_line[i+1]).replace('/', '')), int(str(text_obj_line[i+2]).replace('/', ''))]
        club.participants = Participants(participants)
        
        for j in range(i+3, len(text_obj_line)-2, 2):
            tmp = [int(str(text_obj_line[j]).replace('/', '')), int(str(text_obj_line[j+1]).replace('/', ''))]
            club.starts_by_segments.append(Starts(tmp))
        
        # tmp = []
        # for part in text_obj_line[2].text.split('/'):
        #     tmp.append(int(part.strip()))
        # club.participants = Participants(tmp)
        # # Add segments
        # for i in range(3, len(text_obj_line) - 1):
        #     tmp = []
        #     for part in text_obj_line[i].text.split('/'):
        #         tmp.append(int(part.strip()))
        #     club.starts_by_segments.append(Starts(tmp))
        return club
    
    def _generate_club(self, text_obj: PDFText, club_id: str = '-', name: str = '') -> Club:
        """ Generates a new club object (if not still available)
        :type text_obj: PDFText
        :param text_obj: Object with the text
        :type club_id; str
        :param club_id: The club id
        :type name: str
        :param name: Name of the Club
        :return: A club object
        """
        # check if club in list with name and pdf text
        club = next((x for x in self._collection.clubs if x.name == text_obj.text or x.name == name), None)
        if not club:
            # Create club
            if name == '':
                club = Club(text_obj.text, club_id)
            else:
                club = Club(name, club_id)
        # Add PDF object as occurrence to club
        club.add_occurrence(text_obj)
        return club
                
            
    
    
def _page_to_dict_row(page: pymupdf.TextPage, page_no: int, key: str) -> tuple:
    
    match = False
    page_dict = {}
    # page.search() # todo look into it
    page_offset = page_no * 1000
    
    entries = page.extractWORDS()
    
    tmp_y : float= -1.0
    
    for entry in entries:
        pdf_text = PDFText(entry, page_no)
        match = pdf_text.text == key
        
        if tmp_y != pdf_text.y:
            tmp_y = pdf_text.y
            page_dict[float(page_offset) + pdf_text.y] = []
        
        page_dict[float(page_offset) + pdf_text.y].append(pdf_text)
        
    return page_dict, match
    
    



