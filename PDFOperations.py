import os

from Class_Clubs import *
from Class_PDFText import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno

from pypdf import PdfReader, PdfWriter, PageObject
from pypdf.generic import DictionaryObject, NameObject, ArrayObject, FloatObject

class _FileInfo:
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
    
# todo mor comments
def _remove_to_start(file_info: _FileInfo, compare_string: str, precise: bool = False):
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

def _end_or_next_section(file_info: _FileInfo, section_str: str):
    if file_info.section_no <= file_info.max_section:
        # set next find_str
        next_value = section_str
        # Set step to judging panel section 2
        file_info.step = 2
        file_info.clear_page_data()
        #todo change str
        print(fr'Verarbeite Kampfgericht - Abschnitt {file_info.section_no}')
    else:
        # Dummy value
        next_value = '#####'
        # End
        file_info.step = -1
        file_info.clear_page_data()
    return next_value

#todo add comments
def _generate_club_year(collection: SpecialCollection, text_obj: PDFText) -> tuple:
    pattern = re.compile(r'(\d{4})\s(.*)')
    match = pattern.match(text_obj.text)

    if match:
        year_str = match.group(1)
        club_str = match.group(2).strip()
    else:
        # found a relay with no year
        year_str = '0'
        club_str = text_obj.text.strip()
        
    year = _generate_year(collection, text_obj, year_str)
    club = _generate_club(collection, text_obj, '-', club_str)

    return year, club

def _generate_club(collection: SpecialCollection, text_obj: PDFText, club_id: str = '-', name: str = '') -> Club:
    # check if club in list
    club = next((x for x in collection.clubs if x.name == text_obj.text or x.name == name), None)
    if not club:
        # Create club
        if name == '':
            club = Club(text_obj.text, club_id)
        else:
            club = Club(name, club_id)
    club.add_occurrence(text_obj)
    return club

#todo add comments
def _generate_year(collection: SpecialCollection, text_obj: PDFText, year_str='') -> Year:
    if year_str == '':
        year_str = text_obj.text
    try:
        year_no = int(year_str)
    except:
        year_no = 0
    
    year = collection.get_year(year_no)
    if not year:
        year = Year(year_no)
    year.add_occurrence(text_obj)
    return year

def _create_club(collection: SpecialCollection, text_obj_line: list, association: Association, name: str = '') -> Club:
    # Create club
    club = _generate_club(collection, text_obj_line[0], text_obj_line[1].text, name)
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
    
#todo more comments
def _analyse_clubs(file_info: _FileInfo, collection: SpecialCollection, start_value: str, stop_value: str):
    pdf_values = collection.config.pdf_values
    # Create variables
    association: [Association, None] = None
    club_index: int = -1
    length: int = 0
    index: int = 0
    # Remove unused values from page
    _remove_to_start(file_info, start_value)
    # Create key list to loop over values
    keys: list = list(file_info.pages_data.keys())[:-3]
    # get correct cnt and index of club
    while index < len(keys) and club_index == -1:
        entries = file_info.pages_data[keys[index]]
        for i in range(len(entries)):
            entry = entries[i]
            if entry.text == pdf_values.club and not file_info.pages_data[keys[index - 1]][0].text.startswith(pdf_values.continue_value):
                length = len(entries)
                association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                club_index = i
                break
        index += 1
    
    if club_index != 1:
        # todo change print
        print('[Debug] Clubs are not count')
    else:
        print('[Debug] Clubs has a number')
    
    while index < len(keys):
        # Create Clubs - without number
        if club_index != 1:
            for index in range(index, len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                if len(file_info.pages_data[keys[index]]) == length:
                    _create_club(collection, text_list[club_index:], association)
                else:
                    break
        # Clubs has number and are in one line?
        else:
            for index in range(index, len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                if len(file_info.pages_data[keys[index]]) == length:
                    _create_club(collection, text_list[club_index:], association)
                elif len(file_info.pages_data[keys[index]]) == length - 1:
                    name = ' '.join(text_list[0].text.split(' ')[1:])
                    _create_club(collection, text_list, association, name)
                else:
                    break
        # Find new association
        for index in range(index, len(keys)):
            text_list: list = file_info.pages_data[keys[index]]
            if len(text_list) == length and text_list[club_index].text == pdf_values.club:
                association_str = file_info.pages_data[keys[index - 1]][0].text
                if not association_str.startswith(pdf_values.continue_value) and association_str != pdf_values.no_of_entries:
                    association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                break
            # end in case stop is reached
            elif len(text_list) == 1 and text_list[0].text.startswith(stop_value):
                index = len(keys)
                break
        
        # increment not to stop on last value
        index += 1
    
def _analyse_judging_panel(file_info: _FileInfo, collection: SpecialCollection, start_value: str, stop_value: str):
    pdf_values = collection.config.pdf_values
    # create club list
    club_list = [x.name for x in collection.clubs]
    # Remove unused values from page
    _remove_to_start(file_info, start_value)
    for entry in file_info.pages_data.values():
        if len(entry) > 1:
            if entry[len(entry) - 1].text != pdf_values.club:
                # Add club
                last = entry[len(entry) - 1]
                if last.text in club_list:
                    index = club_list.index(last.text)
                    club = collection.clubs[index]
                    club.add_occurrence(last)
                else:
                    club = _generate_club(collection, last)
                    club_list.append(club.name)
                    #todo change prinf
                    print(fr'{club} has no swimmer')
                
                judge_name = '-'
                if len(entry) == 3:
                    judge_name = entry[1].text
                # Create judge
                Judge(entry[0].text, judge_name, club, collection.sections_by_no(file_info.section_no))
        else:
            # found stop condition
            if entry[0].text.startswith(stop_value):
                break

#todo more comments
def _analyse_sequenz(file_info: _FileInfo, collection: SpecialCollection, start_value: str) -> int:
    next_competition: int = 0
    # Remove unused values from page
    _remove_to_start(file_info, start_value)
    
    for entry in file_info.pages_data.values():
        competition = Competition.from_string(entry[0].text, collection.sections_by_no(file_info.section_no))
        if competition:
            if collection.competitions.index(competition) == len(collection.competitions) - 1:
                # In case of final didn't count it has no run
                if competition.is_final():
                    # todo change string
                    print(fr'Finale Wettkampf {competition.no} gefunden')
            else:
                # get next competition which is not final
                if competition.is_final():
                    next_competition = -1
                    for comp in collection.competitions[collection.competitions.index(competition) + 1:]:
                        if not comp.is_final():
                            next_competition = comp.no
                            break
                else:
                    # Stop condition found start competition still in list
                    next_competition = competition.no
                break
    return next_competition
    
def _analyse_competition(file_info: _FileInfo, collection: SpecialCollection, competition_no: int) -> int:
    pdf_values = collection.config.pdf_values
    # active competition
    competition = collection.competition_by_no(competition_no)
    # Remove unused values from page
    _remove_to_start(file_info, competition.name(), True)
    
    # Still no heat found
    heat = None
    # create heat_zero
    heat_zero = Heat(0)
    
    for entry in file_info.pages_data.values():
        # sort by x value because of setting of pdf object sometimes random
        entry = sorted(entry, key=lambda ldb: ldb.x)
        # check for 4 or 5 values and not 4 value is club to identify a lane
        if 4 <= len(entry) <= 5 and entry[3].text != pdf_values.club:
            # Check entry length
            if len(entry) == 4:
                # In case of four club and year a one
                time_str = entry[3].text
                year, club = _generate_club_year(collection, entry[2])
            else:
                time_str = entry[4].text
                # Create year
                year = _generate_year(collection, entry[2])
                # Create club
                club = _generate_club(collection, entry[3])
            # Create athlete
            athlete_text = ' '.join(map(str, entry[1:4]))
            athlete_name = entry[1].text
            # In case of relay on real name is there
            if competition.is_relay():
                athlete_text += fr' ({competition.sex})'
                athlete_name += fr' ({competition.sex})'
            
            # Check if athlete exist
            athlete = None
            athlete_list = collection.athletes_by_name(athlete_name)
            if athlete_list:
                if len(athlete_list) > 0:
                    for a in athlete_list:
                        if a.club == club and a.year == year:
                            # found athlete
                            athlete = a
                            break
                else:
                    athlete = athlete_list[0]
            
            if not athlete:
                # Create Athlete
                athlete = Athlete(athlete_name, year, club)
            
            # Check if list ot lane
            if not heat and pdf_values.lane not in entry[0].text:
                # list entry
                lane_str = entry[0].text.replace('.', '').strip()
                # set list entry
                list_entry = True
            else:
                # list entry
                lane_str = entry[0].text.replace(pdf_values.lane, '').strip()
                # set list entry
                list_entry = False
            
            # Create lane
            lane_no = int(lane_str)
            time = datetime.time.fromisoformat(fr'00:{time_str}')
            # Create lane, will be added to collection depends on heat
            if heat:
                Lane(lane_no, time, athlete, heat, list_entry)
            else:
                Lane(lane_no, time, athlete, heat_zero, list_entry)
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

def _step_00_check_entry_result(file_info: _FileInfo, collection: SpecialCollection) -> str:
    # set next find_str
    next_value = collection.config.pdf_values.judging_panel
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # output - for info
    # todo replace print
    print(fr'Verarbeite Anzahl der Meldungen')
    return next_value

def _step_01_check_section(file_info: _FileInfo, collection: SpecialCollection) -> str:
    pdf_values = collection.config.pdf_values
    # Run function
    _analyse_clubs(file_info, collection, pdf_values.entry_cnt, pdf_values.judging_panel)
    # Set max section in competition
    file_info.max_section = len(collection.clubs[0].starts_by_segments)
    # Create sections
    for i in range(file_info.max_section):
        Section(i + 1)
    
    # set next find_str
    next_value = pdf_values.segment
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # todo change printf
    print(fr'Verarbeite Kampfgericht - Abschnitt {file_info.section_no}')
    return next_value


def _step_02_check_judging_panel(file_info: _FileInfo, collection: SpecialCollection) -> str:
    pdf_values = collection.config.pdf_values
    # call function for analysing
    _analyse_judging_panel(file_info, collection, pdf_values.judging_panel, pdf_values.segment)
    # set next find_str
    next_value = pdf_values.competition_sequenz
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # todo change print
    print(fr'Verarbeite Abschnitssdaten - Abschnitt {file_info.section_no}')
    return next_value


def _step_03_check_section_data(file_info: _FileInfo, collection: SpecialCollection) -> str:
    # set next find_str
    next_value = collection.config.pdf_values.heat + ' 1/'
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # todo change print
    print(fr'Verarbeite Wettkampffolge - Abschnitt {file_info.section_no}')
    return next_value


def _step_04_check_sequenz(file_info: _FileInfo, collection: SpecialCollection) -> str:
    pdf_values = collection.config.pdf_values
    # set competition no
    file_info.competition_no = _analyse_sequenz(file_info, collection, pdf_values.competition_sequenz)
    
    # In case this sections has only finals
    if file_info.competition_no == -1:
        # increase section number
        file_info.section_no += 1
        # end or go to next
        next_value = _end_or_next_section(file_info, pdf_values.segment)
    else:
        # Set max competition_no for this segment
        for entry in list(reversed(collection.competitions)):
            if not entry.is_final():
                file_info.max_competition = entry.no
                break
        # Increment page index not start over at heat 1
        file_info.page_index += 1
        
        # set next find_str
        next_value = pdf_values.heat + ' 1/'
        # set next step
        file_info.step += 1
        file_info.clear_page_data()
        # todo change print
        print(fr'Verarbeite Wettkampf {file_info.competition_no} ')
    return next_value


def _step_05_check_competition(file_info: _FileInfo, collection: SpecialCollection) -> str:
    file_info.competition_no = _analyse_competition(file_info, collection, file_info.competition_no)
    # Decrement page index to make sure to find the competition
    file_info.page_index -= 1
    
    if file_info.competition_no == file_info.max_competition:
        # increase section no
        file_info.section_no += 1
        if file_info.section_no <= file_info.max_section:
            # set next find_str
            next_value = collection.config.pdf_values.judging_panel
        else:
            # set next find_str - because of last entry find itself
            next_value = collection.competition_by_no(file_info.competition_no).name()
        # Do not change step
        file_info.clear_page_data()
        # todo change print
        print(fr'Verarbeite Wettkampf {file_info.competition_no} ')
    # Create next steps
    elif file_info.competition_no > file_info.max_competition:
        next_value = _end_or_next_section(file_info, collection.config.pdf_values.segment)
    else:
        # set next find_str
        next_value = collection.competition_by_no(file_info.competition_no + 1).name()
        # Do not set step but clear data
        file_info.clear_page_data()
        # todo change print
        print(fr'Verarbeite Wettkampf {file_info.competition_no} ')
    
    return next_value


_STEP_LIST: list = [
    _step_00_check_entry_result,
    _step_01_check_section,
    _step_02_check_judging_panel,
    _step_03_check_section_data,
    _step_04_check_sequenz,
    _step_05_check_competition
]

# todo name bad
def _create_pages_data(page_elements: list, file_info: _FileInfo, stop_value) -> bool:
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
    
def _analyse_steps(file_info: _FileInfo, collection: SpecialCollection) -> str:
    step = file_info.step
    next_value: str = ''
    if step < 6:
        next_value = _STEP_LIST[step](file_info, collection)
    else:
        # todo change print
        print(fr'Finished')
    return next_value

def read_pdf(pdf_file: str) -> [Collection, None]:
    # ---- File checks -----
    # use full path
    pdf_file = os.path.abspath(pdf_file)
    # Check if file exist
    if not os.path.exists(pdf_file):
        return None
    
    # ---- Start reading -----
    # Generate local variables
    collection: SpecialCollection = SpecialCollection(os.path.basename(pdf_file))
    # shortcut for pdf values
    pdf_values = collection.config.pdf_values
    # Generate class with file information
    file_info: _FileInfo = _FileInfo()
    
    # Extract pages
    pdf_pages = extract_pages(pdf_file)
    # todo replace with log class
    print(fr'Analyse file {pdf_file}')
    
    # Set next value to find
    find_next = pdf_values.entry_cnt
    # Loop through each page in the PDF
    for page_no, page_layout in enumerate(pdf_pages, start=0):
        # todo replace with log class
        # Get the current page from the PDF
        print(fr'Read page {page_no + 1:02d}')
        # Set page no
        file_info.page_no = page_no
        # Loop over data
        while True:
            # Create next page and check if another page should be read
            if _create_pages_data(list(page_layout), file_info, find_next):
                # stop "while True" loop -> continue for loop -> next page
                break
            else:
                find_next = _analyse_steps(file_info, collection)
    
    return collection


def _add_highlight_annotation(page: PageObject, pdf_text: PDFText, rgb_color: list, start_pos: float, end_pos: float, offset_px: int):
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
    
def highlight_pdf(input_pdf: str, output_pdf: str, occurrences: list[PDFText], color: list, start_perc: int = 7, end_perc: int = 95, offset_px: int = 1):
    # ---- File checks -----
    # use full path
    input_pdf = os.path.abspath(input_pdf)
    # Check if file exist
    if not os.path.exists(input_pdf):
        return None
    # ----- Color check -----
    if not color:
        color = [255, 255, 0]
    # check color
    if len(color) != 3:
        raise ValueError
    for i in range(0, len(color)):
        if color[i] > 255:
            color[i] = 255
        elif color[i] < 0:
            color[i] = 0
        # convert to float
        color[i] = float(color[i]) / 255
    # ----- Correct inputs -----
    if start_perc < 0 or start_perc > 100:
        start_perc = 0
    if end_perc < 0 or end_perc > 100:
        end_perc = 100
    if offset_px < 0:
        offset_px = 0
    
    # ----- Start reading -----
    # Read the input PDF using PyPDF2
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

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
                _add_highlight_annotation(page, occurrences[i], color, start_pos, end_pos, offset_px)
                i += 1
            else:
                break
        
        writer.add_page(page)
    
    # Write the modified PDF to the output file
    with open(output_pdf, "wb") as fp:
        writer.write(fp)
    # print(f"Found {len(occurrences)} occurrence of {search_text}.")
    print(f"Saved highlighted PDF to {output_pdf}.")
