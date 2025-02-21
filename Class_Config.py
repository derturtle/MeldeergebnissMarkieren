import os
import configparser

# Global dictionary for default values could be found in pdf
__PDF_VALUES: dict = {
    'competition': 'Wettkampf',
    'heat': 'Lauf',
    'heats': 'Läufe',
    'lane': 'Bahn',
    'club': 'Verein',
    'segment': 'Abschnitt',
    'entry_cnt': 'Anzahl Meldungen',
    'no_of_entries': 'Gesamtzahl der Meldungen',
    'competition_sequenz': 'Wettkampffolge',
    'judging_panel': 'Kampfgericht',
    'continue_value': 'noch',
    'finale': 'Finale',
    'male': 'männlich',
    'female': 'weiblich',
    'mixed': 'mixed'
}
# Global dictionary for default colors to use
__COLORS: dict = {
    'yellow': '#ffff00',
    'grey_75': '#bfbfbf',
    'grey': '#808080',
    'cyan': '#00ffff',
    'green': '#00ff00',
    'lite_green': '#80ff00',
    'lite_blue': '#0080ff',
    'magenta': '#ff00ff',
    'orange': '#ff8000'
}
# Global dictionary for default values which are not grouped
__DEFAULT: dict = {
    'color': 'yellow',
    'file_ending': '_marked',
    'default_club': 'SV Georgsmarienhütte',
    'mark_start': 7,
    'mark_end': 95,
    'offset': 1
}
# Global dictionary for to create default config
_CONFIG: dict = {
    'Default': __DEFAULT,
    'Colors': __COLORS,
    'PDFParseValues': __PDF_VALUES
}


class _ParseValues:
    """
    Represents _ParseValues object
    
    Here are all values stored which are parsed in a PDF file

    Attributes:
    -----------
    competition : str
        Value for finding a competition
    competition_sequenz : str
        Value for finding a competition sequenz
    club : str
        Value for finding a club
    heat : str
        Value for finding a heat
    heats : str
        Value for finding heats
    lane : str
        Value for finding a lane
    segment : str
        Value for finding a segment
    male : str
        male value
    female : str
        female value
    mixed : str
        mixed value
    segment : str
        Value for finding segment
    final : str
        Value for finding a final
    entry_cnt : str
        Value for finding the entry cnt
    judging_panel : str
        Value for finding the judging panel
    continue_value : str
        Value for finding the continue value
    no_of_entries : str
        Value for finding the no of entries
    """
    def __init__(self, parsed_values: dict):
        """ Initializes a new _ParseValues class
        :param parsed_values: The values to be parsed
        """
        self.parsed_values: dict = parsed_values

    @property
    def competition(self) -> str:
        """ Returns a competition string
        :return: Value to identify the competition
        """
        return self._chk_key('competition')

    @property
    def competition_sequenz(self) -> str:
        """ Returns a competition sequenz string
        :return: Value to identify the competition sequenz
        """
        return self._chk_key('competition_sequenz')

    @property
    def club(self) -> str:
        """ Returns a club string
        :return: Value to identify the club(s)
        """
        return self._chk_key('club')

    @property
    def heat(self) -> str:
        """ Returns a heat string
        :return: Value to identify a heat
        """
        return self._chk_key('heat')

    @property
    def heats(self) -> str:
        """ Returns a heats string
        :return: Value to identify the value for heats
        """
        return self._chk_key('heats')

    @property
    def lane(self) -> str:
        """ Returns a lane string
        :return: Value to identify a lane
        """
        return self._chk_key('lane')

    @property
    def segment(self) -> str:
        """ Returns a segment string
        :return: Value to identify a segment
        """
        return self._chk_key('segment')

    @property
    def male(self) -> str:
        """ Returns the male string
        :return: The male value
        """
        return self._chk_key('male')

    @property
    def female(self) -> str:
        """ Returns the female string
        :return: The female value
        """
        return self._chk_key('female')

    @property
    def mixed(self) -> str:
        """ Returns the mixed string
        :return: The mixed value
        """
        return self._chk_key('mixed')

    @property
    def final(self) -> str:
        """ Returns a final string
        :return: Value to identify a final
        """
        return self._chk_key('finale')

    @property
    def entry_cnt(self) -> str:
        """ Returns a entry count string
        :return: Value to identify an entry count
        """
        return self._chk_key('entry_cnt')

    @property
    def judging_panel(self) -> str:
        """ Returns a judging panel string
        :return: Value to identify a judging panel
        """
        return self._chk_key('judging_panel')

    @property
    def continue_value(self) -> str:
        """ Returns the continue value
        :return: A string to identify the continue value
        """
        return self._chk_key('continue_value')

    @property
    def no_of_entries(self) -> str:
        """ Returns a no of entries string
        :return: Value to identify the number of entries
        """
        return self._chk_key('no_of_entries')

    def _chk_key(self, key: str) -> str:
        """ Function checks if key in dictionary
        :param key: Key to check
        :return: The value from the dictionary
        """
        if key in list(self.parsed_values.keys()):
            return self.parsed_values[key]
        else:
            return ''


class _Colors:
    """
    Represents a Color object
    
    Attributes:
    -----------
    hex : dict
        A dictionary with the colors a kex in hex
    rgb : dict
        A dictionary with the colors a kex in rgb
    """
    def __init__(self, colors: dict):
        """ Initializes a new _Color class
        :param colors: The color values
        """
        self._colors = colors
        self.hex = {}
        self.rgb = {}
        self._convert_colors()

    def _convert_colors(self):
        """ Function to convert colors from hex to rgb """
        # loop over colors
        for key, value in self._colors.items():
            # check if color starts with # (hex)
            if value.startswith('#'):
                # Create hex value
                hex_value = value.replace('#', '').strip()
            # check if color starts with 0x (hex)
            elif value.startswith('0x'):
                # Create hex value
                hex_value = value.replace('0x', '').strip()
            else:
                # Use value direct
                hex_value = value.strip()
            # Convert to dec
            dec_value = self._hex_to_dec(hex_value)
            # Set attributes
            self.hex[key] = hex_value
            self.rgb[key] = dec_value

    @staticmethod
    def _hex_to_dec(value: str):
        """ Function converts hex values like 'KAFFEE' to rgb
        :param value: hex value
        :raise ValueError: The value is not like 6x[0..9A..F]
        """
        if len(value) == 6:
            r = int(value[:2], 16)
            g = int(value[2:4], 16)
            b = int(value[4:], 16)
            return r, g, b
        else:
            raise ValueError


class Config:
    """
    Represents a Config object

    Attributes:
    -----------
    pdf_values : _ParseValues
        A object with the values to be parsed
    colors : _Colors
        A object with the available colors
    """
    def __init__(self, config_file: str = ''):
        """ Initializes a new config class
        :param config_file: Name of the config file
        """
        # Create config file
        self._config = configparser.ConfigParser()
        if not config_file == '':
            # Read config file
            self._create_config(config_file)
        else:
            # Create config file
            self._create_config('.result_config.ini')
        # Config file to dictionary
        self._config_dict = dict(self._config)
        # Set parsed values if available
        if 'PDFParseValues' in list(self._config_dict.keys()):
            self.pdf_values = _ParseValues(dict(self._config_dict['PDFParseValues']))
        else:
            self.pdf_values = _ParseValues({})
        # Set colors if available
        if 'Colors' in list(self._config_dict.keys()):
            self._colors = _Colors(dict(self._config_dict['Colors']))
        else:
            self._colors = _Colors({})

    def _create_config(self, config_file):
        """ Creates config file
        :param config_file:  Name of config file
        """
        # Check if file exist
        if os.path.exists(config_file):
            # Read file
            self._config.read(config_file)
        else:
            # otherwise read default config
            self._config.read_dict(_CONFIG)
            # and write
            with open(config_file, 'w') as fp:
                self._config.write(fp)

    @property
    def colors(self) -> _Colors:
        """ Return a color values
        :return: Color dictionary
        """
        return self._colors
