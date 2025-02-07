import re
import datetime

FINAL_STR: str = 'Finale'


class _Entry:
    def __init__(self, entry_name: [str, None] = None):
        self._name = ''
        self._instance: dict = {}
        if entry_name:
            self.create(entry_name)
        else:
            self.create('default')
        pass
    
    @property
    def instance(self) -> dict:
        return self._instance[self._name]
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if value in list(self._instance.keys()):
            self._name = value
    
    def available(self) -> list:
        return list(self._instance.keys())
    
    def create(self, value: str) -> bool:
        if self.exist(value):
            return False
        else:
            self._instance[value] = {}
            self.name = value
            return True
    
    def is_active(self, value: str):
        return self.name == value
    
    def exist(self, value) -> bool:
        return value in list(self._instance.keys())

class _Registry:
    def __init__(self, name: [str, None] = None):
        #self._instance = {}
        #self.entry : _Entry = _Entry(self._instance, name)
        self.entry: _Entry = _Entry(name)
    
    def add(self, obj):
        # if type(obj) not in self.entry.instance:
        #     self.entry.instance[type(obj)] = {}
        # self.entry.instance[type(obj)][str(obj)] = obj
        self.entry.instance.setdefault(type(obj), []).append(obj)
    
    def remove(self, obj):
        obj_list = self.entry.instance.get(type(obj), [])
        if obj in obj_list:
            obj_list.remove(obj)
            # Falls die Liste leer ist, entfernen wir den Typ ganz aus dem Dict
            if not obj_list:
                del self.entry.instance[type(obj)]
    
    def get_all(self, obj_type=None):
        if obj_type:
            return self.entry.instance.get(obj_type, [])
        return self.entry.instance
    
    def __repr__(self):
        return f"Registry[{self.entry.name}]({self.entry.instance})"

class _Base:
    _registry: [None, _Registry] = None
    
    def __init__(self, name: str  = ''):
        self._name = name
        if not _Base._registry:
            _Base._registry = _Registry(name)
        elif name:
            _Base._registry.entry.create(name)
        
        _Base._registry.add(self)
        self._name = _Base._registry.entry.name
            
    def __del__(self):
        _Base._registry.remove(self)
        
    def __repr__(self):
        return f"{self.__class__.__name__}()"
    
    def remove(self):
        self.__del__()
        

class Collection(_Base):
    
    def __init__(self, name: str):
        self._name = name
        _Base.__init__(self, name)
    
    @property
    def associations(self) -> list:
        return self._get_list(Association)
    
    @property
    def clubs(self) -> list:
        return self._get_list(Club)
    
    @property
    def sections(self) -> list:
        return self._get_list(Section)
    
    @property
    def years(self) -> list:
        return self._get_list(Year)
    
    @property
    def judges(self) -> list:
        return self._get_list(Judge)
    
    @property
    def athletes(self) -> list:
        return self._get_list(Athlete)
    
    @property
    def competitions(self) -> list:
        return self._get_list(Competition)
    
    @property
    def heats(self) -> list:
        return self._get_list(Heat)
    
    @property
    def lanes(self) -> list:
        return self._get_list(Lane)

    def _get_list(self, obj_type) -> list:
        self._set_active()
        ret_list = self._registry.get_all(obj_type)
        if ret_list == self._registry.entry.instance:
            return []
        else:
            return ret_list

    def _set_active(self):
        if not self._registry.entry.is_active(self._name):
            self._registry.entry.name = self._name

    def __str__(self) -> str:
        return fr'Collection({self._name})'

class SpecialCollection(Collection):
    
    def competition_by_no(self, value: int):
        return self._by_no(value, self.competitions)
    
    def competitions_dict(self) -> dict:
        return dict(map(lambda x: (x.no, x), self.competitions))
    
    def sections_by_no(self, value: int):
        return self._by_no(value, self.sections)
    
    def sections_dict(self) -> dict:
        return dict(map(lambda x: (x.no, x), self.sections))
    
    def club_by_name(self, value: str):
        return self._by_name(value, self.clubs)
    
    def clubs_dict(self):
        return dict(map(lambda x: (x.no, x), self.clubs))
    
    def athletes_by_name(self, value):
        pass
    
    def athletes_by_year(self, value):
        pass
    
    def athlete_by_club(self, value):
        pass
    
    def athletes_dict(self):
        pass
    
    def get_year(self, year: int):
        if type(year) != int:
            raise ValueError
        if self.years:
            for y in self.years:
                if y.year == year:
                    return y
        return None
        
    @staticmethod
    def _by_no(no: int, objects: list):
        if type(no) != int:
            raise ValueError
        if objects:
            values = [item for item in objects if item.no == no]
            if values:
                return values[0]
            
        return None
    
    @staticmethod
    def _by_name(name: str, objects: list, single_obj: bool = True):
        if type(name) != str:
            raise ValueError
        if objects:
            values = [item for item in objects if item.name == name]
            if values:
                if single_obj:
                    return values[0]
                else:
                    return values
        
        return None

# ----- Base Class Area -----

class HasOccurrence:
    def __init__(self):
        self._occurrence: list = []
    
    @property
    def occurrence(self) -> list:
        return self._occurrence
    
    def add_occurrence(self, value):
        if not value in self._occurrence:
            self._occurrence.append(value)
    
    def remove_occurrence(self, value):
        if value in self._occurrence:
            self._occurrence.remove(value)


class HasLanes:
    def __init__(self):
        self._lanes: list = []
    
    @property
    def lanes(self) -> list:
        return self._lanes
    
    def add_lane(self, value):
        if not value in self._lanes:
            self._lanes.append(value)
    
    def remove_lane(self, value):
        if value in self._lanes:
            self._lanes.remove(value)


class HasHeats:
    def __init__(self):
        self._heats: list = []
    
    @property
    def heats(self) -> list:
        return self._heats
    
    def add_heat(self, value):
        if not value in self._heats:
            self._heats.append(value)
    
    def remove_heat(self, value):
        if value in self._heats:
            self._heats.remove(value)


class HasClubs:
    def __init__(self):
        self._clubs: list = []
    
    @property
    def clubs(self) -> list:
        return self._clubs
    
    def add_club(self, value):
        if not value in self._clubs:
            self._clubs.append(value)
    
    def remove_club(self, value):
        if value in self._clubs:
            self._clubs.remove(value)


class HasAthletes:
    def __init__(self):
        self._athletes: list = []
    
    @property
    def athletes(self) -> list:
        return self._athletes
    
    def add_athlete(self, value):
        if not value in self._athletes:
            self._athletes.append(value)
    
    def remove_athlete(self, value):
        if value in self._athletes:
            self._athletes.remove(value)


class HasJudges:
    def __init__(self):
        self._judges: list = []
    
    @property
    def judges(self) -> list:
        return self._judges
    
    def add_judge(self, value):
        if not value in self._judges:
            self._judges.append(value)
    
    def remove_judge(self, value):
        if value in self._judges:
            self._judges.remove(value)


class HasCompetitions:
    def __init__(self):
        self._competitions: list = []
    
    @property
    def competitions(self) -> list:
        return self._competitions
    
    def add_competition(self, value):
        if not value in self._competitions:
            self._competitions.append(value)
    
    def remove_competition(self, value):
        if value in self._competitions:
            self._competitions.remove(value)


class Quantity:
    def __init__(self, first_enty_name: str, second_entry_name: str, args: tuple, kwargs: dict):
        self.__first_enty_name = first_enty_name
        self.__second_entry_name = second_entry_name
        self._value: dict = {first_enty_name: 0, second_entry_name: 0}
        
        if len(args) == 0:
            # use kwargs
            self.__check_kwargs(kwargs)
        elif len(args) == 1:
            if type(args[0]) is dict:
                self.__check_kwargs(args[0])
            elif type(args[0]) is list and len(args[0]) <= 2:
                self.__check_list(args[0])
            elif type(args[0]) is int:
                self._value[self.__first_enty_name] = args[0]
            else:
                raise ValueError
        elif len(args) == 2:
            self.__check_list(list(args))
        else:
            raise ValueError
    
    def __str__(self):
        return fr'{self._value[self.__first_enty_name]} / {self._value[self.__second_entry_name]}'
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}('
        tmp += fr'{self._first_enty_name}={self._value[self._first_enty_name]}, '
        tmp += fr'{self._second_entry_name}={self._value[self._second_entry_name]}'
        return tmp + ')'
    
    def __check_kwargs(self, kwargs: dict):
        if len(kwargs) != 0:
            for key, value in kwargs.items():
                # self[key] = value
                if not (key == self.__first_enty_name or key == self.__second_entry_name and type(value) is int):
                    raise ValueError
                else:
                    self._value[key] = value
    
    def __check_list(self, args: list):
        for i in range(0, len(args)):
            if type(args[i]) is int:
                self._value[list(self._value.keys())[i]] = args[i]
            else:
                raise ValueError
    
    def to_list(self) -> list:
        return [self._value[self._first_enty_name], self._value[self._first_enty_name]]
    
    def to_dict(self) -> dict:
        return self._value
    
    def is_empty(self) -> bool:
        return self.cnt == 0
    
    @property
    def cnt(self) -> int:
        return sum(self.to_list())
    
    @property
    def _first_enty_name(self) -> str:
        return self.__first_enty_name
    
    @property
    def _second_entry_name(self) -> str:
        return self.__second_entry_name


# ----- Working Classes -----

class Participants(Quantity):
    def __init__(self, *args, **kwargs):
        Quantity.__init__(self, 'female', 'male', args, kwargs)
    
    @property
    def female(self) -> int:
        return self._value[self._first_enty_name]
    
    @female.setter
    def female(self, cnt: int):
        self._value[self._first_enty_name] = cnt
    
    @property
    def male(self) -> int:
        return self._value[self._second_entry_name]
    
    @male.setter
    def male(self, cnt: int):
        self._value[self._second_entry_name] = cnt


class Starts(Quantity):
    def __init__(self, *args, **kwargs):
        Quantity.__init__(self, 'single', 'relay', args, kwargs)
    
    @property
    def single(self) -> int:
        return self._value[self._first_enty_name]
    
    @single.setter
    def single(self, cnt: int):
        self._value[self._first_enty_name] = cnt
    
    @property
    def relay(self) -> int:
        return self._value[self._second_entry_name]
    
    @relay.setter
    def relay(self, cnt: int):
        self._value[self._second_entry_name] = cnt


class Association(_Base, HasClubs):
    NO_STRING: str = 'LSV-Nr.: '
    
    def __init__(self, name: str, dsv_id: int = 0):
        self.name = name
        self.dsv_id = dsv_id
        HasClubs.__init__(self)
        _Base.__init__(self)
        pass
    
    def __str__(self) -> str:
        result = self.name
        if self.dsv_id != '':
            if self.dsv_id != 0:
                result += fr' ({self.NO_STRING}{self.dsv_id})'
            else:
                result += fr' ({self.dsv_id})'
        if len(self.clubs) > 0:
            result += fr' [{len(self.clubs)}]'
        return result
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}('
        tmp += fr'{self.name}'
        if self.dsv_id > 0:
            tmp += fr', dsv_id={self.dsv_id}'
        return tmp + ')'
    
    # def __del__(self):
    #     _Base.__del__(self)
    
    @classmethod
    def from_string(cls, string: str):
        local_id = 0
        parts = string.split('(')
        if len(parts) == 2:
            local_id = int(parts[1][:-1].replace(cls.NO_STRING, ''))

        name = parts[0].strip()

        # Check if association still there
        name_list = [x.name for x in cls._registry.get_all(cls)]
        if name in name_list:
            association = cls._registry.get_all(cls)[name_list.index(name)]
        else:
            association = cls(name, local_id)

        return association


class Club(_Base, HasAthletes, HasOccurrence, HasJudges):
    
    def __init__(self, name: str, dsv_id: str = '', association: [Association, None] = None):
        self.name = name
        self.dsv_id = dsv_id
        
        self.participants: Participants = Participants()
        self.starts_by_segments: list = []
        self.__association = None
        self.association = association
        
        HasAthletes.__init__(self)
        HasOccurrence.__init__(self)
        HasJudges.__init__(self)
        _Base.__init__(self)
        pass
    
    def __str__(self) -> str:
        result = self.name
        if self.dsv_id != '':
            if self.dsv_id.isnumeric():
                result += fr' (DSV-Id: {self.dsv_id})'
            else:
                result += fr' ({self.dsv_id})'
        if not self.participants.is_empty():
            result += fr' [ {self.participants} ]'
        return result
    
    def __del__(self):
        self.association = None
        _Base.__del__(self)
        
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}('
        tmp += fr'{self.name}'
        if self.dsv_id:
            tmp += fr', dsv_id={self.dsv_id}'
        if self.association:
            tmp += fr', association={self.association}'
        return tmp + ')'
    
    def __eq__(self, other: str):
        return self.name == other
    
    def __ne__(self, other: str):
        return not self.__eq__(other)
    
    @property
    def association(self):
        return self.__association
    
    @association.setter
    def association(self, value: [Association, None]):
        self.__association = self.__setter(value, self.__association)
    
    @property
    def starts(self) -> Starts:
        single = 0
        relay = 0
        for start in self.starts_by_segments:
            if type(start) == Starts:
                single += start.single
                relay += start.relay
        return Starts([single, relay])
    
    def __setter(self, value, obj):
        if value and obj:
            obj.remove_club(self)
            value.add_club(self)
        elif value:
            value.add_club(self)
        elif obj:
            obj.remove_club(self)
        return value


class Section(_Base, HasCompetitions, HasJudges):
    def __init__(self, no: int):
        self.no: int = int(no)
        
        HasCompetitions.__init__(self)
        HasJudges.__init__(self)
        _Base.__init__(self)
        
    def __str__(self):
        return fr'Abschnitt {self.no}'
    
    def __repr__(self):
        return fr'{self.__class__.__name__}({self.no})'
    
    # def __del__(self):
    #     _Base.__del__(self)
    

class Judge(_Base):
    def __init__(self, position: str, name: str = '-', club: [Club, None] = None, section: [Section,None] = None):
        self.name = name
        self.position = position
        self._section = None
        self._club = None
        self.section = section
        self.club = club
        
        _Base.__init__(self)
        
    def __str__(self):
        no = 0
        club =''
        if self._section:
            no = self._section.no
        if self.club:
            club = fr' {self.club.name}'
        
        return fr'[{no}] {self.position} ({self.name}){club}'
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}('
        tmp += fr'{self.position}, '
        tmp += fr'{self.name}'
        if self.club:
            tmp += fr', club={self.club}'
        if self.section:
            tmp += fr', section={self.section}'
        return tmp + ')'
    
    def __del__(self):
        self.section = None
        self.club = None
        _Base.__del__(self)
    
    @property
    def section(self) -> [Section, None]:
        return self._section
    
    @section.setter
    def section(self, value: [Section, None]):
        self._section = self.__setter(value, self._club)
    
    @property
    def club(self) -> [Club, None]:
        return self._club
    
    @club.setter
    def club(self, value: [Club, None]):
        self._club = self.__setter(value, self._club)
    
    def __setter(self, value, obj):
        if value and obj:
            obj.remove_judge(self)
            value.add_judge(self)
        elif value:
            value.add_judge(self)
        elif obj:
            obj.remove_judge(self)
        return value

class Year(_Base, HasOccurrence, HasAthletes):
    def __init__(self, year: int):
        self._year: int = int(year)
        
        HasOccurrence.__init__(self)
        HasAthletes.__init__(self)
        _Base.__init__(self)
    
    def __str__(self):
        return str(self._year)
    
    def __repr__(self):
        return fr'{self.__class__.__name__}({str(self)})'
    
    # def __del__(self):
    #     _Base.__del__(self)
    
    @property
    def year(self):
        return self._year

class Athlete(_Base, HasLanes, HasOccurrence):
    def __init__(self, name: str, year: [Year, None], club: [Club, None] = None):
        self.name: str = str(name)
        self._year: [Year, None] = None
        if year:
            self.year = year
        self._club: [Club, None] = None
        if club:
            self.club = club
            
        HasOccurrence.__init__(self)
        HasLanes.__init__(self)
        _Base.__init__(self)
    
    def __str__(self):
        club_text = ''
        if self.club:
            club_text = fr' {self.club.name}'
        return fr'{self.name} ({self.year}){club_text}'
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}('
        tmp += fr'{self.name}'
        if self.year:
            tmp += fr', year={self.year}'
        if self.club:
            tmp += fr', club={self.club}'
        return tmp + ')'
    
    def __del__(self):
        self.year = None
        self.club = None
        _Base.__del__(self)
    
    @property
    def year(self) -> [Year, None]:
        return self._year
    
    @year.setter
    def year(self, value: [Year, None]):
        self._year = self.__setter(value, self._year)
    
    @property
    def club(self) -> [Club, None]:
        return self._club
    
    @club.setter
    def club(self, value: [Club, None]):
        self._club = self.__setter(value, self._club)
    
    def __setter(self, value, obj):
        if value and obj:
            obj.remove_athlete(self)
            value.add_athlete(self)
        elif value:
            value.add_athlete(self)
        elif obj:
            obj.remove_athlete(self)
        return value

class Competition(_Base, HasHeats):
    
    def __init__(self, *, no: int, discipline: str, distance: int, sex: str, section: [Section, None] = None, text: str = '',
                 repetition: int = 0, heat_cnt: int = 0, final: bool = False):
        self.no: int = int(no)
        self._section: [Section, None] = None
        self.section = section
        self.discipline: str = str(discipline)
        self.distance: int = int(distance)
        self.repetition: int = int(repetition)
        self.text: str = str(text)
        self.sex: str = str(sex)
        self.heat_cnt: int = int(heat_cnt)
        self._final: bool = bool(final)
        
        HasHeats.__init__(self)
        _Base.__init__(self)
    
    def __str__(self):
        return self.name()
    
    def __repr__(self):
        if self.text:
            return fr'{self.__class__.__name__}({self.text})'
        else:
            tmp = fr'{self.__class__.__name__}('
            tmp += fr'no={self.no}, '
            if self.repetition > 0:
                tmp += fr'repetition={self.repetition}, '
            tmp += fr'distance={self.distance}, '
            tmp += fr'discipline={self.discipline}'
        return tmp + ')'
    
    def __del__(self):
        self.section = None
        _Base.__del__(self)
    
    def name(self, with_heat: bool = False) -> str:
        if self.text != '':
            if with_heat:
                return self.text
            else:
                parts = self.text.split('(')
                if 'Läufe' in parts[len(parts) - 1] or 'Lauf' in parts[len(parts) - 1]:
                    parts = parts[0:len(parts) - 1]
                return str('('.join(parts)).strip()
        else:
            result: str = fr'Wettkampf {self.no} - '
            if self.repetition != 0:
                result += fr'{self.repetition}x'
            result += fr'{self.distance}m {self.discipline} {self.sex}'
            if with_heat:
                if len(self.heats) != 1:
                    result += fr' ({self.heat_cnt} Läufe)'
                else:
                    result += fr' ({self.heat_cnt} Lauf)'
            return result
    
    def is_final(self) -> bool:
        return self._final
    
    def is_relay(self) -> bool:
        return self.repetition > 0
    
    @property
    def section(self) -> Section:
        return self._section
    
    @section.setter
    def section(self, value: [None, Section]):
        self._section = self.__setter(value, self._section)
        
    def __setter(self, value, obj):
        # in case we change value
        if value and obj:
            obj.remove_competition(self)
            value.add_competition(self)
        elif value:
            value.add_competition(self)
        elif obj:
            obj.remove_competition(self)
        return value
    
    @classmethod
    def from_string(cls, string: str, section: [Section, None] = None):
        pattern = re.compile(r'Wettkampf (\d+) - (\d+|\d+x\d+)m (.+?) (männlich|weiblich|mixed)(.*)')
        sub_pat = re.compile(r'.*\((\d+) (Läufe|Lauf)\)')
        
        match = pattern.match(string)
        if match:
            parts = match.group(2).split('x')
            if len(parts) == 2:
                distance = int(parts[1])
                repetition = int(parts[0])
            else:
                distance = int(parts[0])
                repetition = 0
            
            heat_cnt: int = 0
            sub_match = sub_pat.match(match.group(5))
            if sub_match:
                heat_cnt = int(sub_match.group(1))
            
            is_final: bool = FINAL_STR in string

            no = int(match.group(1))
            # check if in list
            no_list = [x.no for x in cls._registry.get_all(cls)]
            if no in no_list:
                competition = cls._registry.get_all(cls)[no_list.index(no)]
            else:
                competition = cls(no=no, distance=distance, discipline=match.group(3), sex=match.group(4),
                       text=string, section=section, repetition=repetition, heat_cnt=heat_cnt, final=is_final)
            return competition
        else:
            return None


class Heat(_Base, HasLanes):
    
    def __init__(self, no: int, competition: [Competition, None] = None):
        self.no: int = int(no)
        # self._lanes: list[Lane] = []
        if competition is None:
            self._competition = None
        else:
            self.competition = competition
        
        HasLanes.__init__(self)
        _Base.__init__(self)
    
    def __str__(self):
        c_no: int = 0
        if self.competition:
            c_no = self.competition.no
        return fr'WK{c_no:02d}/L{self.no:02d} [{len(self._lanes)}]'
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}({self.no}'
        if self.competition:
            tmp += fr', {self.competition}'
        return tmp + ')'
    
    def __del__(self):
        self.competition = None
        _Base.__del__(self)
    
    @property
    def competition(self) -> [Competition, None]:
        return self._competition
    
    @competition.setter
    def competition(self, value: [Competition, None]):
        self._competition = self.__setter(value, self._competition)
    
    def __setter(self, value, obj):
        if value and obj:
            obj.remove_heat(self)
            value.add_heat(self)
        elif value:
            value.add_heat(self)
        elif obj:
            obj.remove_heat(self)
        return value

    
    @classmethod
    def from_string(cls, string: str):
        pattern = re.compile(r'Lauf (\d+)(.*)')
        match = pattern.match(string)
        if match:
            return cls(match.group(1))
        else:
            return None


class Lane(_Base):
    def __init__(self, no: int, time: datetime.time, athlete: Athlete, heat: [Heat, None]):
        self.no: int = int(no)
        self.time: datetime.time = time
        self._athlete: [None, Athlete] = None
        self.athlete: Athlete = athlete
        self._heat: [Heat, None] = None
        
        if heat:
            self.heat = heat
            
        _Base.__init__(self)
    
    def __str__(self):
        return fr'Bahn {self.no} - {str(self.athlete)} - {self.time_str}'
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}({self.no}, {self.time_str}, {self.athlete}'
        if self.heat:
            tmp += fr', {self.heat.no}'
        return tmp + ')'
        
        
    
    def __del__(self):
        self.heat = None
        self.athlete = None
        _Base.__del__(self)
        
    @property
    def time_str(self) -> str:
        return fr'{self.time.strftime("%M:%S,")}{int(self.time.strftime("%f"))/10000}'
    
    @property
    def heat(self) -> Heat:
        return self._heat
    
    @heat.setter
    def heat(self, value: [Heat, None]):
        self._heat = self.__setter(value, self._heat)
    
    @property
    def athlete(self) -> Athlete:
        return self._athlete
    
    @athlete.setter
    def athlete(self, value: [Athlete, None]):
        self._athlete = self.__setter(value, self._athlete)
    
    def __setter(self, value, obj):
        if value and obj:
            obj.remove_lane(self)
            value.add_lane(self)
        elif value:
            value.add_lane(self)
        elif obj:
            obj.remove_lane(self)
        return value
