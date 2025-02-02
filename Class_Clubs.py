import re
import datetime

FINAL_STR: str = 'Finale'

#----- Base Class Area -----

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

# todo this name is wrong for starts
class Participants:
    def __init__(self, *args, **kwargs):
        self._value: dict = {'female': 0, 'male': 0}
        
        if len(args) == 0:
            # use kwargs
            self.__check_kwargs(kwargs)
        elif len(args) == 1:
            if type(args[0]) is dict:
                self.__check_kwargs(args[0])
            elif type(args[0]) is list and len(args[0]) <= 2:
                self.__check_list(args[0])
            elif type(args[0]) is int:
                self._value['male'] = args[0]
            else:
                raise ValueError
        elif len(args) == 2:
            self.__check_list(list(args))
        else:
            raise ValueError
    
    def __str__(self):
        return fr'{self._value["female"]} / {self._value["male"]}'
 
    def __check_list(self, args: list):
        for i in range(0, len(args)):
            if type(args[i]) is int:
                self._value[list(self._value.keys())[i]] = args[i]
            else:
                raise ValueError
    
    def __check_kwargs(self, kwargs: dict):
        if len(kwargs) != 0:
            for key, value in kwargs.items():
                # self[key] = value
                if not (key == 'male' or key == 'female' and type(value) is int):
                    raise ValueError
                else:
                    self._value[key] = value
    
    def to_list(self) -> list:
        return [self._value['female'], self._value['male']]
    
    def to_dict(self) -> dict:
        return self._value
    
    def is_empty(self) -> bool:
        return self.cnt == 0
    
    @property
    def cnt(self) -> int:
        return sum(self.to_list())
    
    @property
    def male(self):
        return self._value['male']
    
    @male.setter
    def male(self, cnt: int):
        self._value['male'] = cnt
    
    @property
    def female(self):
        return self._value['female']
    
    @female.setter
    def female(self, cnt: int):
        self._value['female'] = cnt


class Association(HasClubs):
    NO_STRING: str = 'LSV-Nr.: '
    
    def __init__(self, name: str, dsv_id: int = 0):
        HasClubs.__init__(self)
        self.name = name
        self.dsv_id = dsv_id
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
    
    @classmethod
    def from_string(cls, string: str):
        local_id = 0
        parts = string.split('(')
        if len(parts) == 2:
            local_id = int(parts[1][:-1].replace(cls.NO_STRING, ''))
        
        return Association(parts[0].strip(), local_id)


class Club(HasAthletes, HasOccurrence):
    
    def __init__(self, name: str, dsv_id: str = '', association: [Association, None] = None):
        HasAthletes.__init__(self)
        HasOccurrence.__init__(self)
        self.name = name
        self.dsv_id = dsv_id
        
        self.participants: Participants = Participants()
        self.segments: list = []
        self.__association = None
        self.association = association
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
        
    def __setter(self, value, obj):
        if value:
            value.add_club(self)
        elif obj:
            obj.remove_club(self)
        return value


class Year(HasOccurrence, HasAthletes):
    def __init__(self, year: int):
        HasOccurrence.__init__(self)
        HasAthletes.__init__(self)
        self._year: int = int(year)
        
    @property
    def year(self):
        return self._year
    
    def __str__(self):
        return str(self._year)


class Athlete(HasLanes, HasOccurrence):
    def __init__(self, name: str, year: [Year, None], club: [Club, None] = None):
        HasOccurrence.__init__(self)
        HasLanes.__init__(self)
        self.name: str = str(name)
        self._year: [Year, None] = None
        if year:
            self.year = year
        self._club: [Club, None] = None
        if club:
            self.club = club
    
    def __str__(self):
        club_text = ''
        if self.club:
            club_text = fr' {self.club.name}'
        return fr'{self.name} ({self.year}){club_text}'

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
        if value:
            value.add_athlete(self)
        elif obj:
            obj.remove_athlete(self)
        return value
        


class Competition(HasHeats):
    
    def __init__(self, *, no: int, discipline: str, distance: int, sex: str, section: int = 0, text: str = '',
                 repetition: int = 0, heat_cnt: int = 0, final: bool = False):
        HasHeats.__init__(self)
        self.no: int = int(no)
        self.section: int = int(section)
        self.discipline: str = str(discipline)
        self.distance: int = int(distance)
        self.repetition: int = int(repetition)
        self.text: str = str(text)
        self.sex: str = str(sex)
        self.heat_cnt: int = int(heat_cnt)
        self._final: bool = bool(final)
    
    def __str__(self):
        return self.name()
    
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
    
    def is_relay(self)-> bool:
        return self.repetition > 0
    
    @classmethod
    def from_string(cls, string: str, section: int = 0):
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
            
            return cls(no=int(match.group(1)), distance=distance, discipline=match.group(3), sex=match.group(4),
                       text=string, section=section, repetition=repetition, heat_cnt=heat_cnt, final=is_final)
        else:
            return None


class Heat(HasLanes):
    
    def __init__(self, no: int, competition: [Competition, None] = None):
        HasLanes.__init__(self)
        self.no: int = int(no)
        # self._lanes: list[Lane] = []
        if competition is None:
            self._competition = None
        else:
            self.competition = competition
    
    def __str__(self):
        c_no: int = 0
        if self.competition:
            c_no = self.competition.no
        return fr'WK{c_no:02d}/L{self.no:02d} [{len(self._lanes)}]'
    
    @property
    def competition(self) -> [Competition, None]:
        return self._competition
    
    @competition.setter
    def competition(self, value: [Competition, None]):
        if value:
            value.add_heat(self)
        else:
            self._competition.remove_heat(self)
        self._competition = value
    
    @classmethod
    def from_string(cls, string: str):
        pattern = re.compile(r'Lauf (\d+)(.*)')
        match = pattern.match(string)
        if match:
            return cls(match.group(1))
        else:
            return None


class Lane:
    def __init__(self, no: int, time: datetime.time, athlete: Athlete, heat: [Heat, None]):
        self.no: int = int(no)
        self.time: datetime.time = time
        self._athlete: [None, Athlete] = None
        self.athlete: Athlete = athlete
        self._heat: [Heat, None] = None
        
        if heat:
            self.heat = heat
    
    def __str__(self):
        return fr'Bahn {self.no} - {str(self.athlete)} - {self.time}'
    
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
        if value:
            value.add_lane(self)
        elif obj:
            obj.remove_lane(self)
        return value
