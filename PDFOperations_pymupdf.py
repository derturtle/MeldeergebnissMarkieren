import os
import pymupdf
from Class_Competition_Objects import *

class PDFText:
    
    def __init__(self, value: tuple, page_no: int = -1):
        self._value : tuple = value
        
        if page_no > 0:
            self._page_no = page_no
        else:
            self._page_no: int = -1
    
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
    def combine(pdftext_objects: list, page_no: int = -1):
        # Check for only a single object
        if len(pdftext_objects) == 1 and type(pdftext_objects[0]) == PDFText:
            return pdftext_objects[0]
        
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
        return PDFText((x1, y1, x2, y2, text.strip()), page_no)
    
class PDFTextCombined(PDFText):
    
    def __init__(self, value, page_no: int = -1):
        self.objects = []
        
        if type(value) is tuple:
            PDFText.__init__(self, value, page_no)
        elif type(value) is list:
            if len(value) == 1:
                if type(value[0]) == PDFText:
                    PDFText.__init__(self, value[0].value, page_no)
                else:
                    PDFText.__init__(self, value[0], page_no)
            else:
                pdftext = PDFText.combine(value, page_no)
                PDFText.__init__(self, pdftext.value, page_no)
                self.objects = value
        else:
            raise ValueError(f'Wrong value type {value}')
    
    def __getitem__(self, index: int):
        return self.objects[index]
        
    def pop(self, index: int):
        obj = self.objects.pop(index)
        self._value = PDFText.combine(self.objects, self.page_no).value
        return obj
        
    @property
    def page_no(self) -> int:
        if self._page_no == -1 and all(map(lambda x: x.page_no==self.objects[0].page_no, self.objects)):
            return self.objects[0].page_no
        else:
            return self._page_no
        
        
    @staticmethod
    def combine(pdftext_objects: list, page_no: int = -1):
        if len(pdftext_objects) == 1 and type(pdftext_objects[0]) == PDFText:
            return pdftext_objects[0]
        return PDFTextCombined(pdftext_objects, page_no)
        
        

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
            if 0 <= self.index < len(self.pages):
                return self.pages[self.index]
            elif self.index == -1:
                return self.next_page()
            return None
        
        def get_textpage(self):
            page = self.get_page()
            if page:
                return page.get_textpage()
            return page
        
        def find_next(self, text: str, header: float = -1000000.0) -> tuple:
            
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
            # to see page page.extractText()
            while page:
                # Check for search term
                if text:
                    # Search for text in page
                    results = page.search(text)
                else:
                    # No result loop to end of document
                    results = []
                # There is still old data
                if self._last_data:
                    page_data.update(dict(sorted(self._last_data.items())))
                    self._last_data = {}
                    # In case we have a result
                    # loop over result to find next match
                    for result in results:
                        # Check if there is a match on the page
                        if result.ul.y >= page_data[list(page_data.keys())[0]][0].y:
                            key = result.ul.y + ((self.index + 1) * 1000)
                            keys = list(page_data.keys())
                            cpy_keys = keys[keys.index(key):]
                            for i in cpy_keys[1:]:
                                self._last_data[i] = page_data[i].copy()
                                del page_data[i]
                            
                            # Sort page data
                            page_data = dict(sorted(page_data.items()))
                            # return values
                            return page_data[key].copy(), page_data, self.index
                else:
                    y_old: float = -1.0
                    key: float = y_old
                    # Get words
                    for entry in page.extractWORDS():
                        pdf_text = PDFText(entry, self.index+1)
                        # Add only if not in header
                        if pdf_text.y > header:
                            # In case there is no result or the object is bigger tha the result
                            if not results or pdf_text.y <= results[0].ul.y:
                                # Store in page data
                                y_old = store_data(page_data, y_old, pdf_text)
                                key = y_old
                            else:
                                # Otherwise store for next run
                                y_old = store_data(self._last_data, y_old, pdf_text)
                    if results:
                        if key > 0:
                            # Sort page data
                            page_data = dict(sorted(page_data.items()))
                            # return values
                            return page_data[key].copy(), page_data, self.index
                        else:
                            return [], {}, self.index
                # Next step
                page = self.next_textpage()
            if text == '':
                # go to end of document
                return [], page_data, self.index
            else:
                # found nothing
                return [], {}, self.index
    
    def __init__(self, pdf_file: str = ''):
        # self._rd_index : int = 0
        self._header_pos = 0.0
        self._text_x_min: int = -1
        self._text_x_max: int = -1
        self._collection = None
        pass
    
    @property
    def text_x_range(self) -> tuple:
        return  self._text_x_min, self._text_x_max
    
    @property
    def collection(self):
        return self._collection
    
    def read_pdf(self, pdf_file: str) -> bool:
        
        # ---- File checks -----
        # use full path
        pdf_file = os.path.abspath(pdf_file)
        # Check if file exist
        if not os.path.exists(pdf_file):
            return False
        # print information
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Analyse file:')
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] {pdf_file}')
        
        # ---- Start reading -----
        # Generate local variables
        self._collection: SpecialCollection = SpecialCollection(os.path.abspath(pdf_file))
        # shortcut for pdf values
        self._pdf_values = self._collection.config.pdf_values
        
        doc = pymupdf.open(pdf_file)

        # ----- Work with reading object -----
        read_obj = self._ReadPDF(doc)
        
        # get header
        findings, page_dict, _ = read_obj.find_next(self._pdf_values.entry_cnt)
        if findings:
            self._header_pos = findings[0].y - 1.0
        
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Entry result')
        # get competition information
        findings, page_dict, _ = read_obj.find_next(self._pdf_values.judging_panel, self._header_pos)
        self._analyse_result_report(page_dict)
        
        comp_index = 0
        
        # ---- Loop over Document start with Judging panel ----
        for section_no, section in enumerate(self._collection.sections, start=1):
            
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Judging panel - Section {section_no}')
            # ----- Get Judging panel
            findings, page_dict, _ = read_obj.find_next(self._pdf_values.competition_sequenz, self._header_pos)
            self._analyse_judging_panel(page_dict, section)
            
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition sequenz - Section {section_no}')
            # ----- Get competition sequenz (find by "heat 1")
            findings, page_dict, _ = read_obj.find_next(f'{self._pdf_values.heat} 1', self._header_pos)
            left_over = self._analyse_sequenz(page_dict, section)
            
            # ----- Loop over competitions
            # Get competition list without finals
            competitions = [comp for comp in self._collection.competitions if not comp.is_final()][comp_index:]
            # loop over all without the last one
            for i in range(0, len(competitions)-1):
                print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition {str(competitions[i])}')
                # Analyse competition
                findings, page_dict, _ = read_obj.find_next(f'{self._pdf_values.competition} {competitions[i+1].no}', self._header_pos)
                self._analyse_competition(page_dict, competitions[i], left_over)
                # Clear left over
                left_over = None
            # Check for last section (must loop to en of document)
            if section_no == len(self._collection.sections):
                # Go to end of page document -> last competition
                find_str = ''
            else:
                # Next judging panel
                find_str = self._pdf_values.judging_panel
                # Set new competition start index
                comp_index += len(competitions)
            
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition {str(competitions[-1])}')
            # Analyse last completion of section (or document)
            findings, page_dict, _ = read_obj.find_next(find_str, self._header_pos)
            self._analyse_competition(page_dict, competitions[-1])
            
        return True
    
    @staticmethod
    def highlight_pdf(input_pdf: str, output_pdf: str, occurrences: list[PDFText], color: [list, tuple],
                      start_pos: [int, float] = int(7), end_pos: [int, float] = int(95), offset_px: int = 1):
        """ Add annotations to PDF by occurrences list
        :type input_pdf: str
        :param input_pdf: Input pdf file
        :type output_pdf: str
        :param output_pdf: Output pdf file
        :type occurrences: list[PDFtext]
        :param occurrences: Object list with all the occurrences to highlight
        :type color: list
        :param color: Color in rgb for the color of the annotation
        :type start_pos: [int, float]
        :param start_pos: Start (x-pos) of annotation in percent or as float (direct position)
        :type end_pos: [int, float]
        :param end_pos: End (x-pos) of annotation in percent or as float (direct position)
        :type offset_px: int
        :param offset_px: Offset in px to resize annotation
        """
        # ---- File checks -----
        # use full path
        input_pdf = os.path.abspath(input_pdf)
        # Check if file exist
        if not os.path.exists(input_pdf):
            return False
        
        # ----- Color check -----
        if type(color) is tuple:
            color = list(color)
        PDFOperations._color_check(color)

        doc = pymupdf.open(input_pdf)
        pages = list(doc.pages())
        
        width = pages[0].mediabox[2]
        
        # ----- Calculate and check position -----
        pos_x1 = PDFOperations._pos_x1_check(start_pos, width)
        pos_x2 = PDFOperations._pos_x2_check(end_pos, width)
        
        PDFOperations._add_rects(occurrences, pages, color, pos_x1, pos_x2, offset_px, 0.2)
  
        doc.save(output_pdf)
        
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Saved highlighted PDF to')
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] {output_pdf}')
        pass
    
    @staticmethod
    def highlight_pdf_clubs(input_pdf: str, output_pdf: str, clubs: list[Club], colors: list[tuple],
                            start_pos: [int, float] = int(7), end_pos: [int, float] = int(95), offset_px: int = 1):
        """ Add annotations to PDF by club occurence
        :type input_pdf: str
        :param input_pdf: Input pdf file
        :type output_pdf: str
        :param output_pdf: Output pdf file
        :type clubs: list[Club]
        :param clubs: A list of clubs which should be annotated
        :type colors: list[tuple]
        :param colors: A list of colors for the annotation color for every club
        :type start_pos: [int, float]
        :param start_pos: Start (x-pos) of annotation in percent or as float (direct position)
        :type end_pos: [int, float]
        :param end_pos: End (x-pos) of annotation in percent or as float (direct position)
        :type offset_px: int
        :param offset_px: Offset in px to resize annotation
        """
        
        # ---- File checks -----
        # use full path
        input_pdf = os.path.abspath(input_pdf)
        # Check if file exist
        if not os.path.exists(input_pdf):
            return None
        
        # ---- File checks -----
        if len(clubs) != len(colors):
            raise Exception('clubs and colors must have the same length')
        
        doc = pymupdf.open(input_pdf)
        pages = list(doc.pages())
        
        width = pages[0].mediabox[2]
        
        # ----- Calculate and check position -----
        pos_x1 = PDFOperations._pos_x1_check(start_pos, width)
        pos_x2 = PDFOperations._pos_x2_check(end_pos, width)
        
        for i in range(len(clubs)):
            color = colors[i]
            # ----- Color check -----
            if type(color) is tuple:
                color = list(color)
            PDFOperations._color_check(color)
            
            PDFOperations._add_rects(clubs[i].occurrence, pages, color, pos_x1, pos_x2, offset_px, 0.2)
        
        doc.save(output_pdf)
        
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Saved highlighted PDF to')
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] {output_pdf}')
        pass
        
            
        
    @staticmethod
    def _add_rects(occurrences: list, pages: list, color: list, start_px: float, end_px: float, offset_px: float, radius: float):
        for obj in occurrences:
            page = pages[obj.page_no - 1]
            
            # Unpack the bounding box coordinates
            x0, y0, x1, y1 = obj.bbox
            # Override x0 and x1
            x0 = start_px
            x1 = end_px
            
            # Slightly enlarge the rect to make it appear "behind" text
            rect = pymupdf.Rect(x0 - offset_px, y0 - offset_px, x1 + offset_px, y1 + offset_px)
            
            page.draw_rect(rect, color=color, fill=color, radius=radius, overlay=False)
    
    @staticmethod
    def _color_check(color: list):
        """ CHeck if the color is in correct format
        :param color: Color in RGB as list
        """
        # ----- Color check -----
        if not color:
            color = [255, 255, 0]
        # check color
        if len(color) != 3:
            raise ValueError(fr'Color is not in RGB format {color}')
        for i in range(len(color)):
            if color[i] > 255:
                color[i] = 255
            elif color[i] < 0:
                color[i] = 0
            # convert to float
            color[i] = float(color[i]) / 255
    
    @staticmethod
    def _pos_x1_check(start_pos: [int, float], width: float) -> float:
        """ Check x1 (start) position of marking
        :param start_pos: start position
        :param width: width of page
        :return: Actual x1 position (start) as float
        """
        if type(start_pos) is int:
            if start_pos < 0 or start_pos > 100:
                start_pos = 0
            # Calculate percent to float position
            return float(width) * (start_pos / 100)
        elif type(start_pos) is float:
            if start_pos < 0.0:
                start_pos = 0.0
            return start_pos
        else:
            raise TypeError('Only float or int are allowed')
    
    @staticmethod
    def _pos_x2_check(end_pos: [int, float], width: float) -> float:
        """ Check x2 (end) position of marking
        :param end_pos: start position
        :param width: width of page
        :return: Actual x2 position (pos) as float
        """
        if type(end_pos) is int:
            if end_pos < 0 or end_pos > 100:
                end_pos = 100
            # Calculate percent to float position
            return float(width) * (end_pos / 100)
        elif type(end_pos) is float:
            if end_pos > width:
                end_pos = width
            return end_pos
        else:
            raise TypeError('Only float or int are allowed')
        
    def _analyse_result_report(self, page_dict: dict):
        
        # ----- Create variables
        # Variable indicates if associations (0) should be found or clubs (1)
        parse_step: int = 0
        # shorter way to access config
        pdf_values = self._collection.config.pdf_values
        # Create an association object
        association: [Association, None] = None
        # Positon of the club in the array
        club_index: int = 0
        # Store the header line (with club in it)
        header_line: list = []
        # Get key list
        keys = list(page_dict.keys())
        
        # ----- Find club index
        # Get entry len and club position
        for key in keys:
            # Loop over list
            for i in range(len(page_dict[key])):
                if page_dict[key][i].text == pdf_values.club:
                    header_line = page_dict[key]
                    club_index = i
                    break
        # In case no header is found document wrong
        if not header_line:
            raise Exception(f'Value {pdf_values.club} not found until {" ".join([obj.text for obj in page_dict[list(page_dict.keys())[-1]]])}')
        
        # Do a debug print
        if club_index != 1:
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | Clubs are not numbered')
        else:
            print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | Clubs are numbered')
        
        # ----- Get associations and clubs
        for i, key in enumerate(keys, start=0):
            # ----- Find association
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

                if i+2 < len(keys):
                    if page_dict[keys[i+2]][club_index].text == pdf_values.club:
                        parse_step -= 1
                    else:
                        self._extract_club(page_dict[key][club_index:], header_line[club_index + 1].x, association)
                else:
                    # End loop - it has no "no. of entries" in it
                    break
        
        # ----- Create Sections
        for i, starts in enumerate(self._collection.clubs[0].starts_by_segments, start=1):
            # Create Segments
            Section(i)
        
        pass


    def _analyse_judging_panel(self, page_dict: dict, section: Section):
        
        # Get first entry
        header = page_dict[list(page_dict.keys())[0]]
        
        if len(header) != 3:
            raise Exception(f"For judging panel three vales are expected. Found {header}")
        
        page_list = self._create_table_list(page_dict, header, self._pdf_values.segment)
        
        # ----- Create judging panel
        for entry in page_list:
            # If last entry is None -> no valid judging panel entry
            if entry[-1] is None:
                continue
            # Add club
            club = self._collection.club_by_name(str(entry[2]))
            if club is not None:
                club.add_occurrence(entry[2])
            else:
                # club didn't exist
                club = self._generate_club(entry[2])
                print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Info: {club} has no athlete')
            # Add judge
            if not entry[1]:
                Judge(entry[0].text, '-', club, section)
            else:
                Judge(entry[0].text, entry[1].text, club, section)
        pass
    
    def _analyse_sequenz(self, page_dict: dict, section: Section) -> dict:
        res_dict: dict = {}
        for key, objs in page_dict.items():
            line_text = ' '.join([obj.text for obj in objs])
            competition = Competition.from_string(line_text, section)
            if competition:
                if competition.is_final():
                    print(
                        fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Found finale: Competition {competition.no}')
            else:
                res_dict[key] = objs
        return res_dict
    
    def _analyse_competition(self, page_dict: dict, competition: Competition, additional_values=None):
        
        LANE_INDEX: int = 0
        NAME_INDEX: int = 1
        YEAR_INDEX: int = 2
        CLUB_INDEX: int = 2 # Same because year will be poped from list
        TIME_INDEX: int = 3
        
        def extract_year(pdf_obj: PDFText) -> Year:
            # generate year
            year_str = pdf_obj.text
            try:
                if year_str[:4].isnumeric():
                    # Try to made int from string
                    year_no = int(year_str[:4])
                elif year_str.startswith('AK'):
                    # In case of only AK
                    year_no = int(year_str.replace('AK', '').strip())
                else:
                    year_no = 0
            except Exception as e:
                print(f'[Exception] {e}')
                # otherwise set year to 0
                year_no = 0
            # Check if year is available in collection
            result_year = self._collection.get_year(year_no)
            if not result_year:
                # In case year is not available create it
                result_year = Year(year_no)
            # Add PDF object as occurrence to year
            result_year.add_occurrence(pdf_obj)
            
            return result_year
        
        def extract_athlete(pdf_obj: PDFText, a_club: Club, a_year: Year) -> Athlete:
            # ---- Create athlete -----
            a_name = pdf_obj.text
            # In case of relay on real name is there
            if competition.is_relay():
                a_name += fr' ({competition.sex})'
            
            # Check if athlete exist
            result_athlete = None
            athletes = self._collection.athletes_by_name(a_name)
            if athletes:
                if len(athletes) > 0:
                    for a in athletes:
                        if a.club == a_club and a.year == a_year:
                            # found athlete
                            result_athlete = a
                            break
                else:
                    result_athlete = athletes[0]
            
            if not result_athlete:
                # Create Athlete
                result_athlete = Athlete(a_name, a_year, a_club)
            result_athlete.add_occurrence(pdf_obj)
            return result_athlete
        
        # find header
        header = []
        for value in page_dict.values():
            if (value[0].text == self._pdf_values.lane or value[0].text == self._pdf_values.no) and value[1].text != "0":
                header = value
                break
        
        if len(header) != 5:
            raise Exception(f"For competition five vales are expected. Found {header}")
        
        if additional_values is None:
            page_list = self._create_table_list(page_dict, header, self._pdf_values.competition)
        else:
            page_list = self._create_table_list(additional_values, header, self._pdf_values.competition)
            page_list.extend(self._create_table_list(page_dict, header, self._pdf_values.competition))
            
        # Get x min/max of page
        if self._text_x_min == -1 and page_list:
            for entry in page_list:
                if entry[LANE_INDEX].text.startswith(self._pdf_values.lane):
                    # Found x min/max
                    self._text_x_min = entry[LANE_INDEX].x
                    self._text_x_max = entry[TIME_INDEX+1].bbox[2]
                    # Break loop
                    break
        
        # create heat_zero
        heat_zero = Heat(0)
        # Still no heat found
        heat = heat_zero
        
        last_lane = 10000
        for entry in page_list:
            # Inclusive special treatment for year is short and text is center
            entry_year = entry.pop(2)
            # Wrong entry -> should not have none, go to next
            if None in entry:
                continue
            
            if entry_year is None:
                if type(entry[YEAR_INDEX]) is PDFTextCombined:
                    # Create year
                    year = extract_year(entry[NAME_INDEX][-1])
                    if year.year != 0:
                        entry[NAME_INDEX].pop(-1)
                else:
                    year = Year(0)
            else:
                # Create year
                year = extract_year(entry_year)
            
            # Create club
            club = self._generate_club(entry[CLUB_INDEX])
            # Create athlete
            athlete = extract_athlete(entry[NAME_INDEX], club, year)
            # Create time
            time = datetime.time.fromisoformat(fr'00:{entry[TIME_INDEX].text}')
            # ----- Create lane -----
            # Get lane text
            lane_str = entry[LANE_INDEX].text
            # Default: lane is not a list entry
            list_entry = False
            if self._pdf_values.lane in lane_str:
                # Get lane_no
                lane_no = int(lane_str.replace(self._pdf_values.lane, '').strip())
                # Check for next heat
                if lane_no > 0:
                    if lane_no < last_lane:
                        # Create new heat
                        heat = Heat(heat.no+1, competition)
                    # Store last lange to create new heat
                    last_lane = lane_no
            else:
                # Get lane_no
                lane_no = int(lane_str.replace('.', '').strip())
                # Lane is list entry
                list_entry = True
            
            lane = Lane(lane_no, time, athlete, heat, list_entry)
            
        # Ad heat 0 to competition if it has lanes
        if len(heat_zero.lanes) > 0:
            heat_zero.competition = competition
        else:
            heat_zero.remove()
    
    
    def _create_table_list(self, page_dict: dict, header: list, stop_cond: str) -> list:
        result: list = []
        
        # ----- Generate end points
        pts_end: list = [0]
        for entry in header[1:]:
            pts_end.append(entry.x)
        pts_end.append(100000)
        
        # ----- Loop over dictionary
        for pdf_objs in page_dict.values():
            # End loop in case stop condition matches
            if pdf_objs[0].text == stop_cond:
                break
            
            # Check if length is min the same otherwise reject value
            if len(pdf_objs) >= len(header):
                
                tmp = []
                for i in range(len(pts_end)-1):
                    tmp.append([])
                
                start = 0
                for pdf_obj in pdf_objs:
                    for i in range(start, len(pts_end)-1):
                        if pts_end[i] <= pdf_obj.x < pts_end[i+1]:
                            tmp[i].append(pdf_obj)
                            start = i
                            break
                    
                    
                for i in range(len(tmp)):
                    if tmp[i]:
                        tmp[i] = PDFTextCombined.combine(tmp[i])
                    else:
                        tmp[i] = None
                
                # if tmp is not text of position
                if tmp[0].text != header[0].text:
                    result.append(tmp)
        return result
        

    
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
        
        club_obj = PDFTextCombined.combine(text_obj_line[:i])
        
        # Create club
        club = self._generate_club(club_obj, text_obj_line[i].text, club_obj.text)
        # add association
        if association:
            club.association = association
        
        # Create participants
        participants = [int(str(text_obj_line[i+1]).replace('/', '')), int(str(text_obj_line[i+2]).replace('/', ''))]
        club.participants = Participants(participants)
        # Create segments
        for j in range(i+3, len(text_obj_line)-2, 2):
            tmp = [int(str(text_obj_line[j]).replace('/', '')), int(str(text_obj_line[j+1]).replace('/', ''))]
            club.starts_by_segments.append(Starts(tmp))
        
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
    



