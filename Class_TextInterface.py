import os
import sys
import glob
import curses

from enum import Enum

from Class_Config import Config
from Class_Competition_Objects import Collection
from Class_PDFOperations import PDFOperations
from CreateFileOutput import club_to_file, FileType

MENU_DEBUG: bool = False

class MenuStep(Enum):
    """An enum for menu selection"""
    SELECT_PDF = 1
    ENTER_PATH = 2
    ANALYSE_FILE = 3
    SELECT_CLUB = 4
    SELECT_COLOR = 5
    ENTER_COLOR = 6
    SUMMARY = 7
    EXIT = 8

class MenuStdout:
    """
    Represents stdout object for the curses standard screen

    Attributes:
    -----------
    max_lines: int
        No of used lines

    Methods:
    --------
    write
        Writes to the screen
    flush
        Clears the write buffer
    """
    def __init__(self, stdscr, start_row, max_lines):
        """ Initializes a new MenuStdout object
        :param stdscr: Screen object
        :param start_row: Row to start writing
        :param max_lines: No of used lines
        """
        self._index: int = 0
        self._buffer: list = []
        self._max_lines: int = 0
        
        self.stdscr = stdscr
        self.start_row = start_row
        self.max_lines = max_lines
    
    @property
    def max_lines(self) -> int:
        """ Returns the number of used lines
        :return: No of used lines
        """
        return  self._max_lines
    
    @max_lines.setter
    def max_lines(self, value: int):
        """ Set a new number fo write lines and clear the write buffer """
        self._max_lines = value
        self.flush()
        
    def write(self, text: str):
        """ Function writes to the screen
        :param text: Test to write
        """
        # If newline in text split line and loop over split
        for split in text.split('\n'):
            # In case it is not empty
            if split:
                # Add text and clear all other characters form line
                split = split + ' ' * (self.stdscr.getmaxyx()[1] - len(split))
                # Check if index is max
                if self._index == self._max_lines:
                    # remove first from buffer and add new string to it
                    self._buffer.remove(self._buffer[0])
                    self._buffer.append(split)
                else:
                    # Add to buffer and incremnet index
                    self._buffer[self._index] = split
                    self._index += 1
        # loop over buffer an write to screen
        for row, text in enumerate(self._buffer, start=self.start_row):
            self.stdscr.addstr(row, 0, text)
        # update screen
        self.stdscr.refresh()
        
    def flush(self):
        """ Clear write buffer """
        self._index = 0
        self._buffer = [''] * self._max_lines
        
class Key:
    """ Represents a Key class """
    KEY_CTRL: int = 96          # ctrl
    KEY_ESC: int = 27           # esc
    KEY_RETURN : int = 10       # return
    KEY_SPACE: int = 32         # space
    
class KeyLists(Key):
    """ Represents a key list class """
    LIST_EXIT: list = [ord('x') - Key.KEY_CTRL, ord('X') - Key.KEY_CTRL]
    LIST_BACK: list = [ord('b') - Key.KEY_CTRL, ord('B') - Key.KEY_CTRL, Key.KEY_ESC]
    LIST_CHG_DIR : list = [ord('d') - Key.KEY_CTRL, ord('D') - Key.KEY_CTRL]
    LIST_CHG_COLOR: list = [ord('o') - Key.KEY_CTRL, ord('o') - Key.KEY_CTRL]
    LIST_PREV_PAGE: list = [ord('p') - Key.KEY_CTRL, ord('P') - Key.KEY_CTRL, curses.KEY_PPAGE, curses.KEY_PREVIOUS]
    LIST_NEXT_PAGE: list = [ord('n') - Key.KEY_CTRL, ord('N') - Key.KEY_CTRL, curses.KEY_NPAGE, curses.KEY_NEXT]
    LIST_OKAY: list = [curses.KEY_ENTER, Key.KEY_RETURN]

class MenuEntry:
    """ Represents a Menu entry object """
    def __init__(self, pos: int, text: str, shortcut: str, keys: list):
        """ Initializes a new MenuEntry object
        :param pos: Position in Menu
        :param text: Text which is shown
        :param shortcut: The key-shortcut which is displayed
        :param keys: List of valid keys
        """
        self.pos: int = pos
        self.text: str = text
        self.shortcut: str = shortcut
        self.keys: list = keys
        pass
    
    def __str__(self):
        return fr'^{self.shortcut} {self.text}'
        
class BottomMenu:
    """ Represents bottom menu class """
    EXIT: MenuEntry = MenuEntry(0, 'Exit', '^X', KeyLists.LIST_EXIT)
    BACK: MenuEntry = MenuEntry(1, 'Back', '^B', KeyLists.LIST_BACK)
    CHG_DIR: MenuEntry = MenuEntry(2, 'Change dir', '^D', KeyLists.LIST_CHG_DIR)
    CHG_COLOR: MenuEntry = MenuEntry(2, 'Add color', '^O', KeyLists.LIST_CHG_COLOR)
    PREV_PAGE: MenuEntry = MenuEntry(3, 'Prev page', '^P', KeyLists.LIST_PREV_PAGE)
    NEXT_PAGE: MenuEntry = MenuEntry(4, 'Next page', '^N', KeyLists.LIST_NEXT_PAGE)

class HasScreen:
    """
    Represents a class which has a screen object
    
    Attributes:
    -----------
    stdscr
        Value for the stdscr
    y_max: int
        Max rows of the screen
    x_max: int
        Max characters to display
        
    Methods:
    --------
    update
        Updates the screen object
    """
    def __init__(self, stdscr):
        """ Initializes a new HasScreen object
        :param stdscr: Screen object
        """
        self._stdscr = stdscr
        self._y_max = 0
        self._x_max = 0
        self.update()
        
    @property
    def stdscr(self):
        """ Returns the screen object
        :return: The screen object
        """
        return self._stdscr
    
    @property
    def y_max(self) -> int:
        """ Returns the maximum count of rows for the screen
        :return: Maximum count of rows
        """
        return self._y_max

    @property
    def x_max(self) -> int:
        """ Returns the maximum signs which could be displayed in one row
        :return: Maximum signs of one row
        """
        return self._x_max
    
    def update(self, stdscr = None):
        """ Update the screen object
        :param stdscr: A new screen object
        """
        if stdscr is not None:
            self._stdscr = stdscr
        # get new y and x max values
        self._y_max, self._x_max = self.stdscr.getmaxyx()

class DrawBase(HasScreen):
    """
    Represents a basic draw class
    
    Methods:
    --------
    draw_sel_str
        Draws a selected string
    draw_head
        Draws a header for the screen
    """
    def __init__(self, stdscr):
        """ Initializes a new DrawBase object
        :param stdscr: Screen object
        """
        HasScreen.__init__(self, stdscr)
        
    def draw_sel_str(self, row: int, col: int, text: str, selected: bool):
        """ Draws a selected string to the screen (inverted text)
        :param row: Row to write to
        :param col: Position in row
        :param text: Test to display
        :param selected: If it is selected ot not
        """
        # Draws if it is selected
        if selected:
            # Invert screen ON
            self.stdscr.attron(curses.A_REVERSE)
        # Draw
        self.stdscr.addstr(row, col, text)
        # Invert screen OFF
        self.stdscr.attroff(curses.A_REVERSE)

            
    def draw_head(self, strings: list):
        """ Draws a header
        :param strings: Expects a list of 3 string which generates the header two lines and first line of text
        """
        self.stdscr.addstr(0, 0, strings[0], curses.A_BOLD)
        self.stdscr.addstr(1, 0, strings[1], curses.A_ITALIC)
        self.stdscr.addstr(3, 0, strings[2])
  

class TwoColumnList(DrawBase):
    """
    Represents a two colum Menu class
    
    Attributes:
    -----------
    act_value : str
        The actual selected value
    selected_idx : int
        The actual selected index
    last_row : int
        The last row on which was drawn
    next_row : int
        The next row which is not used
    entries_drawn : int
        The entries on the Screen
    entry_cnt : int
        The count of entries on the screen
    entry_max : int
        The maximum entries which could be drawn
    is_drawn : bool
        If it was drawn (once)
    row_start : int
        The row where the drawings starts
    row_end : int
        The row where the drawings stop
    next_page : bool
        If a next page is available
    prev_page : bool
        If a previous page is available
    default_search : bool
        If a default value should be selected
    default_string : str
        The default value
    values : list
        The list of values to be displayed
    default_end : str
        In case a value exceeds site, the default ending
    
    Methods:
    --------
    draw: int
        Draws the two columns
    draw_next: int
        Draws the next page
    draw_previous: int
        Draws the previous page
    refresh
        Update the drawing area
    eval_arrows_keys : int
        Evaluate if an arrow key is pressed
    """
    
    def __init__(self, stdscr, values, start_row: int=0, end_row: int = 0, default_end: str = ''):
        """ Initializes a new DrawBase object
        :param stdscr: Screen object
        :param values: Values to display
        :param start_row: Row to start the list
        :param end_row: Row where the list should end display
        :param default_end: In case an entry is too long this is the default ending
        """
        # Inti base
        DrawBase.__init__(self, stdscr)
        # Init protected attributes
        self._row_start: int = 0
        self._row_end: int = self.y_max
        
        self._entry_start: int = 0
        self._entry_end: int = -1
        self._last_row: int = 0
        self._elements: list = []
        self._selected_idx: int = 0
        
        self._drawn = False
        # Init with parameters
        self.values = values
        self.default_end = default_end
        self.row_start = start_row
        self.row_end = end_row
        self.default_search: bool = True
        self.default_string: str = ''
    
    @property
    def act_value(self) -> str:
        """ Returns the actual selected value
        :return: Selected (string) value
        """
        # Check if it was drawn
        if self.is_drawn:
            # Check if something is selected
            if self.selected_idx < len(self.values[self._entry_start:]):
                # Return value
                return self.values[self._entry_start:][self.selected_idx]
        return ''
        
    @property
    def selected_idx(self) -> int:
        """ Returns the selected index
        :return: The selected index
        """
        return self._selected_idx
        
    @property
    def last_row(self) -> int:
        """ Retruns the last row on which was written
        :return: The last row on which was written
        """
        return self._last_row
    
    @property
    def next_row(self) -> int:
        """ Returns the next (empty, not used) row
        :return: The next no used row
        """
        return self._last_row + 1
    
    @property
    def entries_drawn(self) -> list:
        """ Returns the entries which are actually displayed
        :return: The entries list which appear on the screen
        """
        return self.values[self._entry_start:self._entry_start+self._entry_end]
    
    @property
    def entry_cnt(self) -> int:
        """ Returns the count of the entries which are drawn
        :return: Count of entries draws
        """
        return self._entry_end - self._entry_start + 1
        
    @property
    def entry_max(self) -> int:
        """ Returns the max entries which could be displayed
        :return: Max entries which could be displayed
        """
        return (self.row_end - self.row_start - 1) * 2
        
    @property
    def is_drawn(self) -> bool:
        """ Returns if it was drawn (once)
        :return: Was drawn (once)
        """
        return self._drawn
        
    @property
    def row_start(self) -> int:
        """ Returns the start row of drawing
        :return: The start row of drawing
        """
        return self._row_start
    
    @row_start.setter
    def row_start(self, value: int):
        """ Sets the start row of drawing
        :param value: No of row
        """
        if type(value) is int:
            if 0 <= value <= self.y_max:
                self._row_start = value
                return
            
        raise ValueError
    
    @property
    def row_end(self) -> int:
        """ Returns the end row of drawing
        :return: The end row of drawing
        """
        return self._row_end
    
    @row_end.setter
    def row_end(self, value: int):
        """ Sets the end row of drawing
        :param value: No of row
        """
        if type(value) is int:
            if 1 <= value <= self.y_max:
                self._row_end = value
                return
            elif ((self.y_max-1) * -1) <= value <= 0:
                self._row_end = self.y_max + value
                return
            
        raise ValueError
        
    def draw(self, selected_idx: int=0, entry_idx = 0) -> int:
        """ Draws the two column list
        :param selected_idx: Index which is selected
        :param entry_idx: Start index of page
        :return: The new selected index
        """
        # update screen data
        self.update()
        # Check if a default value is set
        if not self.is_drawn and self.default_search and self.default_string != '':
            if self.default_string in self.values:
                # Get index of default string
                index = self.values.index(self.default_string)
                # Check on which page index is
                entry_idx = int(index / self.entry_max) * self.entry_max
                # Set selected idx
                selected_idx = index - entry_idx
        
        # generate full end string
        end_string = fr'[..]{self.default_end}'
        
        # Calculate start and stop of columns
        col_start = [1, int(self.x_max / 2) + 1]
        col_end = [int(self.x_max / 2) - 1, int(self.x_max / 2) * 2 - 1]
        col_len = col_end[0] - col_start[0]
        
        # Check that index is not out of bound
        if selected_idx > len(self.values[entry_idx:])-1:
            # Store selected_idx
            self._selected_idx = 0
        else:
            # Store selected_idx
            self._selected_idx = selected_idx
        
        # Set actual row
        self._last_row = self.row_start
        
        self._elements = []
        idx = -1
        if self.values:
            # Store start entry
            self._entry_start = entry_idx
            # loop over every index
            for value in self.values[entry_idx:]:
                # increase index
                idx += 1
                # Calculate position left (0) or right (1)
                pos: int = idx % 2
                # trim value if necessary
                if len(value) > col_len:
                    value = value[0:col_len - len(end_string)] + end_string
                # draw value check if selected
                self.draw_sel_str(self._last_row, col_start[pos], value, idx == self._selected_idx)
                self._elements.append([self._last_row, col_start[pos], value])
                # if position is right
                if pos == 1:
                    # increase row count
                    self._last_row += 1
                    # check if row reached end
                    if self.next_row == self.row_end:
                        break

            # Store entry end
            self._entry_end = self._entry_start + idx
            
            # return -1 in case all values where drawn
            if idx >= len(self.values) - 1:
                idx = -1
            
            self._drawn = True
        else:
            # Add error message
            self.stdscr.addstr(self._last_row, col_start[0], 'Nothing found')
            self._elements.append([self._last_row, col_start[0], 'Nothing found'])
        return idx
    
    @property
    def next_page(self) -> bool:
        """ Returns if next page is available
        :return: Next page available
        """
        if self.is_drawn:
            if self._entry_end + 1 < len(self.values):
                return True
        return False
    
    def draw_next(self, selected_idx: int=0):
        """ Draws the next page
        :param selected_idx: The selected idx on the next page
        :return: New selected idx
        """
        if self._entry_end + 1 < len(self.values):
            return self.draw(selected_idx, self._entry_end+1)
        else:
            self.refresh(selected_idx)
            return -1
            
    def _calc_prev_page_index(self) -> int:
        return self._entry_start - self.entry_max
    
    @property
    def prev_page(self) -> bool:
        """ Returns if previous page is available
        :return: Previous page available
        """
        if self.is_drawn:
            if self._calc_prev_page_index() >= 0:
                return True
        return False
        
    def draw_previous(self, selected_idx: int=0):
        """ Draws the previous page
        :param selected_idx: The selected idx on the previous page
        :return: New selected idx
        """
        prev_page_index = self._calc_prev_page_index()
        if prev_page_index >= 0:
            return self.draw(selected_idx, prev_page_index)
        else:
            self.refresh(selected_idx)
            return -1
    
    
    def refresh(self, selected_idx):
        """ Refresh the screen
        :param selected_idx: New selected index
        """
        self.update()
        if self.is_drawn:
            if self._selected_idx != selected_idx:
                # Old index not highlighted
                self.draw_sel_str(self._elements[self._selected_idx][0], self._elements[self._selected_idx][1], self._elements[self._selected_idx][2], False)
                # New index highlighted
                self.draw_sel_str(self._elements[selected_idx][0], self._elements[selected_idx][1], self._elements[selected_idx][2], True)
                # set new selection
                self._selected_idx = selected_idx
            self.stdscr.refresh()
        
    def eval_arrows_keys(self, key) -> int:
        """ Evaluate the arrow keys press
        :param key: Arrow key press
        :return: New selected index
        """
        new_idx = self.selected_idx
        
        # only one entry
        if (self.entry_cnt-1) == 0:
            return new_idx
        
        # Min 2. entries
        if key == curses.KEY_UP:
            # Check for first row left
            if self.selected_idx == 0:
                if (self.entry_cnt-1) >= 2:
                    new_idx = (self.entry_cnt-1) - ((self.entry_cnt-1) + 1) % 2
            # Check for first row right
            elif self.selected_idx == 1:
                if (self.entry_cnt-1) >= 3:
                    new_idx = (self.entry_cnt-1) - 1 + ((self.entry_cnt-1) + 1) % 2
            else:
                new_idx = self.selected_idx - 2
        elif key == curses.KEY_DOWN:
            if self.selected_idx == (self.entry_cnt-1) - 1:
                new_idx = 1 - ((self.entry_cnt-1) + 1) % 2
            elif self.selected_idx == (self.entry_cnt-1):
                new_idx = ((self.entry_cnt-1) + 1) % 2
            else:
                new_idx = self.selected_idx + 2
        elif key == curses.KEY_LEFT:
            if self.selected_idx == (self.entry_cnt-1) and ((self.entry_cnt-1) + 1) % 2 == 1:
                # do nothing
                pass
            # elif act_idx == 0:
            #     new_idx = 1
            # even
            elif self.selected_idx % 2 == 0:
                new_idx = self.selected_idx + 1
            # odd
            else:
                new_idx = self.selected_idx - 1
        elif key == curses.KEY_RIGHT:
            if self.selected_idx == (self.entry_cnt-1) and ((self.entry_cnt-1) + 1) % 2 == 1:
                # do nothing
                pass
            # elif act_idx == 1:
            #     new_idx = 0
            # even
            elif self.selected_idx % 2 == 0:
                new_idx = self.selected_idx + 1
            # odd
            else:
                new_idx = self.selected_idx - 1
        else:
            pass
        
        return new_idx


class TextInterface:
    """
    Represents an object which runs the Text interface

    Attributes:
    -----------
    stdscr:
        Value for the stdscr
    config: Config
        Configuration to read and write to

    Methods:
    --------
    hmi : list
        Starts the human machine interface
    """
    __OKAY : str = '<< Okay >>'
    __ENTRY_ALL: str = '* All *'
    
    def __init__(self):
        self.stdscr = None
        self.config: [Config, None] = None
        # Base class for base functions of screen
        self._base: [DrawBase, None]
        # path variables
        self._pdf_file = ''
        self._default_path = ''
        # output of pdf read
        self._collection : [Collection, None] = None
        self._borders : list = []
        # values stored out of pdf
        self._sel_no: int = 0
        self._clubs: list = []
        self._colors: list = []
        # Initialize the steps as an ordered list of methods
        self._steps = {
            MenuStep.SELECT_PDF:   self._menu_select_pdf,
            MenuStep.ENTER_PATH:   self._menu_enter_path,
            MenuStep.ANALYSE_FILE: self._menu_analyse_file,
            MenuStep.SELECT_CLUB:  self._menu_select_club,
            MenuStep.SELECT_COLOR: self._menu_select_color,
            MenuStep.ENTER_COLOR:  self._menu_enter_color,
            MenuStep.SUMMARY:      self._menu_summery
        }

    
    def hmi(self, config: Config = None):
        """ Run the hmi
        :param config: Used config file
        """
        # Check config
        if config:
            # Sets config
            self.config = config
        else:
            # Create new config
            self.config = Config()
        # Set default path
        self._default_path = os.path.expanduser('~/Downloads/')
        if not os.path.isdir(self._default_path):
            self._default_path = os.path.expanduser('~')
        # Start wrapper
        curses.wrapper(self._menu_main)
    
    def _menu_main(self, stdscr):
        """Main menu function that steps through the various menus."""
        # init base
        self._base = DrawBase(stdscr)
        # Store screen object
        self.stdscr = stdscr
        # Start with the first step
        current_step = MenuStep.SELECT_PDF
        while current_step != MenuStep.EXIT:
            # call step function
            current_step = self._steps[current_step]()
    
    def _menu_enter_path(self) -> MenuStep:
        """ Menu to change the search path
        :return: The next menu step which should be displayed
        """
        # Display menu on screen
        key = self._display_path_dialog()
        # ----- evaluate keys -----
        # Exit keys
        if key in BottomMenu.EXIT.keys:
            # End Menu
            return MenuStep.EXIT
        else:
            # Next menu choose pdf file
            return MenuStep.SELECT_PDF
    
    def _menu_enter_color(self) -> MenuStep:
        """ Menu to enter a new color
        :return: The next menu step which should be displayed
        """
        # Display color dialog on screen
        key = self._display_new_color_dialog()
        # ----- evaluate keys -----
        # Exit keys
        if key in BottomMenu.EXIT.keys:
            # End Menu
            return MenuStep.EXIT
        else:
            # Next menu choose color
            return MenuStep.SELECT_COLOR
    
    def _menu_analyse_file(self) -> MenuStep:
        """ Menu displays only that the file is analysed
        :return: The next menu step which should be displayed
        """
        # in case there is still data
        if self._collection:
            # and the data is from the same file
            if self._collection.name == self._pdf_file:
                # go direct to choose club
                return MenuStep.SELECT_CLUB
        # Shorten actual file if necessary
        act_file = self._shorten_file(self._pdf_file, self._base.x_max - 4)
        # Clear screen
        self.stdscr.clear()
        # Draw heading of screen
        self._base.draw_head(["Reading PDF file", f"({act_file})", "Please wait"])
        # Generate stdout for menu
        local_out = MenuStdout(self.stdscr, 5, 15)
        # Override stdout
        sys.stdout = local_out
        # Read pdf-file
        pdf_obj = PDFOperations()
        # Read pdf
        if not pdf_obj.read_pdf(self._pdf_file):
            # Clear screen again
            self.stdscr.clear()
            # No valid data found
            self._base.draw_head(
                ["Reading PDF file", f"({self._pdf_file})", "Reading failed, Esc to go back and select other file"])
            # Draw bottom menu
            self._draw_menu(end=True, back=True)
            # Wait for key
            key = self.stdscr.getch()
            # ----- evaluate keys -----
            # Back key
            if key in BottomMenu.BACK.keys:
                # Next menu choose pdf
                return MenuStep.SELECT_PDF
            # Exit keys
            elif key in BottomMenu.EXIT.keys:
                # End Menu
                return MenuStep.EXIT
        else:
            # Store collection and the borders
            self._collection = pdf_obj.collection
            self._border = pdf_obj.text_x_range
        # Next menu select club
        return MenuStep.SELECT_CLUB
            
    def _menu_select_pdf(self) -> MenuStep:
        """ Menu to choose a pdf file
        :return: The next menu step which should be displayed
        """
        filetype = '.pdf'
        # Get search path
        if 'search_path' in list(self.config.default.keys()):
            # Take search path from config if available
            act_path = os.path.abspath(self.config.default['search_path'])
        else:
            # Take default search path
            act_path = os.path.abspath(self._default_path)
        # In case path is no dir
        if not os.path.isdir(act_path):
            # Go to select path
            return MenuStep.ENTER_PATH
            
        # search pdf files
        pdf_files = glob.glob(fr'{act_path}/*{filetype}')
        # Create list of files (basename)
        if pdf_files:
            pdf_files = list(map(os.path.basename, pdf_files))
            pdf_files.sort() # sort files
        # Create header
        header = ["Choose your PDF file:", f"({act_path})", '']
        # Create menu class
        two_column_pdf = TwoColumnList(self.stdscr, pdf_files, 3, -2, filetype)
        # Display menu
        key = self._display_two_columns(two_column_pdf, header, True, False, True, False)
        #----- evaluate keys -----
        # Change dir key
        if key in BottomMenu.CHG_DIR.keys:
            # store act path
            self.config.default['search_path'] = act_path
            # Next menu enter a new path
            return MenuStep.ENTER_PATH
        # Enter key
        elif key in KeyLists.LIST_OKAY:
            # Create pdf file (full path)
            self._pdf_file = os.path.abspath(act_path + '/' + two_column_pdf.act_value)
            # Next menu analyse pdf file
            return MenuStep.ANALYSE_FILE
        else:
            # End Menu
            return MenuStep.EXIT

    def _menu_select_club(self) -> MenuStep:
        """ Menu to select a club from the pdf file
        :return: The next menu step which should be displayed
        """
        # Shorten actual file if necessary
        act_file = self._shorten_file(self._pdf_file, self._base.x_max - 4)
        # Generate a list with club names
        club_names = list(map(lambda x: x.name, self._collection.clubs))
        # In case list is not empty
        if club_names:
            # Sort names
            club_names.sort()
            if self._sel_no == 0:
                # In case there is no club selected add ALL to list
                club_names.insert(0, self.__ENTRY_ALL)
            else:
                # If there is a club still selected
                for club in self._clubs:
                    # remove it from list
                    club_names.remove(club)
        # Create header
        header = ["Found following Clubs:", f"({act_file})", '']
        # Create menu class
        two_column_club = TwoColumnList(self.stdscr, club_names,3,-2, '')
        # Create entry for config file
        if self._sel_no == 0:
            # In case it is the first one default is 'club'
            entry = 'club'
        else:
            # Otherwise it is 'club_<No>'
            entry = fr'club_{self._sel_no+1:02d}'
        # Check if entry exist
        if entry in self.config.default.keys():
            # Set default entry
            two_column_club.default_string = self.config.default[entry]
        # Display menu
        key = self._display_two_columns(two_column_club, header, True, True, False, False)
        # ----- evaluate keys -----
        # Back key
        if key in BottomMenu.BACK.keys:
            if self._sel_no == 0:
                # Next menu choose pdf
                return MenuStep.SELECT_PDF
            else:
                # Remove from list last index from lists
                if len(self._clubs) == self._sel_no + 1:
                    self._clubs.pop(self._sel_no)
                if len(self._colors) == self._sel_no + 1:
                    self._colors.pop(self._sel_no)
                # Decrement index
                self._sel_no -= 1
                return MenuStep.SUMMARY
        # Enter keys
        elif key in KeyLists.LIST_OKAY:
            # Store club
            if len(self._clubs) <= self._sel_no:
                self._clubs.append(two_column_club.act_value)
            else:
                self._clubs[self._sel_no] = two_column_club.act_value
            # Next menu select color
            return MenuStep.SELECT_COLOR
        else:
            # End menu
            return MenuStep.EXIT
        
    def _menu_select_color(self) -> MenuStep:
        """ Menu to select a club how to highlight pdf
        :return: The next menu step which should be displayed
        """
        # init variables
        index: int = -1
        default_str: str = ''
        # Create entry for config file
        if self._sel_no == 0:
            # In case it is the first one default is 'color'
            entry = 'color'
        else:
            # Otherwise it is 'color_<No>'
            entry = fr'color_{self._sel_no + 1:02d}'
        # Check if entry exist
        if entry in self.config.default.keys():
            # Check if entry in color list
            if self.config.default[entry] in list(self.config.colors.hex.keys()):
                # Get index of entry
                index = list(self.config.colors.hex.keys()).index(self.config.default[entry])
        # Create color list
        color_list = list(map(lambda x: fr'[{x[1].upper()}] {x[0]}', self.config.colors.hex.items()))
        if index >= 0:
            # Store default string
            default_str = color_list[index]
        # Sort list
        color_list.sort()
        # Create menu class
        two_column_color = TwoColumnList(self.stdscr, color_list, 3, -2, '')
        # Set default string (if exits)
        two_column_color.default_string = default_str
        # Create header
        header = [f'Select your color for marking', f'({self._clubs[self._sel_no]})', '']
        # Display menu
        key = self._display_two_columns(two_column_color, header, True, True, False, True)
        # ----- evaluate keys -----
        # Back key
        if key in BottomMenu.BACK.keys:
            # Next menu is select club
            return MenuStep.SELECT_CLUB
        # Change color key
        elif key in BottomMenu.CHG_COLOR.keys:
            # Next menu is to enter a new color
            return MenuStep.ENTER_COLOR
        # Okay keys
        elif key in KeyLists.LIST_OKAY:
            # Get color form selected value
            color = two_column_color.act_value.split(']')[1].strip()
            # Store color
            if len(self._colors) <= self._sel_no:
                self._colors.append(color)
            else:
                self._colors[self._sel_no] = color
            return MenuStep.SUMMARY
        else:
            return MenuStep.EXIT
        
    def _menu_summery(self) -> MenuStep:
        """ Last menu with a summery
        :return: The next menu step which should be displayed
        """
        # Shorten actual file if necessary
        act_file = self._shorten_file(self._pdf_file, self._base.x_max - len('Output: '))
        # Check if onyl one club is selected
        if self._sel_no == 0:
            # If only one club selected
            if self._clubs[0] != self.__ENTRY_ALL:
                # Generate output file with name of club
                output_file = fr'Output: {act_file[:-4]}_{self._clubs[0]}.pdf'
            else:
                # Generate output file with placeholder
                output_file = fr'Output: {act_file[:-4]}_<club_name>>.pdf'
        else:
            # Set to marked with the number of clubs
            output_file = fr'Output: {act_file}_marked_{self._sel_no+1:02d}.pdf'
        # Generate a club list to display
        club_list: list = []
        for i in range(self._sel_no+1):
            club_list.append(fr' {self._clubs[i]} ({self._colors[i]})')
        # Create menu points
        if self._sel_no + 1 >= 10 or self._clubs[0] == self.__ENTRY_ALL:
            # Only okay
            menus = [self.__OKAY]
        else:
            # Okay and new selection
            menus = [self.__OKAY, 'Add club for selection']
        # Create header
        if self._sel_no == 0:
            # Single club
            header = ['Summery', output_file, '\n' + club_list[0]]
        else:
            # More clubs
            header = ['Summery', output_file, '\n'+'\n'.join(club_list)]
        # Create menu class
        two_column_summery = TwoColumnList(self.stdscr, menus, 15, -2, '')
        # Display menu
        key = self._display_two_columns(two_column_summery, header, True, True)
        # ----- evaluate keys -----
        # Back key
        if key in BottomMenu.BACK.keys:
            # Next menu color select
            return MenuStep.ENTER_COLOR
        # Oky keys
        elif key in KeyLists.LIST_OKAY:
            # In case okay is selected
            if two_column_summery.act_value == self.__OKAY:
                # Create stdout for screen
                local_out = MenuStdout(self.stdscr, 17, 4)
                # Override stdout
                sys.stdout = local_out
                # Generate files
                self._gen_files_and_update_config()
                # Set stdout to default one
                sys.stdout = sys.__stdout__
                # End Menu
                return MenuStep.EXIT
            else:
                # Increment counter
                self._sel_no += 1
                # Next menu select club
                return MenuStep.SELECT_CLUB
        else:
            # End menu
            return MenuStep.EXIT
    
    def _gen_files_and_update_config(self):
        """Generates all output files for the menu"""
        output_file = ''
        # Check if mark start in config
        if 'mark_start' in list(self.config.default.keys()):
            # set start value
            self._border[0] = self.config.default['mark_start']
        # Check if mark start in config
        if 'mark_end' in list(self.config.default.keys()):
            # set end value
            self._border[1] = self.config.default['mark_end']
        # Check if all clubs should be created
        if self._clubs[0] == self.__ENTRY_ALL:
            # Get color
            color = self.config.colors.rgb[self._colors[0]]
            # Loop over clubs
            for club in self._collection.clubs:
                # Create output file name
                output_file = self._gen_output_file(os.path.dirname(self._pdf_file),
                                                    os.path.basename(self._pdf_file)[:-4] + '_' + club.name)
                # Highlight pdf
                PDFOperations.highlight_pdf(self._pdf_file, output_file, club.occurrence, color,
                                            self._border[0], self._border[1], int(self.config.default['offset']))
                # Create other output
                club_to_file(output_file[:-4] + '.md', club, FileType.MARKDOWN)
                club_to_file(output_file[:-4] + '.html', club, FileType.HTML)
        # Only one or up to 10 should be created
        else:
            # Init lists
            clubs: list = []
            colors: list = []
            # Loop over range of selected clubs
            for i in range(len(self._clubs)):
                # Add to club and color list
                clubs.append(self._collection.club_by_name(self._clubs[i]))
                colors.append(self.config.colors.rgb[self._colors[i]])
                # Set new config values
                if i > 0:
                    self.config.default[fr'color_{i + 1:02d}'] = self._colors[i]
                    self.config.default[fr'club_{i + 1:02d}'] = self._clubs[i]
                else:
                    self.config.default['color'] = self._colors[i]
                    self.config.default['club'] = self._clubs[i]
                # Create output file name
                output_file = self._gen_output_file(os.path.dirname(self._pdf_file),
                                                    os.path.basename(self._pdf_file)[:-4] + '_' + clubs[i].name)
                # Create other output
                club_to_file(output_file[:-4] + '.md', clubs[i], FileType.MARKDOWN)
                club_to_file(output_file[:-4] + '.html', clubs[i], FileType.HTML)
            # In case of single club
            if self._sel_no != 0:
                # Create output file name
                output_file = self._gen_output_file(os.path.dirname(self._pdf_file), os.path.basename(self._pdf_file)[:-4] + '_' + fr'_marked_{self._sel_no + 1:02d}')
            # Highlight pdf
            PDFOperations.highlight_pdf_clubs(self._pdf_file, output_file, clubs, colors,
                                              self._border[0], self._border[1], int(self.config.default['offset']))
        # Store path in config
        if self._default_path != os.path.dirname(self._pdf_file):
            self.config.default['search_path'] = os.path.dirname(self._pdf_file)
        # Update config
        self.config.save()
    
    @staticmethod
    def _gen_output_file(path: str, file_name: str) -> str:
        """ Generates the full file name with path and name (replace unwanted characters)
        :param path: Path of the file
        :param file_name: Name of the file
        :return: Full file name
        """
        if file_name.endswith('.pdf'):
            # remove pdf from file name
            file_name = file_name[:-4]
            
        # ----- Replace unwanted characters -----
        file_name = file_name.replace('/', ' ') # remove '/
        file_name = file_name.replace('.', ' ') # remove '.'
        file_name = ' '.join(file_name.split()) # remove more than one ' ' (blanc)
        
        # Check if ending is correct
        if not file_name.endswith('.pdf'):
            # Otherwise add it
            file_name += '.pdf'
        
        # Return full path
        return os.path.abspath(path +'/'+ file_name)
    
    @staticmethod
    def _shorten_file(file_name: str, max_length: int) -> str:
        """ Shorten file name in case it is to long
        :param file_name: File name with path
        :param max_length: Max length to display
        :return: Shortened file name
        """
        # Check if length is to long
        if MENU_DEBUG or len(file_name) > max_length:
            # Shorten file
            act_file = os.path.basename(file_name)
        else:
            # do not shorten
            act_file = file_name
        # return name
        return act_file
    
    @staticmethod
    def _active_key_list(exit_entry: bool, back_entry: bool, chg_dir_entry: bool, chg_color_entry: bool, enter_keys: bool) -> list:
        """ Generates a key list to check
        :param exit_entry: If exit keys should be checked
        :param back_entry: If back keys should be checked
        :param chg_dir_entry: If change dir keys should be checked
        :param chg_color_entry: If change color keys should be checked
        :param enter_keys: If enter keys should be checked
        :return: A list of keys
        """
        # Init key list
        keys = []
        # Check if exit keys should be added
        if exit_entry:
            keys.extend(BottomMenu.EXIT.keys)
        # Check if back keys should be added
        if back_entry:
            keys.extend(BottomMenu.BACK.keys)
        # Check if change dir keys should be added
        if chg_dir_entry:
            keys.extend(BottomMenu.CHG_DIR.keys)
        # Check if change color keys should be added
        if chg_color_entry:
            keys.extend(BottomMenu.CHG_COLOR.keys)
        # Check if enter keys should be added
        if enter_keys:
            keys.extend(KeyLists.LIST_OKAY)
        return keys
    
    def _display_two_columns(self, two_column_list: TwoColumnList, header_list: list, exit_menu: bool = True, back_menu: bool = False, chg_dir_menu: bool = False, chg_color_menu: bool = False) -> int:
        """ Display a two column select screen
        :param two_column_list: Object which handles the data
        :param header_list: Header to be displayed
        :param exit_menu: If exit menu entry should be shown
        :param back_menu: If back menu entry should be shown
        :param chg_dir_menu: I change dir menu entry should be shown
        :param chg_color_menu: If change color menu entry should be displayed
        :return: valid pressed key as int
        """
        # function variables
        key: int = 0
        selected_idx: int = 0
        # Create menu
        draw_fcn = two_column_list.draw
        # main menu loop
        while True:
            if draw_fcn == two_column_list.refresh:
                # create header
                if MENU_DEBUG:
                    self._base.draw_head([header_list[0], f"{header_list[1]} [{selected_idx}] [{key}] [{two_column_list.entry_cnt} ({two_column_list._entry_start}|{two_column_list._entry_end})| {two_column_list.entry_max}]", header_list[2]])
                # refresh list
                two_column_list.refresh(selected_idx)
            else:
                # empty screen
                self.stdscr.clear()
                # create header
                if MENU_DEBUG:
                    self._base.draw_head([header_list[0], f"{header_list[1]} [{selected_idx}] [{key}] [{two_column_list.entry_cnt} ({two_column_list._entry_start}|{two_column_list._entry_end})| {two_column_list.entry_max}]", header_list[2]])
                else:
                    self._base.draw_head(header_list)
                # draw list
                draw_fcn(selected_idx)
                # draw menu
                self._draw_menu(next_page=two_column_list.next_page, prev_page=two_column_list.prev_page, end=exit_menu, back=back_menu, chg_dir=chg_dir_menu, chg_color=chg_color_menu)
                # Hide cursor
                curses.curs_set(0)
            
            # do keys
            key = self.stdscr.getch()
            # eval arrow keys
            selected_idx=two_column_list.eval_arrows_keys(key)
            # eval prev and next page
            if two_column_list.prev_page and key in BottomMenu.PREV_PAGE.keys:
                draw_fcn = two_column_list.draw_previous
            elif two_column_list.next_page and key in BottomMenu.NEXT_PAGE.keys:
                draw_fcn = two_column_list.draw_next
            else:
                draw_fcn = two_column_list.refresh
            # Get key list
            keys = self._active_key_list(exit_menu, back_menu, chg_dir_menu, chg_color_menu, two_column_list.is_drawn)
            # In case key is valid
            if key in keys:
                # return it
                return key
         
    def _display_path_dialog(self) -> int:
        """ Display a path dialog screen
        :return: Valid key number
        """
        # Clear screen
        self.stdscr.clear()
        # Display all characters
        curses.echo()
        # Check dir
        if os.path.isdir(self.config.default['search_path']):
            self._base.draw_head(["Enter new path: ", fr"(old Path: {self.config.default['search_path']})", ''])
        else:
            self._base.draw_head(["Enter new path: ", fr"Error: Path {self.config.default['search_path']} not exist", ''])
        # Draw bottom menu
        self._draw_menu(end=True, back=True)
        # Add line to where to add
        self.stdscr.addstr(5, 0, "> ")
        # Set curser
        curses.setsyx(3, 2)
        # make curser visible
        curses.curs_set(1)
        # Menu loop
        new_path = ""
        while True:
            # wait for key pressed
            key = self.stdscr.getch()
            # Get key list to check
            keys = self._active_key_list(True, True, False, False, False)
            # Check if key is valid
            if key in keys:
                # In case it is valid return key and disable curser
                curses.curs_set(0)
                return key
            # In case kex is enter
            elif key in KeyLists.LIST_OKAY:
                # Store new path
                tmp_path = new_path
                # Check if start with . to add to old dir
                if tmp_path.startswith('.'):
                    # add to old dir
                    tmp_path = self.config.default['search_path'] + '/' + tmp_path
                # If path exist
                if tmp_path:
                    # Create absolute path (and expand user)
                    tmp_path = os.path.abspath(os.path.expanduser(tmp_path))
                # Check if path is valid
                if os.path.isdir(tmp_path):
                    # Stop display all characters
                    curses.noecho()
                    # Store path
                    self.config.default['search_path'] = tmp_path
                    # Disable curser
                    curses.curs_set(0)
                    # end loop
                    break
                else:
                    # Display that the path was invalid and clear path
                    self.stdscr.addstr(3, 0, "Invalid path. Press Esc to go back or type a valid path: ")
                    new_path = ''
            # Key Backspace
            elif key == curses.KEY_BACKSPACE:
                # Remove last character
                new_path = new_path[:-1]
            else:
                # Add the typed character to the string
                new_path += chr(key)
            # In case of debug
            if MENU_DEBUG:
                self.stdscr.addstr(7, 0, ' ' * int(self.stdscr.getmaxyx()[1]))
                self.stdscr.addstr(7, 0, fr'key={key}')
                
            # Redraw the input with the updated string
            self.stdscr.addstr(5, 2, ' ' * int(self.stdscr.getmaxyx()[1] - 3))
            self.stdscr.addstr(5, 2, new_path)
            # Update screen
            self.stdscr.refresh()
        # Return the key value
        return key
        
    def _display_new_color_dialog(self) -> int:
        """ Display a color dialog screen
        :return: Valid key number
        """
        # Clear screen
        self.stdscr.clear()
        # Display all characters
        curses.echo()
        # init default strings
        invalid_format: str = '(invalid format)'
        valid_format: str = '(valid)'
        # Chose between color and name (color = True)
        color_active = True
        # Create header
        self._base.draw_head(["Enter new color: ", '', ''])
        # Create Menu
        self._draw_menu(end=True, back=True)
        # Add entry to add name
        self.stdscr.addstr(5, 0, 'Color name:', curses.A_ITALIC)
        self.stdscr.addstr(6, 0, "> ")
        # Add entry to add color
        self.stdscr.addstr(2, 0, 'Color in RGB = 255,255,255 or hex = 0x|# FFFFFF:', curses.A_ITALIC)
        self.stdscr.addstr(3, self._base.x_max - len(invalid_format) - 1, invalid_format, curses.A_ITALIC)
        self.stdscr.addstr(3, 0, "> ")
        # Set curser and made it visible
        curses.setsyx(3, 2)
        curses.curs_set(1)
        # Init string for name and color
        entries: dict = {
            True:'' , # color
            False:'', # name
        }
        # Generate valid keys to leave menu
        keys = self._active_key_list(True, True, False, False, False)
        # Display loop
        while True:
            # Wait for key
            key = self.stdscr.getch()
            # Check if key is in list
            if key in keys:
                # Disable curser
                curses.curs_set(0)
                # end loop
                break
            # If oky was pressed
            elif key in KeyLists.LIST_OKAY:
                # Check if name and color is valid
                if entries[True] != '' and entries[False] != '':
                    if self.config.colors.valid_color(entries[True]):
                        self.config.colors.add(entries[False], entries[True])
                        self.config.default['color'] = entries[False]
                        # Incase they are valid end loop
                        break
                # Change entry from name to color or vise versa
                color_active = not color_active
            # Backspace key (ASCII code 263)
            elif key == curses.KEY_BACKSPACE:
                # Remove from string
                entries[color_active] = entries[color_active][:-1]
            else:
                # Add to string
                entries[color_active] += chr(key)
            # Debug stuff
            if MENU_DEBUG:
                self.stdscr.addstr(8, 0, ' ' * int(self.stdscr.getmaxyx()[1]))
                self.stdscr.addstr(8, 0, fr'key={key}')
            # Check if color active
            if color_active:
                # Remove line
                self.stdscr.addstr(3, 2, ' ' * int(self.stdscr.getmaxyx()[1] - 3))
                # Draw valid or invalid
                if self.config.colors.valid_color(entries[color_active]):
                    self.stdscr.addstr(3, self._base.x_max - len(valid_format) - 1, valid_format, curses.A_ITALIC)
                else:
                    self.stdscr.addstr(3, self._base.x_max - len(invalid_format) - 1, invalid_format, curses.A_ITALIC)
                # Redraw the input with the updated string
                self.stdscr.addstr(3, 2, entries[color_active])
            else:
                # Redraw the input with the updated string
                self.stdscr.addstr(6, 2, ' ' * int(self.stdscr.getmaxyx()[1] - 3))
                self.stdscr.addstr(6, 2, entries[color_active])
            # update screen
            self.stdscr.refresh()
        # return key
        return key
        
    def _draw_menu_entry(self, row, pos, shortcut, text):
        """ Draw a single menu entry
        :param row: On the Row to draw
        :param pos: Position in row
        :param shortcut: The shortcut to display
        :param text: Menu text to display
        """
        # Draw showrcut
        self._base.draw_sel_str(row, pos*15, shortcut, True)
        # Draw text
        self._base.draw_sel_str(row, pos*15 + len(shortcut) + 1, text, False)
    
    def _draw_menu(self, *, end: bool = True, back: bool = True, next_page: bool = False, prev_page: bool = False, chg_dir: bool = False, chg_color: bool = False):
        """ Draws a menu with valid entries
        :param end: Exit menu displayed?
        :param back: Back menu displayed?
        :param next_page: Next page displayed?
        :param prev_page: Previous page displayed?
        :param chg_dir: Change dir displayed?
        :param chg_color: Change color displayed?
        """
        # get last row
        last_row = self.stdscr.getmaxyx()[0] -1
        # create list of menus to draw
        menus = [end, back, next_page, prev_page, chg_dir, chg_color]
        # create menu list
        entries = [BottomMenu.EXIT, BottomMenu.BACK, BottomMenu.NEXT_PAGE, BottomMenu.PREV_PAGE, BottomMenu.CHG_DIR, BottomMenu.CHG_COLOR]
        # loop over menu to draw
        for i in range(len(entries)):
            if menus[i]:
                self._draw_menu_entry(last_row, entries[i].pos, entries[i].shortcut, entries[i].text)
    
    @classmethod
    def run(cls, config: Config = None):
        """ Runs the menu
        :param config: Config file if exist
        """
        menu = cls()
        menu.hmi(config)

if __name__ == '__main__':
    #curses.wrapper(menu_main)
    TextInterface.run()
    

