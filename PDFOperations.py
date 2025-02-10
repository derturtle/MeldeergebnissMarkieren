import os

from Class_Clubs import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno, LTItem

from pypdf import PdfReader, PdfWriter, PageObject
from pypdf.generic import DictionaryObject, NameObject, ArrayObject, FloatObject


class PDFText:
    def __init__(self, text_container: LTItem, page_no: int):
        self.text_container: LTItem = text_container
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
        HEADER_MAX: float = 10000.0
        PAGE_INDEX_INIT: int = -1
        
        def __init__(self):
            self.step: int = 0
            self.section_no: int = 1
            self.competition_no: int = 1
            
            self.max_section: int = 0
            self.max_competition: int = 0
            
            self.__page_no: int = self.PAGE_INDEX_INIT
            self.pages_data: dict = {}
            self.page_index: int = -1
            self.page_header: float = self.HEADER_MAX
        
        @property
        def page_no(self) -> int:
            return self.__page_no
        
        @page_no.setter
        def page_no(self, value: int):
            if self.__page_no != value:
                self.page_index = self.PAGE_INDEX_INIT
                self.__page_no = value
        
        def clear_page_data(self):
            self.pages_data = {}
        
        def header_set(self) -> bool:
            return self.page_header != self.HEADER_MAX
    
    def __init__(self, pdf_file):
        self._pdf_file: str
        self.collection: SpecialCollection
        self.pdf_file = pdf_file
        pass
    
    @property
    def pfd_values(self):
        if self.collection.config:
            return self.collection.config.pdf_values
        else:
            return None
    
    @property
    def pdf_file(self) -> str:
        return self._pdf_file
    
    @pdf_file.setter
    def pdf_file(self, value: str):
        if os.path.exists(value):
            self._pdf_file = os.path.abspath(value)
            self.collection = SpecialCollection(os.path.basename(self._pdf_file))
        else:
            raise ValueError
    
    def highlight_annotation(self, output_file: str, occurrences: list[PDFText], color: list, start_perc: int = 7,
                             end_perc: int = 95, offset_px: int = 1):
        # Read the input PDF using PyPDF2
        if color is None:
            color = [255, 255, 0]
        reader = PdfReader(self.pdf_file)
        writer = PdfWriter()
        # check color
        if len(color) != 3:
            raise ValueError
        for i in range(0,len(color)):
            if color[i] > 255:
                color[i] = 255
            elif color[i] < 0:
                color[i] = 0
            # convert to float
            color[i] = float(color[i]) / 255
        # Correct inputs
        if start_perc < 0 or start_perc > 100:
            start_perc = 0
        if end_perc < 0 or end_perc > 100:
            end_perc = 100
        if offset_px < 0:
            offset_px = 0
        # Set variables
        page_no = 0
        page = reader.pages[page_no]
        width = page.mediabox[2]
        # Calculate start and end position
        start_pos = float(width) * (start_perc / 100)
        end_pos = float(width) * (end_perc / 100)
        # loop over pages
        i = 0
        for page_no in range(1, reader.get_num_pages()):
            page = reader.pages[page_no]
            
            while i < len(occurrences):
                if occurrences[i].page_no == page_no:
                    self.__add_highlight_annotation(page, occurrences[i], color, start_pos, end_pos, offset_px)
                    i += 1
                else:
                    break
            
            writer.add_page(page)
        
        # Write the modified PDF to the output file
        with open(output_file, "wb") as fp:
            writer.write(fp)
        # print(f"Found {len(occurrences)} occurrence of {search_text}.")
        print(f"Saved highlighted PDF to {output_file}.")
    
    def __add_highlight_annotation(self, page: PageObject, pdf_text: PDFText, rgb_color: list, start_pos: float,
                                   end_pos: float, offset_px: int):
        """
        Adds a highlight annotation to a PDF page.
        """
        # Unpack the bounding box coordinates
        x0, y0, x1, y1 = pdf_text.bbox
        x0 = start_pos
        x1 = end_pos
        
        # Create a highlight annotation dictionary
        highlight = DictionaryObject()
        highlight.update({
            NameObject("/Type"): NameObject("/Annot"),  # Annotation type
            NameObject("/Subtype"): NameObject("/Highlight"),  # Highlight annotation subtype
            NameObject("/Rect"): ArrayObject([
                FloatObject(x0), FloatObject(y0), FloatObject(x1), FloatObject(y1)
            ]),  # Rectangle defining the annotation area
            NameObject("/QuadPoints"): ArrayObject([
                # Coordinates for the highlight area (quadrilateral points)
                FloatObject(x0), FloatObject(y1 + offset_px),  # Top-left
                FloatObject(x1), FloatObject(y1 + offset_px),  # Top-right
                FloatObject(x0), FloatObject(y0 - offset_px),  # Bottom-left
                FloatObject(x1), FloatObject(y0 - offset_px)  # Bottom-right
            ]),
            # Set color of annotation
            NameObject("/C"): ArrayObject(
                [FloatObject(rgb_color[0]), FloatObject(rgb_color[1]), FloatObject(rgb_color[2])]),
            NameObject("/F"): FloatObject(4),  # Annotation flags (4 = printable)
        })
        
        # Add the annotation to the page's annotations list
        if "/Annots" not in page:
            page[NameObject("/Annots")] = ArrayObject()
        page[NameObject("/Annots")].append(highlight)
    
    def read(self):
        # Create file in class
        file_info: PDFFile.__FileInfo = PDFFile.__FileInfo()
        # e extract pages
        pdf_pages = extract_pages(self._pdf_file)
        
        print(fr'Analyse file {self._pdf_file}')
        
        # Set next value to find
        find_next = self.pfd_values.entry_cnt
        # Loop through each page in the PDF
        for page_no, page_layout in enumerate(pdf_pages, start=0):
            # Get the current page from the PDF
            print(fr'Read page {page_no + 1:02d}')
            # Set page no
            file_info.page_no = page_no
            # Check for next page
            while True:
                next_page = self.__create_pages_data(list(page_layout), file_info, find_next)
                # in case of next page
                if next_page:
                    # end "while True" loop
                    break
                else:
                    find_next = self.__analyse_steps(file_info)
    
    def __analyse_steps(self, file_info: __FileInfo) -> str:
        step = file_info.step
        next_value: str = ''
        if step == 0:
            # set next find_str
            next_value = self.pfd_values.judging_panel
            # set next step
            file_info.step += 1
            file_info.clear_page_data()
            # output - for info
            print(fr'Verarbeite Anzahl der Meldungen')
        elif step == 1:
            # Run function
            self.__analyse_clubs(file_info, self.pfd_values.entry_cnt, self.pfd_values.judging_panel)
            # Set max section in competition
            # file_info.max_section = len(list(self.clubs.values())[0].starts_by_segments)
            # neu collection
            file_info.max_section = len(self.collection.clubs[0].starts_by_segments)
            # Create sections
            for i in range(file_info.max_section):
                Section(i + 1)
            
            # set next find_str
            next_value = self.pfd_values.segment
            # set next step
            file_info.step += 1
            file_info.clear_page_data()
            # output - for info
            print(fr'Verarbeite Kampfgericht - Abschnitt {file_info.section_no}')
        elif step == 2:
            self.__analyse_judging_panel(file_info, self.pfd_values.judging_panel, self.pfd_values.segment)
            
            # set next find_str
            next_value = self.pfd_values.competition_sequenz
            # set next step
            file_info.step += 1
            file_info.clear_page_data()
            # output - for info
            print(fr'Verarbeite Abschnitssdaten - Abschnitt {file_info.section_no}')
        elif step == 3:
            
            # set next find_str
            next_value = self.pfd_values.heat + ' 1/'
            # set next step
            file_info.step += 1
            file_info.clear_page_data()
            # output - for info
            print(fr'Verarbeite Wettkampffolge - Abschnitt {file_info.section_no}')
        elif step == 4:
            file_info.competition_no = self.__analyse_sequenz(file_info, self.pfd_values.competition_sequenz)
            
            # In case this sections has only finals
            if file_info.competition_no == -1:
                # increase section number
                file_info.section_no += 1
                # end or go to next
                next_value = self.__end_or_next_section(file_info)
            else:
                # Set max competition_no for this segment
                for entry in list(reversed(self.collection.competitions)):
                    if not entry.is_final():
                        file_info.max_competition = entry.no
                        break
                # Increment page index not start over at heat 1
                file_info.page_index += 1
                
                # set next find_str
                next_value = self.pfd_values.heat + ' 1/'
                # set next step
                file_info.step += 1
                file_info.clear_page_data()
                # output - for info
                print(fr'Verarbeite Wettkampf {file_info.competition_no} ')
        elif step == 5:
            file_info.competition_no = self.__analyse_competition(file_info, file_info.competition_no)
            # Decrement page index to make sure to find the competition
            file_info.page_index -= 1
            
            if file_info.competition_no == file_info.max_competition:
                # increase setion no
                file_info.section_no += 1
                if file_info.section_no <= file_info.max_section:
                    # set next find_str
                    next_value = self.pfd_values.judging_panel
                else:
                    # set next find_str - because of last entry find itself
                    next_value = self.collection.competition_by_no(file_info.competition_no).name()
                # Do not change step
                file_info.clear_page_data()
                # output - for info
                print(fr'Verarbeite Wettkampf {file_info.competition_no} ')
            # Create next steps
            elif file_info.competition_no > file_info.max_competition:
                next_value = self.__end_or_next_section(file_info, self.pfd_values.segment)
            else:
                # set next find_str
                next_value = self.collection.competition_by_no(file_info.competition_no + 1).name()
                # Do not set step but clear data
                file_info.clear_page_data()
                # output - for info
                print(fr'Verarbeite Wettkampf {file_info.competition_no} ')
        else:
            # do nothing
            print(fr'Finished')
        
        return next_value
    
    @staticmethod
    def __end_or_next_section(file_info: __FileInfo, section_str: str):
        if file_info.section_no <= file_info.max_section:
            # set next find_str
            next_value = section_str
            # Set step to judging panel section 2
            file_info.step = 2
            file_info.clear_page_data()
            # output - for info
            print(fr'Verarbeite Kampfgericht - Abschnitt {file_info.section_no}')
        else:
            # Dummy value
            next_value = '#####'
            # End
            file_info.step = -1
            file_info.clear_page_data()
        return next_value
    
    @staticmethod
    def __create_pages_data(page_elements: list, file_info: __FileInfo, stop_value) -> bool:
        next_page: bool = True
        # Process each element in the layout of the page
        for index, element in enumerate(page_elements, start=0):
            if element.bbox[3] < file_info.page_header and isinstance(element,
                                                                      LTTextContainer):  # Check if the element is a text container
                for text_line in element:
                    # LTChar
                    # LTAnno
                    # Represent an actual letter in the text as a Unicode string. Note that, while a LTChar object has
                    # actual boundaries, LTAnno objects does not, as these are "virtual" characters, inserted by a
                    # layout analyzer according to the relationship between two characters (e.g. a space).
                    if isinstance(text_line, LTAnno) or isinstance(text_line, LTChar):
                        # Ignore LTAnno
                        continue
                    txt_obj = PDFText(text_line, file_info.page_no)
                    # -- Check for match - to end scan
                    if index > file_info.page_index and txt_obj.text.startswith(stop_value):
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
    
    @staticmethod
    def __remove_to_start(file_info: __FileInfo, compare_string: str, precise: bool = False):
        rm_keys: list = []
        for key, entry in file_info.pages_data.items():
            rm_keys.append(key)
            if len(entry) == 1:
                if not precise:
                    if entry[0].text.startswith(compare_string):
                        break
                else:
                    if entry[0].text == compare_string:
                        break
        
        for key in rm_keys:
            del file_info.pages_data[key]
    
    def __analyse_clubs(self, file_info: __FileInfo, start_value: str, stop_value: str):
        association: [Association, None] = None
        club_index: int = -1
        length: int = 0
        index: int = 0
        # Remove unused values from page
        self.__remove_to_start(file_info, start_value)
        # Create key list to loop over values
        keys: list = list(file_info.pages_data.keys())[:-3]
        # get correct cnt and index of club
        while index < len(keys) and club_index == -1:
            entries = file_info.pages_data[keys[index]]
            for i in range(len(entries)):
                entry = entries[i]
                if entry.text == self.pfd_values.club and not file_info.pages_data[keys[index - 1]][0].text.startswith(
                        'noch'):
                    length = len(entries)
                    association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                    club_index = i
                    break
            index += 1
        
        if club_index != 1:
            print('[Debug] Clubs are not count')
        else:
            print('[Debug] Clubs has a number')
        
        while index < len(keys):
            # Create Clubs - without number
            if club_index != 1:
                for index in range(index, len(keys)):
                    text_list: list = file_info.pages_data[keys[index]]
                    if len(file_info.pages_data[keys[index]]) == length:
                        self.__create_club(text_list[club_index:], association)
                    else:
                        break
            # Clubs has number and are in one line?
            else:
                for index in range(index, len(keys)):
                    text_list: list = file_info.pages_data[keys[index]]
                    if len(file_info.pages_data[keys[index]]) == length:
                        self.__create_club(text_list[club_index:], association)
                    elif len(file_info.pages_data[keys[index]]) == length - 1:
                        name = ' '.join(text_list[0].text.split(' ')[1:])
                        self.__create_club(text_list, association, name)
                    else:
                        break
            # Find new association
            for index in range(index, len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                if len(text_list) == length and text_list[club_index].text == self.pfd_values.club:
                    association_str = file_info.pages_data[keys[index - 1]][0].text
                    if not association_str.startswith('noch') and association_str != 'Gesamtzahl der Meldungen':
                        association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                    break
                # end in case stop is reached
                elif len(text_list) == 1 and text_list[0].text.startswith(stop_value):
                    index = len(keys)
                    break
            
            # increment not to stop on last value
            index += 1
    
    def __analyse_judging_panel(self, file_info: __FileInfo, start_value: str, stop_value: str):
        # create club list
        club_list = [x.name for x in self.collection.clubs]
        # Remove unused values from page
        self.__remove_to_start(file_info, start_value)
        for entry in file_info.pages_data.values():
            if len(entry) > 1:
                if entry[len(entry) - 1].text != self.pfd_values.club:
                    # Add club
                    last = entry[len(entry) - 1]
                    if last.text in club_list:
                        index = club_list.index(last.text)
                        club = self.collection.clubs[index]
                        club.add_occurrence(last)
                    else:
                        club = self.__generate_club(last)
                        club_list.append(club.name)
                        print(fr'{club} has no swimmer')
                    
                    judge_name = '-'
                    if len(entry) == 3:
                        judge_name = entry[1].text
                    # Create judge
                    Judge(entry[0].text, judge_name, club, self.collection.sections_by_no(file_info.section_no))
            else:
                # found stop condition
                if entry[0].text.startswith(stop_value):
                    break
    
    def __analyse_sequenz(self, file_info: __FileInfo, start_value: str) -> int:
        next_competition: int = 0
        # Remove unused values from page
        self.__remove_to_start(file_info, start_value)
        
        for entry in file_info.pages_data.values():
            competition = Competition.from_string(entry[0].text, self.collection.sections_by_no(file_info.section_no))
            if competition:
                if self.collection.competitions.index(competition) == len(self.collection.competitions) - 1:
                    # In case of final didn't count it has no run
                    if competition.is_final():
                        print(fr'Finale Wettkampf {competition.no} gefunden')
                else:
                    # get next competition which is not final
                    if competition.is_final():
                        next_competition = -1
                        for comp in self.collection.competitions[self.collection.competitions.index(competition) + 1:]:
                            if not comp.is_final():
                                next_competition = comp.no
                                break
                    else:
                        # Stop condition found start competition still in list
                        next_competition = competition.no
                    break
        return next_competition
    
    def __analyse_competition(self, file_info: __FileInfo, competition_no: int) -> int:
        # active competition
        competition = self.collection.competition_by_no(competition_no)
        # Remove unused values from page
        self.__remove_to_start(file_info, competition.name(), True)
        
        # Still no heat found
        heat = None
        # create heat_zero
        heat_zero = Heat(0)
        
        for entry in file_info.pages_data.values():
            if len(entry) == 5 and entry[3].text != self.pfd_values.club:
                
                # Create year
                year = self.__generate_year(entry[2])
                # Create club
                club = self.__generate_club(entry[3])
                # Create athlete
                athlete_text = ' '.join(map(str, entry[1:4]))
                athlete_name = entry[1].text
                # In case of relay on real name is there
                if competition.is_relay():
                    athlete_text += fr' ({competition.sex})'
                    athlete_name += fr' ({competition.sex})'
                
                # Check if athlete exist
                athlete = None
                athlete_list = self.collection.athletes_by_name(athlete_name)
                if athlete_list:
                    if len(athlete_list) > 0:
                        for a in athlete_list:
                            if a.club == club and a.year == year:
                                athlete = a
                                break
                    else:
                        athlete = athlete_list[0]
                
                if not athlete:
                    # Create Athlete
                    athlete = Athlete(athlete_name, year, club)
                
                # Create lane
                lane_no = int(entry[0].text.replace(self.pfd_values.lane, '').strip())
                time = datetime.time.fromisoformat(fr'00:{entry[4].text}')
                if heat:
                    lane = Lane(lane_no, time, athlete, heat)
                else:
                    lane = Lane(lane_no, time, athlete, heat_zero)
            elif len(entry) == 1:
                # create new heat
                heat = Heat.from_string(entry[0].text)
                if heat:
                    if competition:
                        heat.competition = competition
                else:
                    tmp_obj = Competition.from_string(entry[0].text)
                    if tmp_obj:
                        # Ad heat 0 to competition if it has lanes
                        if len(heat_zero.lanes) > 0:
                            heat_zero.competition = competition
                        else:
                            heat_zero.remove()
                        competition = tmp_obj
                        # Also end condition - next competition
                        break
            else:
                pass
        
        if competition_no == competition.no:
            return competition_no + 1
        else:
            return competition.no
    
    def __generate_year(self, text_obj: PDFText) -> Year:
        try:
            year_no = int(text_obj.text)
        except:
            year_no = 0
        
        year = self.collection.get_year(year_no)
        if not year:
            year = Year(year_no)
        year.add_occurrence(text_obj)
        return year
    
    def __create_club(self, text_obj_line: list, association: Association, name: str = '') -> Club:
        # Create club
        club = self.__generate_club(text_obj_line[0], text_obj_line[1].text, name)
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
            club.starts_by_segments.append(Starts(tmp))
        return club
    
    def __generate_club(self, text_obj: PDFText, club_id: str = '-', name: str = '') -> Club:
        # check if club in list
        club_exist = any(x.name == text_obj.text for x in self.collection.clubs)
        if not club_exist:
            # Create club
            if name == '':
                club = Club(text_obj.text, club_id)
            else:
                club = Club(name, club_id)
        else:
            index = self.collection.clubs.index(text_obj.text)
            club = self.collection.clubs[index]
        club.add_occurrence(text_obj)
        return club
    
    @staticmethod
    def read_pdf(pdf_file):
        new_class = PDFFile(pdf_file)
        new_class.read()
        return new_class
