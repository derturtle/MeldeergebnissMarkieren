import curses
import glob
import os
import sys

from Class_Config import Config
from PDFOperations import read_pdf

MENU_DEBUG: bool = True

CTRL_VALUE: int = 96
ESC_VALUE: int = 27
RETURN_VALUE: int = 10
SPACE_VALUE: int = 32


MENU_EXIT_STR: str = 'Exit'
MENU_EXIT_SHORT: str = '^X'
MENU_EXIT_KEYS: list  = [ord('x') - CTRL_VALUE, ord('X') - CTRL_VALUE]

MENU_CHANGE_DIR_STR: str = 'Change dir'
MENU_CHANGE_DIR_SHORT: str = '^D'
MENU_CHANGE_DIR_KEYS: list  = [ord('d') - CTRL_VALUE, ord('D') - CTRL_VALUE]

MENU_NEXT_PAGE_STR: str = 'Next page'
MENU_NEXT_PAGE_SHORT: str = '^N'
MENU_NEXT_PAGE_KEYS: list  = [ord('n') - CTRL_VALUE, ord('N') - CTRL_VALUE, curses.KEY_NPAGE, curses.KEY_NEXT]

MENU_PREV_PAGE_STR: str = 'Prev. page'
MENU_PREV_PAGE_SHORT: str = '^P'
MENU_PREV_PAGE_KEYS: list  = [ord('p') - CTRL_VALUE, ord('P') - CTRL_VALUE, curses.KEY_PPAGE, curses.KEY_PREVIOUS]

MENU_BACK_STR: str = 'Back'
MENU_BACK_SHORT: str = '^B'
MENU_BACK_KEYS: list  = [ord('b') - CTRL_VALUE, ord('B') - CTRL_VALUE]

MENU_ENTRY_ALL: str = '* All *'

MENU_QUIT: str = 'quit (q)'
MENU_NEXT_PAGE: str = 'next page ->'
MENU_PREV_PAGE: str = '<- previous page'

_default_path: str = ''
_active_file: str = ''
_selected_club: str = ''
_color: str = ''

class MenuStd:
    
    def __init__(self, stdscr, start_row, max_lines):
        self._index: int = 0
        self._buffer: list = []
        self._max_lines: int = 0
        
        self.stdscr = stdscr
        self.start_row = start_row
        self.max_lines = max_lines
    
    @property
    def max_lines(self) -> int:
        return  self._max_lines
    
    @max_lines.setter
    def max_lines(self, value: int):
        self._max_lines = value
        self.flush()
        
    def write(self, text: str):
        for split in text.split('\n'):
            if split:
                split = split + ' ' * (self.stdscr.getmaxyx()[1] - len(split))
                
                if self._index == self._max_lines:
                    self._buffer.remove(self._buffer[0])
                    self._buffer.append(split)
                else:
                    self._buffer[self._index] = split
                    self._index += 1
            
        for row, text in enumerate(self._buffer, start=self.start_row):
            self.stdscr.addstr(row, 0, text)
        
        self.stdscr.refresh()
        
    def flush(self):
        self._index = 0
        self._buffer = [''] * self._max_lines
        
        


def menu_exit(stdsrc, config: Config):
    exit(0)

def screen_height_weight(stdsrc) -> tuple:
    """ Returns the height and weight of a screen
    :param stdsrc:
    :return: height, weight => height and weight of the screen
    """
    # Get height and weight
    height, weight = stdsrc.getmaxyx()
    # define a minimum
    if weight < 78:
        weight = 78
    if height < 10:
        height = 10
        
    return height, weight

def draw_list_two_columns(stdscr, values: list, selected_idx: int, row_start: int, row_end: int, weight_max: int, end_string: str = '') -> tuple:
    
    col_start = [1, int(weight_max/2)+1]
    col_end = [int(weight_max/2)-1, int(weight_max/2)*2-1]
    col_len = col_end[0] - col_start[0]
    
    end_string = fr'[..]{end_string}'
    row = row_start
    index = 0
    
    if values:
        # loop over every index
        for value in values:
            # Calculate position left (0) or right (1)
            pos: int = index % 2
            # trim value if necessary
            if len(value) > col_len:
                value = value[0:col_len - len(end_string)] + end_string
                
            add_sel_str(stdscr, row, col_start[pos], value, index == selected_idx)
            
            if pos == 1:
                row += 1
                if row + 1 == row_end:
                    break
            # increase index
            index += 1
        
        if index >= len(values)-1:
            index = -1
    else:
        stdscr.addstr(row, col_start[0], 'Nothing found')
        row += 1
        index = -1
    return row, index
    
def draw_menu_item(stdscr, row: int, col_index: int, menu_text: str, menu_shortcut: str):
    add_sel_str(stdscr, row, col_index, menu_shortcut, True)
    add_sel_str(stdscr, row, col_index + len(menu_shortcut) + 1, menu_text, False)
    
def draw_menu(stdscr, row: int, max_weight : int, *, back: bool = False, change_dir: bool = False,  next_page: bool = False, previous_page: bool = False):
    draw_menu_item(stdscr, row, 0, MENU_EXIT_STR, MENU_EXIT_SHORT)

    if change_dir:
        draw_menu_item(stdscr, row, 16, MENU_CHANGE_DIR_STR, MENU_CHANGE_DIR_SHORT)
        
    if next_page:
        draw_menu_item(stdscr, row, max_weight-(2*16), MENU_NEXT_PAGE_STR, MENU_NEXT_PAGE_SHORT)

    if previous_page:
        draw_menu_item(stdscr, row, max_weight - 16, MENU_PREV_PAGE_STR, MENU_PREV_PAGE_SHORT)
        
    if back:
        draw_menu_item(stdscr, row, 16*2, MENU_BACK_STR, MENU_BACK_SHORT)
    

def menu_select_path(stdscr, config: Config):
    global _default_path
    
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter new path: ", curses.A_BOLD)
    if os.path.isdir(config.default['search_path']):
        stdscr.addstr(1, 0, fr"(old Path: {config.default['search_path']})", curses.A_ITALIC)
    else:
        stdscr.addstr(1, 0, fr"Error: Path {config.default['search_path']} not exist", curses.A_ITALIC)
    stdscr.addstr(2, 0, "> ")
    new_path = stdscr.getstr(2, 3, 100).decode("utf-8").strip()
    curses.noecho()
    
    if new_path == '':
        new_path = _default_path
    elif new_path.startswith('.'):
        new_path = config.default['search_path'] + '/' + new_path
    
    new_path = os.path.abspath(os.path.expanduser(new_path))
    
    if os.path.isdir(new_path):
        config.default['search_path'] = new_path
        if not _default_path:
            _default_path = new_path
    
    return menu_choose_pdf

def add_sel_str(stdscr, row: int, col: int, text: str, selected: bool):
    if selected:
        stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(row, col, text)
        stdscr.attroff(curses.A_REVERSE)
    else:
        stdscr.addstr(row, col, text)

def eval_arrows_double_menu(key, act_idx, last_idx) -> int:
    new_idx = act_idx
    
    # only one entry
    if last_idx == 0:
        return new_idx
    
    # Min 2. entries
    if key == curses.KEY_UP:
        # Check for first row left
        if act_idx == 0:
            if last_idx >= 2:
                new_idx = last_idx - (last_idx + 1) % 2
        # Check for first row right
        elif act_idx == 1:
            if last_idx >= 3:
                new_idx = last_idx - 1 + (last_idx + 1) % 2
        else:
            new_idx = act_idx - 2
    elif key == curses.KEY_DOWN:
        if act_idx == last_idx - 1:
            new_idx = 1 - (last_idx + 1) % 2
        elif act_idx == last_idx:
            new_idx = (last_idx + 1) % 2
        else:
            new_idx = act_idx + 2
    elif key == curses.KEY_LEFT:
        if act_idx == last_idx and (last_idx +1 ) % 2 == 1:
            # do nothing
            pass
        # elif act_idx == 0:
        #     new_idx = 1
        # even
        elif act_idx % 2 == 0:
            new_idx = act_idx + 1
        # odd
        else:
            new_idx = act_idx - 1
    elif key == curses.KEY_RIGHT:
        if act_idx == last_idx and (last_idx +1 ) % 2 == 1:
            # do nothing
            pass
        # elif act_idx == 1:
        #     new_idx = 0
        # even
        elif act_idx % 2 == 0:
            new_idx = act_idx + 1
        # odd
        else:
            new_idx = act_idx - 1
    else:
        pass
    
    return new_idx
            
def draw_at_end(stdscr):
    y, x = stdscr.getmaxyx()
    stdscr.addstr(y-1,x-1, '')


def draw_file_dialog(stdscr, act_path, pdf_files, selected_idx, weight, height, key):
    stdscr.clear()
    stdscr.addstr(0, 0, "Choose your PDF file:", curses.A_BOLD)
    if MENU_DEBUG:
        stdscr.addstr(1, 0, f"({act_path}) [{selected_idx}] [{key}]", curses.A_ITALIC)
    else:
        stdscr.addstr(1, 0, f"({act_path})", curses.A_ITALIC)
    
    row = 3
    
    row, last_index = draw_list_two_columns(stdscr, pdf_files, selected_idx, row, height - 2, weight, '.pdf')
    
    #draw_menu(stdscr, height-1, weight, next_page=True, previous_page=True)
    return last_index

def draw_cc_head(stdscr, strings: list):
    stdscr.clear()
    stdscr.addstr(0, 0, strings[0], curses.A_BOLD)
    stdscr.addstr(1, 0, strings[1], curses.A_ITALIC)
    stdscr.addstr(3, 0, strings[2])
    

def menu_choose_color(stdscr, config: Config):
    global _selected_club
    global _color
    height, weight = stdscr.getmaxyx()
    
    color_list = list(map(lambda x: fr'{x[0]} (#{x[1].upper()})', config.colors.hex.items()))
    
    # check if color exist in config
    if config.default['color'] in list(config.colors.rgb.keys()):
        selected_idx: int = int(list(config.colors.rgb.keys()).index(config.default['color']))
        max_entries: int = ((height - 6) * 2)
        start_index = int(selected_idx / max_entries) * max_entries
        selected_idx -= start_index
    else:
        start_index: int = 0
        selected_idx: int = 0
    
    while True:
        draw_cc_head(stdscr, ["Select your color for marking", f"({_selected_club})", ""])
        
        next_page: bool = False
        prev_page: bool = False

        row = 3
        row, last_index = draw_list_two_columns(stdscr, color_list[start_index:], selected_idx, row, height - 2, weight)

        if last_index > 0:
            next_page = True
        if start_index > 0:
            prev_page = True
        
        draw_menu(stdscr, height - 1, weight, back=True, next_page=next_page, previous_page=prev_page)
        
        # generated max idx for evaluate arrows
        if last_index == -1:
            max_idx = len(color_list[start_index:]) - 1
        else:
            max_idx = last_index - start_index
        
        draw_at_end(stdscr)
        # do keys
        key = stdscr.getch()
        # eval arrow key
        selected_idx = eval_arrows_double_menu(key, selected_idx, max_idx)
        # eval menu keys
        if key in MENU_EXIT_KEYS:
            break
        elif next_page and key in MENU_NEXT_PAGE_KEYS:
            start_index += last_index + 1
        elif prev_page and key in MENU_PREV_PAGE_KEYS:
            if start_index > (height - 6) * 2:
                start_index -= (height - 6) * 2
            else:
                start_index = 0
        elif key in MENU_BACK_KEYS:
            return menu_choose_club
        # elif key in [curses.KEY_ENTER, RETURN_VALUE]:
        #     _color = color_list[start_index:][selected_idx]
        #     return menu_chosse_color
    
    return menu_exit


def menu_choose_club(stdscr, config: Config):
    global _active_file
    global _selected_club
    height, weight = stdscr.getmaxyx()
    draw_cc_head(stdscr, ["Reading PDF file", f"({_active_file})", "Please wait"])
    
    local_out = MenuStd(stdscr, 5, 10)
    
    sys.stdout = local_out
    collection, borders = read_pdf(_active_file)
    sys.stdout = sys.__stdout__
    
    error: bool = False
    if not collection:
        error = True
    elif not collection.clubs:
        error = True
    
    if error:
        draw_cc_head(stdscr, ["Reading Failed", f"({_active_file})", "Sorry could not find useful information"])
        
        draw_menu(stdscr, height-1, weight, change_dir=True, back=True)
        
        # do keys
        key = stdscr.getch()
        if key in MENU_BACK_KEYS + [curses.KEY_ENTER, RETURN_VALUE]:
            return menu_choose_pdf
        elif key in MENU_CHANGE_DIR_KEYS:
            return menu_select_path
    else:
        club_names = list(map(lambda x: x.name, collection.clubs))
        club_names.sort()
        club_names.insert(0, MENU_ENTRY_ALL)
        
        # check if club in config
        if config.default['default_club'] in club_names:
            selected_idx: int = int(club_names.index(config.default['default_club']))
            max_entries: int = ((height - 6) * 2)
            start_index = int(selected_idx/max_entries) * max_entries
            selected_idx -= start_index
        else:
            start_index: int = 0
            selected_idx: int = 0
            
            
        while True:
            draw_cc_head(stdscr, ["Found following Clubs:", f"({_active_file})", ''])
            # draw pfd file dialog
            row = 3
            row, last_index = draw_list_two_columns(stdscr, club_names[start_index:], selected_idx, row, height - 2, weight)
            
            next_page: bool = False
            prev_page: bool = False
            
            if last_index > 0:
                next_page = True
            if start_index > 0:
                prev_page = True
            
            draw_menu(stdscr, height - 1, weight, back=True, next_page=next_page, previous_page=prev_page)
            
            # generated max idx for evaluate arrows
            if last_index == -1:
                max_idx = len(collection.clubs[start_index:]) - 1
            else:
                max_idx = last_index - start_index

            if MENU_DEBUG:
                stdscr.addstr(int(stdscr.getmaxyx()[0] - 2), 0, fr'start_index={start_index} selected_idx={selected_idx} index={club_names.index(config.default['default_club'])}/{len(club_names)}')
            
            draw_at_end(stdscr)
            # do keys
            key = stdscr.getch()
            # eval arrow key
            selected_idx = eval_arrows_double_menu(key, selected_idx, max_idx)
            # eval menu keys
            if key in MENU_EXIT_KEYS:
                break
            elif next_page and key in MENU_NEXT_PAGE_KEYS:
                start_index += last_index + 1
            elif prev_page and key in MENU_PREV_PAGE_KEYS:
                if start_index > (height - 6) * 2:
                    start_index -= (height - 6) * 2
                else:
                    start_index = 0
            elif key in MENU_BACK_KEYS:
                return menu_choose_pdf
            elif key in [curses.KEY_ENTER, RETURN_VALUE]:
                _selected_club = club_names[start_index:][selected_idx]
                if _selected_club != MENU_ENTRY_ALL:
                    config.default['default_club'] = _selected_club
                return menu_choose_color
            
    return menu_exit
    

def menu_choose_pdf(stdscr, config: Config):
    global _active_file
    
    act_path = config.default["search_path"]
    pdf_files = glob.glob(fr'{act_path}/*.pdf')
    if pdf_files:
        pdf_files = list(map(os.path.basename, pdf_files))
        pdf_files.sort()

    key = 0
    start_index = 0
    selected_idx = 0
    
    while True:
        # Get height and weight
        height, weight = screen_height_weight(stdscr)
        # draw pfd file dialog
        last_index = draw_file_dialog(stdscr, act_path, pdf_files[start_index:], selected_idx, weight, height, key)
        
        next_page: bool = False
        prev_page: bool = False
        
        if last_index > 0:
            next_page = True
        if start_index > 0:
            prev_page = True
        
        draw_menu(stdscr, height-1, weight, change_dir=True, next_page=next_page, previous_page=prev_page)
        
        # generated max idx for evaluate arrows
        if last_index == -1:
            max_idx = len(pdf_files[start_index:])-1
        else:
            max_idx = last_index-start_index
        
        if MENU_DEBUG:
            stdscr.addstr(int(stdscr.getmaxyx()[0] - 2), 0, fr'max_idx={max_idx}')
        
        draw_at_end(stdscr)
        # do keys
        key = stdscr.getch()
        # eval arrow key
        selected_idx = eval_arrows_double_menu(key, selected_idx, max_idx)
        # eval menu keys
        if key in MENU_EXIT_KEYS:
            break
        elif next_page and key in MENU_NEXT_PAGE_KEYS:
            start_index += last_index + 1
        elif prev_page and key in MENU_PREV_PAGE_KEYS:
            if start_index > (height-6) * 2:
                start_index -= (height-6) * 2
            else:
                start_index = 0
        elif key in MENU_CHANGE_DIR_KEYS:
            return menu_select_path
        elif key in [curses.KEY_ENTER, RETURN_VALUE]:
            if pdf_files:
                _active_file = fr'{act_path}/{pdf_files[selected_idx]}'
                return menu_choose_club
            else:
                return menu_select_path
    
    return menu_exit

def menu_main(stdscr, config : [Config, None] = None):
    global _default_path
    # Check fo config file
    if not config:
        config = Config()
    # Set start screen
    screen = menu_choose_pdf
    # Check path in config file
    if not 'search_path' in config.default.keys():
        # Set default value downloads
        config.default['search_path'] = os.path.expanduser("~/Downloads")
    # Check if path exits
    if not os.path.isdir(config.default['search_path']):
        screen = menu_select_path
    
    # Set default path
    _default_path = config.default['search_path']
    
    # Get standard screen
    #stdscr = curses.initscr()
    
    # Call menu
    while screen:
        screen = screen(stdscr, config)
    
    # Call menu
    #screen(stdscr, config)
    

if __name__ == '__main__':
    curses.wrapper(menu_main)
    #menu()