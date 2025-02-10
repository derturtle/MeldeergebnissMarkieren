import os
import configparser

__PDF_VALUES: dict = {
    'competition': 'Wettkampf',
    'heat': 'Lauf',
    'heats': 'Läufe',
    'lane': 'Bahn',
    'club': 'Verein',
    'segment': 'Abschnitt',
    'entry_cnt': 'Anzahl Meldungen',
    'competition_sequenz': 'Wettkampffolge',
    'judging_panel': 'Kampfgericht',
    'continue_value': 'noch',
    'finale': 'Finale',
    'male': 'männlich',
    'female': 'weiblich',
    'mixed': 'mixed'
}
__COLORS: dict = {
    'yellow': '#ffff00',
    'grey_85': '#d9d9d9',
    'cyan': '#00ffff',
    'green': '#00ff00',
    'lite_green': '#80ff00',
    'lite_blue': '#0080ff',
    'magenta': '#ff00ff',
    'orange': '#ff8000'
}
__DEFAULT: dict = {
    'color': 'yellow',
    'file_ending': '_marked',
    'default_club': 'SV Georgsmarienhütte',
    'mark_start': 7,
    'mark_end': 95,
    'offset': 1
}

_CONFIG: dict = {
    'Default': __DEFAULT,
    'Colors': __COLORS,
    'PDFParseValues': __PDF_VALUES
}


class _ParseValues:
    def __init__(self, parsed_values: dict):
        self.parsed_values: dict = parsed_values
    
    @property
    def competition(self) -> str:
        return self._chk_key('competition')
    
    @property
    def competition_sequenz(self) -> str:
        return self._chk_key('competition_sequenz')
    
    @property
    def club(self) -> str:
        return self._chk_key('club')
    
    @property
    def heat(self) -> str:
        return self._chk_key('heat')
    
    @property
    def heats(self) -> str:
        return self._chk_key('heats')
    
    @property
    def lane(self) -> str:
        return self._chk_key('lane')
    
    @property
    def segment(self) -> str:
        return self._chk_key('segment')
    
    @property
    def male(self) -> str:
        return self._chk_key('male')
    
    @property
    def female(self) -> str:
        return self._chk_key('female')
    
    @property
    def mixed(self) -> str:
        return self._chk_key('mixed')
    
    @property
    def entry_cnt(self) -> str:
        return self._chk_key('entry_cnt')
    
    @property
    def judging_panel(self) -> str:
        return self._chk_key('judging_panel')
    
    def _chk_key(self, key: str) -> str:
        if key in list(self.parsed_values.keys()):
            return self.parsed_values[key]
        else:
            return ''


class _Colors:
    def __init__(self, colors: dict):
        self._colors = colors
        self.colors_hex = {}
        self.colors_rgb = {}
        self._convert_colors()
    
    def _convert_colors(self):
        for key, value in self._colors.items():
            if value.startswith('#'):
                hex_value = value.replace('#', '').strip()
            elif value.startswith('0x'):
                hex_value = value.replace('#', '').strip()
            else:
                hex_value = value.strip()
            dec_value = self._hex_to_dec(hex_value)
            self.colors_hex[key] = hex_value
            self.colors_rgb[key] = dec_value
    
    @staticmethod
    def _hex_to_dec(value: str):
        if len(value) == 6:
            r = int(value[:2], 16)
            g = int(value[2:4], 16)
            b = int(value[4:], 16)
            return r, g, b
        else:
            raise ValueError


class Config:
    def __init__(self, config_file: str = ''):
        self._config = configparser.ConfigParser()
        if not config_file == '':
            self._create_config(config_file)
        else:
            self._create_config('.result_config.ini')
        
        self._config_dict = dict(self._config)
        
        if 'PDFParseValues' in list(self._config_dict.keys()):
            self.pdf_values = _ParseValues(dict(self._config_dict['PDFParseValues']))
        else:
            self.pdf_values = _ParseValues({})
        
        if 'Colors' in list(self._config_dict.keys()):
            self._colors = _Colors(dict(self._config_dict['Colors']))
        else:
            self._colors = _Colors({})
    
    def _create_config(self, config_file):
        if os.path.exists(config_file):
            self._config.read(config_file)
        else:
            self._config.read_dict(_CONFIG)
            with open(config_file, 'w') as fp:
                self._config.write(fp)
    
    @property
    def colors(self) -> dict:
        if 'Colors' in list(self._config_dict.keys()):
            return self._config_dict['Colors']
        else:
            return {}
