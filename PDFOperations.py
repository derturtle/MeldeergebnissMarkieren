import os

from Class_Competition_Objects import *
from Class_PDFText import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno

from pypdf import PdfReader, PdfWriter, PageObject
from pypdf.generic import DictionaryObject, NameObject, ArrayObject, FloatObject


class _FileInfo:
    """
    Represents a file information object
    
    This objects stores infromation about the parsing of the pdf file. It locally used to share information between
    different functions
    
    Attributes:
    -----------
    page_no : int
        Actual page number
    step : int
        The parsing step
    section_no : int
        The actual section no which is parsed
    max_section : int
        The maximum count of competitions
    competition_no: int
        The actual competition number which is parsed
    max_competition : int
        The maximum competition number
    page_index : int
        Index where to start parsing
    page_data : dict
        Stores the Text objects as dictionary by it y-position
    x_start: float
        Stores x start value where text starts
    x_end: float
        Stores x end value where no text is anymore
        
    Methods:
    --------
    clear_page_data()
        Resets the stored page text information
    header_set()
        Returns if the header is set
    """
    # Default value for header
    HEADER_MAX: float = 10000.0
    # Default index for pages
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
        
        self.x_start: float = -1.0
        self.x_end: float = -1.0
    
    @property
    def page_no(self) -> int:
        """ Returns the page number
        :return: The page number
        """
        return self.__page_no
    
    @page_no.setter
    def page_no(self, value: int):
        """ Set the page number (resets page index)"""
        if self.__page_no != value:
            self.page_index = self.PAGE_INDEX_INIT
            self.__page_no = value
    
    def clear_page_data(self):
        """ Resets the stored page text information """
        self.pages_data = {}
    
    def header_set(self) -> bool:
        """ Returns if a header is found and set
        :return: Header is set
        """
        return self.page_header != self.HEADER_MAX
    
    def remove_to_start(self, compare_string: str, precise: bool = False):
        """ Removes all page information from page data until compare value is found
        :type compare_string : str
        :param compare_string: String to compare
        :type precise : bool
        :param precise: Defines it compare should be used as start with (False) or direct match (True)
        """
        # List of keys to removed
        rm_keys: list = []
        # loop over dictionary
        for key, entry in self.pages_data.items():
            # Add key to list
            rm_keys.append(key)
            # Check only if in one line only one Text object
            if len(entry) == 1:
                if not precise:
                    # Check starts with and break loop in case of match
                    if entry[0].text.startswith(compare_string):
                        break
                else:
                    # Check for a match and break loop in case of match
                    if entry[0].text == compare_string:
                        break
        # Remove all keys from dictionary
        for key in rm_keys:
            del self.pages_data[key]


def _end_or_next_section(file_info: _FileInfo, section_str: str):
    """ Checks if scanning ends or next section scanning should start
    :type file_info: _FileInfo
    :param file_info: Information object
    :type section_str: :tr
    :param section_str: Defines the next value to be searched (section)
    :return: The Next value which should be found in pdf
    """
    if file_info.section_no <= file_info.max_section:
        # set next find_str
        next_value = section_str
        # Set step to judging panel section 2
        file_info.step = 2
        file_info.clear_page_data()
        # Print information
        print(
            fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Judging panel - Section {file_info.section_no}')
    else:
        # Dummy value
        next_value = '#####'
        # End
        file_info.step = -1
        file_info.clear_page_data()
    return next_value


def _generate_club_year(collection: SpecialCollection, text_obj: PDFText) -> tuple:
    """ Generates club and year from a single object type
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type text_obj: PDFText
    :param text_obj: Object with the text
    :return:
    """
    # Create scanning pattern for regex
    pattern = re.compile(r'(\d{4})\s(.*)')
    match = pattern.match(text_obj.text)
    # In case of match
    if match:
        # Create strings for year and club
        year_str = match.group(1)
        club_str = match.group(2).strip()
    else:
        # found a relay with no year
        year_str = '0'
        club_str = text_obj.text.strip()
    # Generate year and club
    year = _generate_year(collection, text_obj, year_str)
    club = _generate_club(collection, text_obj, '-', club_str)
    return year, club


def _generate_club(collection: SpecialCollection, text_obj: PDFText, club_id: str = '-', name: str = '') -> Club:
    """ Generates a new club object (if not still available)
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type text_obj: PDFText
    :param text_obj: Object with the text
    :type club_id; str
    :param club_id: The club id
    :type name: str
    :param name: Name of the Club
    :return: A club object
    """
    # check if club in list with name and pdf text
    club = next((x for x in collection.clubs if x.name == text_obj.text or x.name == name), None)
    if not club:
        # Create club
        if name == '':
            club = Club(text_obj.text, club_id)
        else:
            club = Club(name, club_id)
    # Add PDF object as occurrence to club
    club.add_occurrence(text_obj)
    return club


def _generate_year(collection: SpecialCollection, text_obj: PDFText, year_str='') -> Year:
    """ Generates a new year object (if not still available)
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type text_obj: PDFText
    :param text_obj: Object with the text
    :type year_str: str
    :param year_str: The number of the year as string
    :return: A year object
    """
    # Check if there is no year string
    if year_str == '':
        # Set text ob text obj as year string
        year_str = text_obj.text
    try:
        # Try to made int from string
        year_no = int(year_str)
    except:
        # otherwise set year to 0
        year_no = 0
    # Check if year is available in collection
    year = collection.get_year(year_no)
    if not year:
        # In case year is not available create it
        year = Year(year_no)
    # Add PDF object as occurrence to year
    year.add_occurrence(text_obj)
    return year


def _create_club(collection: SpecialCollection, text_obj_line: list, association: Association, name: str = '') -> Club:
    """ Creates the club from a text line
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type text_obj_line: list
    :param text_obj_line: PDFtext object as list
    :type association: Association
    :param association: The club belongs to this association
    :type name: str
    :param name: Name of the Club
    :return: A club object
    """
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


def _analyse_clubs(file_info: _FileInfo, collection: SpecialCollection, start_value: str, stop_value: str):
    """ Check the listed clubs, participants and starts
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type start_value: str
    :param start_value: The value to where to start scanning
    :type stop_value: str
    :param stop_value: The end value which stops analyse
    """
    pdf_values = collection.config.pdf_values
    # Create variables
    association: [Association, None] = None
    club_index: int = -1
    length: int = 0
    index: int = 0
    # Remove unused values from page
    file_info.remove_to_start(start_value)
    # Create key list to loop over values
    keys: list = list(file_info.pages_data.keys())[:-3]
    # get correct cnt and index of club
    while index < len(keys) and club_index == -1:
        # Get the pdf line
        entries = file_info.pages_data[keys[index]]
        # loop over every entry
        for i in range(len(entries)):
            entry = entries[i]
            # Check if line has a club in it
            if entry.text == pdf_values.club and not file_info.pages_data[keys[index - 1]][0].text.startswith(
                    pdf_values.continue_value):
                length = len(entries)
                # Found association, create ir from line
                association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                # end while loop - found club index (in case of numbered clubs it is not 0)
                club_index = i
                # end for loop
                break
        index += 1
    # Do a debug print
    if club_index != 1:
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | Clubs are not numbered')
    else:
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | Clubs are numbered')
    # loop over all other clubs
    while index < len(keys):
        # Create Clubs - without number
        if club_index != 1:
            for index in range(index, len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                # Create club only length is matching
                if len(file_info.pages_data[keys[index]]) == length:
                    # Start club from string list starty by index
                    _create_club(collection, text_list[club_index:], association)
                else:
                    # end for loop
                    break
        # Clubs has number and are in one line?
        else:
            for index in range(index, len(keys)):
                text_list: list = file_info.pages_data[keys[index]]
                # No. is it own element
                if len(file_info.pages_data[keys[index]]) == length:
                    _create_club(collection, text_list[club_index:], association)
                # No. and Club name are one text
                elif len(file_info.pages_data[keys[index]]) == length - 1:
                    name = ' '.join(text_list[0].text.split(' ')[1:])
                    _create_club(collection, text_list, association, name)
                else:
                    # end for loop
                    break
        # Find new association
        for index in range(index, len(keys)):
            text_list: list = file_info.pages_data[keys[index]]
            # in case length match and club is present  in the line
            if len(text_list) == length and text_list[club_index].text == pdf_values.club:
                association_str = file_info.pages_data[keys[index - 1]][0].text
                # check if it is relly an association - check for continue value and no of entries
                if not association_str.startswith(
                        pdf_values.continue_value) and association_str != pdf_values.no_of_entries:
                    # Create association from string
                    association = Association.from_string(file_info.pages_data[keys[index - 1]][0].text)
                break
            # end in case stop is reached
            elif len(text_list) == 1 and text_list[0].text.startswith(stop_value):
                index = len(keys)
                break
        # increment not to stop on last value
        index += 1


def _analyse_judging_panel(file_info: _FileInfo, collection: SpecialCollection, start_value: str, stop_value: str):
    """ Function analyse the judging panel of the section from the competition
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type start_value: str
    :param start_value: The value to where to start scanning
    :type stop_value: str
    :param stop_value: The end value which stops analyse
    """
    pdf_values = collection.config.pdf_values
    # create club list
    club_list = [x.name for x in collection.clubs]
    # Remove unused values from page
    file_info.remove_to_start(start_value)
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
                    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Debug | {club} has no athlete')
                
                judge_name = '-'
                if len(entry) == 3:
                    judge_name = entry[1].text
                # Create judge
                Judge(entry[0].text, judge_name, club, collection.sections_by_no(file_info.section_no))
        else:
            # found stop condition
            if entry[0].text.startswith(stop_value):
                break


def _analyse_sequenz(file_info: _FileInfo, collection: SpecialCollection, start_value: str) -> int:
    """ Function analyse the competition sequenz of one section
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type start_value: str
    :param start_value: The value to where to start scanning
    :return next competition no to be analysed
    """
    next_competition: int = 0
    # Remove unused values from page
    file_info.remove_to_start(start_value)
    # loop over strings (pdf objects)
    for entry in file_info.pages_data.values():
        # Create competition
        competition = Competition.from_string(entry[0].text, collection.sections_by_no(file_info.section_no))
        if competition:
            # Check if index last one (newly created)
            if collection.competitions.index(competition) == len(collection.competitions) - 1:
                # In case of final didn't count it has no run
                if competition.is_final():
                    print(
                        fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Found finale: Competition {competition.no}')
            # Competition still exist (not newly created)
            else:
                # get next competition which is not final
                if competition.is_final():
                    # decrease next competition because final has normally nor heats
                    next_competition = -1
                    # get next competition which is not final
                    for comp in collection.competitions[collection.competitions.index(competition) + 1:]:
                        if not comp.is_final():
                            # found first which is not final -> end loop
                            next_competition = comp.no
                            break
                else:
                    # Stop condition found start competition still in list
                    next_competition = competition.no
                break
    return next_competition


def _analyse_competition(file_info: _FileInfo, collection: SpecialCollection, competition_no: int) -> int:
    """ Function analyse one competition
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :type competition_no: int
    :param competition_no: No. of competition to be analysed
    :return next competition no to be analysed
    """
    pdf_values = collection.config.pdf_values
    # active competition
    competition = collection.competition_by_no(competition_no)
    # Remove unused values from page
    file_info.remove_to_start(competition.name(), True)
    
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
            athlete.add_occurrence(entry[1])
            
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
            # Get left and right x-pos borders
            if file_info.x_start == -1.0:
                file_info.x_start = entry[0].bbox[0]
                file_info.x_end = entry[len(entry) - 1].bbox[2]
        elif len(entry) == 1:
            # in case line is not lane
            if not entry[0].text.startswith(collection.config.pdf_values.lane):
                # create new heat
                heat = Heat.from_string(entry[0].text)
                if heat:
                    if competition:
                        heat.competition = competition
                else:
                    tmp_obj = Competition.from_string(entry[0].text)
                    if tmp_obj:
                        competition = tmp_obj
                        # Also end condition - next competition
                        break
        else:
            pass
    
    # Ad heat 0 to competition if it has lanes
    if len(heat_zero.lanes) > 0:
        heat_zero.competition = competition
    else:
        heat_zero.remove()
        
    # In case there is no competition found
    if competition_no == competition.no:
        # increase return of competition no
        return competition_no + 1
    else:
        return competition.no


def _step_00_check_entry_result(file_info: _FileInfo, collection: SpecialCollection) -> str:
    """ Step 0 check entry results
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
    # set next find_str
    next_value = collection.config.pdf_values.judging_panel
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # output - for info
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Entry result')
    return next_value


def _step_01_check_section(file_info: _FileInfo, collection: SpecialCollection) -> str:
    """ Step 1 check sections, clubs, participants and starts
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
    pdf_values = collection.config.pdf_values
    # Run function
    _analyse_clubs(file_info, collection, pdf_values.entry_cnt, pdf_values.judging_panel)
    # Set max section in competition
    file_info.max_section = len(collection.clubs[0].starts_by_segments)
    # Create sections
    for i in range(file_info.max_section):
        Section(i + 1)
    
    # set next find_str
    next_value = fr'{pdf_values.segment} {file_info.section_no}'
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # output - for info
    print(
        fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Judging panel - Section {file_info.section_no}')
    return next_value


def _step_02_check_judging_panel(file_info: _FileInfo, collection: SpecialCollection) -> str:
    """ Step 2 check judging panel entries
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
    pdf_values = collection.config.pdf_values
    # call function for analysing
    _analyse_judging_panel(file_info, collection, pdf_values.judging_panel, pdf_values.segment)
    # set next find_str
    next_value = pdf_values.competition_sequenz
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # output - for info
    print(
        fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Section data - Section {file_info.section_no}')
    return next_value


def _step_03_check_section_data(file_info: _FileInfo, collection: SpecialCollection) -> str:
    """ Step 3 check section data
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
    # set next find_str
    next_value = collection.config.pdf_values.heat + ' 1/'
    # set next step
    file_info.step += 1
    file_info.clear_page_data()
    # output - for info
    print(
        fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition sequenz - Section {file_info.section_no}')
    return next_value


def _step_04_check_sequenz(file_info: _FileInfo, collection: SpecialCollection) -> str:
    """ Step 4 check competition sequenz
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
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
        # output - for info
        print(
            fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition {file_info.competition_no}')
    return next_value


def _step_05_check_competition(file_info: _FileInfo, collection: SpecialCollection) -> str:
    """ Step 5 check competitions
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
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
        # output - for info
        print(
            fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition {file_info.competition_no}')
    # Create next steps
    elif file_info.competition_no > file_info.max_competition:
        next_value = _end_or_next_section(file_info, collection.config.pdf_values.segment)
    else:
        # set next find_str
        next_value = collection.competition_by_no(file_info.competition_no + 1).name()
        # Do not set step but clear data
        file_info.clear_page_data()
        # output - for info
        print(
            fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Processing: Competition {file_info.competition_no}')
    return next_value


_STEP_LIST: list = [
    _step_00_check_entry_result,
    _step_01_check_section,
    _step_02_check_judging_panel,
    _step_03_check_section_data,
    _step_04_check_sequenz,
    _step_05_check_competition
]


def _pages_to_dict_rows(page_elements: list, file_info: _FileInfo, stop_value) -> bool:
    """ Read page data and put them into a dict list with height as key
    :type page_elements: list
    :param page_elements: PDF objects as list
    :type file_info: _FileInfo
    :param file_info: Information object
    :type stop_value: str
    :param stop_value: Stop scanning pages
    :return: Scan next page
    """
    index_found = False
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
                # Check if index wasn't found
                if not index_found:
                    # -- Check for match - to end scan
                    if index > file_info.page_index and txt_obj.text.startswith(stop_value):
                        # Match page
                        if not file_info.header_set():
                            # Get header - increase to 1 to make sure for test for <
                            file_info.page_header = txt_obj.bbox[3] + 1
                        # Set index
                        file_info.page_index = index
                        index_found = True
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
    """ Statemachine for the steps to analyse the pdf
    :type file_info: _FileInfo
    :param file_info: Information object
    :type collection: SpecialCollection
    :param collection: The collection with all objects
    :return: Next value to be searched in document
    """
    step = file_info.step
    next_value: str = ''
    if step < 6:
        next_value = _STEP_LIST[step](file_info, collection)
    else:
        # output - for info
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Finished')
    return next_value

def read_pdf(pdf_file: str) -> ([Collection, None], list):
    """ Read the pdf file
    :type pdf_file: str
    :param pdf_file: Path of the pdf file
    :return: A collection with all found objects
    """
    # ---- File checks -----
    # use full path
    pdf_file = os.path.abspath(pdf_file)
    # Check if file exist
    if not os.path.exists(pdf_file):
        return None
    
    # ---- Start reading -----
    # Generate local variables
    collection: SpecialCollection = SpecialCollection(os.path.abspath(pdf_file))
    # shortcut for pdf values
    pdf_values = collection.config.pdf_values
    # Generate class with file information
    file_info: _FileInfo = _FileInfo()
    
    # Extract pages
    pdf_pages = extract_pages(pdf_file)
    # output - Info
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Analyse file:')
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] {pdf_file}')
    
    # Set next value to find
    find_next = pdf_values.entry_cnt
    # Loop through each page in the PDF
    for page_no, page_layout in enumerate(pdf_pages, start=0):
        # Get the current page from the PDF
        print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Reading: page {page_no + 1:02d}')
        # Set page no
        file_info.page_no = page_no
        # Loop over data
        while True:
            # Create next page and check if another page should be read
            if _pages_to_dict_rows(list(page_layout), file_info, find_next):
                # stop "while True" loop -> continue for loop -> next page
                break
            else:
                find_next = _analyse_steps(file_info, collection)
    return collection, [file_info.x_start, file_info.x_end]


def _add_highlight_annotation(page: PageObject, pdf_text: PDFText, rgb_color: list, start_pos: float, end_pos: float,
                              offset_px: int):
    """ Adds a highlight annotation to a PDF page.
    :type page: PageObject
    :param page: PDF page to add the annotation to
    :type pdf_text: PDFText
    :param pdf_text: Object to be annotated
    :type rgb_color: list
    :param rgb_color: Color in rgb for the color of the annotation
    :type start_pos: float
    :param start_pos: Start (x-pos) of annotation
    :type end_pos: float
    :param end_pos: End (x-pos) of annotation
    :type offset_px: int
    :param offset_px: Offset in px to resize annotation
    """
    
    # Unpack the bounding box coordinates
    x0, y0, x1, y1 = pdf_text.bbox
    # Override x0 and x1
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
    for i in range(0, len(color)):
        if color[i] > 255:
            color[i] = 255
        elif color[i] < 0:
            color[i] = 0
        # convert to float
        color[i] = float(color[i]) / 255

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
        return None
    
    # ----- Color check -----
    if type(color) is tuple:
        color = list(color)
    _color_check(color)
    
    # ----- Start reading -----
    # Read the input PDF using PyPDF2
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    # Set variables
    page_no = 0
    page = reader.pages[page_no]
    writer.add_page(page)
    width = page.mediabox[2]
    
    # ----- Calculate and check position -----
    pos_x1 = _pos_x1_check(start_pos, width)
    pos_x2 = _pos_x2_check(end_pos, width)
    
    if offset_px < 0:
        offset_px = 0
    
    # loop over pages
    i = 0
    for page_no in range(1, reader.get_num_pages()):
        page = reader.pages[page_no]
        # loop over all occurrences
        while i < len(occurrences):
            if occurrences[i].page_no == page_no:
                # add annotation only it is on the same page
                _add_highlight_annotation(page, occurrences[i], color, pos_x1, pos_x2, offset_px)
                i += 1  # increase index
            else:
                break  # break while loop -> go to next page
        # Add page
        writer.add_page(page)
    
    # Write the modified PDF to the output file
    with open(output_pdf, "wb") as fp:
        writer.write(fp)
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Saved highlighted PDF to')
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] {output_pdf}')
    
    pass

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
    
    occ_dict: dict = {}
    
    # check colors
    for i in range(len(colors)):
        if type(colors[i]) is not list:
            colors[i] = list(colors[i])
        _color_check(colors[i])
        
        for occurrence in clubs[i].occurrence:
            occ_dict[occurrence.page_no*1000 + occurrence.y] = [occurrence, colors[i]]
            
    occ_dict = dict(sorted(occ_dict.items())) #sorted(occurrences, key = lambda x : x[0].page_no*1000 + x[0].y)
    occurrences = list(occ_dict.values())
        
    # ----- Start reading -----
    # Read the input PDF using PyPDF2
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    # Set variables
    page_no = 0
    page = reader.pages[page_no]
    writer.add_page(page)
    width = page.mediabox[2]
    
    # ----- Calculate and check position -----
    pos_x1 = _pos_x1_check(start_pos, width)
    pos_x2 = _pos_x2_check(end_pos, width)
    
    if offset_px < 0:
        offset_px = 0
    
    # loop over pages
    i = 0
    for page_no in range(1, reader.get_num_pages()):
        page = reader.pages[page_no]
        # loop over all occurrences
        while i < len(occurrences):
            if occurrences[i][0].page_no == page_no:
                # add annotation only it is on the same page
                _add_highlight_annotation(page, occurrences[i][0], occurrences[i][1], pos_x1, pos_x2, offset_px)
                i += 1  # increase index
            else:
                break  # break while loop -> go to next page
        # Add page
        writer.add_page(page)
    
    # Write the modified PDF to the output file
    with open(output_pdf, "wb") as fp:
        writer.write(fp)
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] Saved highlighted PDF to')
    print(fr'[{datetime.datetime.now().strftime("%H:%M:%S,%f")}] {output_pdf}')
    
    pass