import re
import datetime
from os.path import split


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
    
    # def __setitem__(self, key, value):
    #     if not (key == 'male' or key == 'female' and type(value) is int):
    #         raise ValueError
    #     else:
    #         self.__value[key] = value
    #
    # def __getitem__(self, item):
    #     if not (item == 'male' or item == 'female'):
    #         raise ValueError
    #     else:
    #         return self.__value[item]
    
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
    
    def toList(self) -> list:
        return [self._value['female'], self._value['male']]
    
    def toDict(self) -> dict:
        return self._value
    
    def isEmpty(self) -> bool:
        return self.cnt == 0
    
    @property
    def cnt(self) -> int:
        return sum(self.toList())
    
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


class Association:
    NO_STRING: str = 'LSV-Nr.: '
    
    def __init__(self, name: str, id: int = 0):
        self.name = name
        self.id = id
        self.clubs = []
        pass
    
    def __str__(self) -> str:
        result = self.name
        if self.id != '':
            if self.id != 0:
                result += fr' ({self.NO_STRING}{self.id})'
            else:
                result += fr' ({self.id})'
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


class Club:
    
    def __init__(self, name: str, id: str = ''):
        self.name = name
        self.id = id
        
        self.participants: Participants = Participants()
        self.segments: list = []
        self.occurrence: list = []
        
        self.__association: [Association, None] = None
        pass
    
    def __str__(self) -> str:
        result = self.name
        if self.id != '':
            if self.id.isnumeric():
                result += fr' (DSV-Id: {self.id})'
            else:
                result += fr' ({self.id})'
        if not self.participants.isEmpty():
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
    def association(self, value: Association):
        if self.__association is not None:
            self.__association.clubs.remove(self.__association)
        
        self.__association = value
        self.__association.clubs.append(self)


class Athlete:
    name: str
    year: int
    club: Club


class Competition:
    
    def __init__(self, *, no: int, discipline: str, distance: int, sex: str, section: int = 0, text: str = '', repetition: int = 0):
        self.no: int = no
        self.section: int = section
        self.discipline: str = discipline
        self.distance: int = distance
        self.repetition: int = repetition
        self.text: str = text
        self.sex: str = sex
        
        self._runs: list = []
        
    def __str__(self):
        return self.name()
        
    def name(self, run_cnt: bool = False) -> str:
        if self.text != '':
            if run_cnt:
                return self.text
            else:
                parts = self.text.split('(')
                if 'Läufe' in parts[len(parts)-1] or 'Lauf' in parts[len(parts)-1]:
                    parts = parts[0:len(parts)-1]
                return str('('.join(parts)).strip()
        else:
            result: str = fr'Wettkampf {self.no} - '
            if self.repetition != 0:
                result += fr'{self.repetition}x'
            result += fr'{self.distance}m {self.discipline} {self.sex}'
            if run_cnt:
                if len(self._runs) != 1:
                    result += fr' ({len(self._runs)} Läufe)'
                else:
                    result += fr' ({len(self._runs)} Lauf)'
            return result
    
    @property
    def runs(self) -> list:
        return self._runs
    
    def add_run(self, value):
        if not value in self._runs:
            self._runs.append(value)
            
    @staticmethod
    def from_string(string: str, section: int = 0):
        pattern = re.compile(r'Wettkampf (\d+) - (\d+|\d+x\d+)m (.+?) (männlich|weiblich)(.*)')
        match = pattern.match(string)
        if match:
            parts = match.group(2).split('x')
            if len(parts) == 2:
                distance = int(parts[1])
                repetition = int(parts[0])
            else:
                distance = int(parts[0])
                repetition = 0
                
            return Competition(no=int(match.group(1)), distance=distance, discipline=match.group(3), sex=match.group(4), text=string, section=0, repetition=repetition)
        else:
            return None
        
    


class Run:
    no: int
    
    _lanes: list
    _competition: Competition
    
    @property
    def competition(self) -> Competition:
        return self._competition
    
    @competition.setter
    def competition(self, value: Competition):
        if not self in value.runs:
            value.runs.append(value)
    
    @property
    def lanes(self) -> list:
        return self._lanes
    
    def add_lane(self, value):
        if not value in self._lanes:
            self._lanes.append(value)


class Lane:
    no: int
    time: datetime.time
    athlete: Athlete
    
    _run: Run
    
    @property
    def run(self) -> Run:
        return self._run
    
    @run.setter
    def run(self, value: Run):
        if not self in value.lanes:
            value.lanes.append(value)
