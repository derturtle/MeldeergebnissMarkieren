import re
import datetime

from Class_Config import Config


class _Entry:
    """
    Represents an entry of a collection
    
    Methods:
    --------
    instance : dict
        Returns the actual instance of the collection
    name : str
        Name of the active collection
    available : list
        Return a list ob available collections
    create : bool
        Creates a new instance if instance didn't exist return it instance was created or not
    is_active(value) : bool
        Returns if the actual value it the active one
    exist(value) : bool
        Returns if the value exist in collection
    """
    
    def __init__(self, entry_name: [str, None] = None):
        """ Initializes a new _Entry instance.
        :type entry_name: [str, None]
        :param entry_name: Name of the entry
        """
        self._name = ''
        self._instance: dict = {}
        if entry_name:
            self.create(entry_name)
        else:
            self.create('default')
        pass
    
    @property
    def instance(self) -> dict:
        """ Returns the actual instance of the collection
        :return: The instance
        """
        return self._instance[self._name]
    
    @property
    def name(self) -> str:
        """ Returns the name of the active collection
        :return: Name
        """
        return self._name
    
    @name.setter
    def name(self, value: str):
        """
        Set the name of the active collection
        
        :type value: str
        :param value: Set the active collection if available
        """
        if value in list(self._instance.keys()):
            self._name = value
    
    def available(self) -> list:
        """ Return a list ob available collections
        :return: Returns a list of all available keys
        """
        return list(self._instance.keys())
    
    def create(self, value: str) -> bool:
        """ Creates a new instance if instance didn't exist return it instance was created or not
        :type value: str
        :param value: Creates a new collection with this value and set it active
        :return: True in case if it was successfully
        """
        if self.exist(value):
            return False
        else:
            self._instance[value] = {}
            self.name = value
            return True
    
    def is_active(self, value: str) -> bool:
        """ Returns if the actual value it the active one
        :type value: str
        :param value: Value to checked if it is active
        :return: Is the name is active
        """
        return self.name == value
    
    def exist(self, value: str) -> bool:
        """ Returns if the actual value exist
        :type value: str
        :param value: Value to be checked if in collection
        :return: Is the name in collection
        """
        return value in list(self._instance.keys())


class _Registry:
    """
    Represents a registry which stores created classes

    Methods:
    --------
    add(obj):
        Add object to the instance
    remove(obj):
        Removes the object from the instance and delete it
    get_all(obj_type = None) : dict
        Return a collection with the specific object type
    """
    
    def __init__(self, name: [str, None] = None):
        """ Initializes a new registry
        :type name: [str, None]
        :param name: Name of the registry [default: None]
        """
        self.entry: _Entry = _Entry(name)
    
    def add(self, obj):
        """ Add an object to the registry
        :param obj: Object to add to the registry
        """
        self.entry.instance.setdefault(type(obj), []).append(obj)
    
    def remove(self, obj):
        """ Removes an object from the registry (if it in)
        :param obj: Object to be removed from registry
        """
        obj_list = self.entry.instance.get(type(obj), [])
        if obj in obj_list:
            obj_list.remove(obj)
            # In case list is empty, remove type from dict
            if not obj_list:
                del self.entry.instance[type(obj)]
    
    def get_all(self, obj_type=None) -> [dict, list]:
        """ Returns a list of all the objects from a type or the hole instance
        :param obj_type: Type of object type(obj)
        :return: The instance or a list of objects
        """
        if obj_type:
            return self.entry.instance.get(obj_type, [])
        return self.entry.instance
    
    def __repr__(self):
        return f"Registry[{self.entry.name}]({self.entry.instance})"


class _Base:
    """
    Represents the base class of all club objects
    
    Methods:
    --------
    remove:
        delete this object
    """
    # Class to store all the created object in
    _registry: [None, _Registry] = None
    # Config class needed for some functions
    _config: [None, Config] = None
    
    def __init__(self, name: str = '', config: [Config, None] = None):
        """ Base class of all club objects
        :param name: Name of the registry [default = '']
        :param config: Config class which could be set [default = None]
        """
        # Set name
        self._name = name
        # If still no registry available
        if not _Base._registry:
            # Create registry
            _Base._registry = _Registry(name)
        # 2. Registry there and name not empty
        elif name:
            # Create new registry
            _Base._registry.entry.create(name)
        
        # Check if no config available
        if not config:
            # Check if no config is stored
            if not _Base._config:
                # Create config
                config = Config()
            # config stored
            else:
                # use stored config
                config = _Base._config
        # Set config
        _Base._config = config
        # Add obj to registry
        _Base._registry.add(self)
        # Set name
        self._name = _Base._registry.entry.name
    
    def __del__(self):
        _Base._registry.remove(self)
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"
    
    def remove(self):
        """ Removes value from registry """
        self.__del__()


class Collection(_Base):
    """
    Represents an object with stored all club classes
    
    Methods:
    --------
    associations : list
        Returns a list of all created association objects
    clubs : list
        Returns a list of all created club objects
    sections : list
        Returns a list of all created section objects
    years : list
        Returns a list of all created year objects
    judges : list
        Returns a list of all created judge objects
    athletes : list
        Returns a list of all created athlete objects
    heats : list
        Returns a list of all created heat objects
    lanes : list
        Returns a list of all created lane objects
    config : Config
        Returns the configuration
    """
    
    def __init__(self, name: str, config: [Config, None] = None):
        """ Initializes a new collection of classes
        :type name: str
        :param name: Name of the collection
        :type config: [Config, None]
        :param config: Set the configuration for this collection [default = None]
        """
        # Set name
        self._name = name
        # Initializes base class
        _Base.__init__(self, name, config)
    
    @property
    def associations(self) -> list:
        """ Returns a list of all created association objects
        :return: A list of all associations
        """
        return self._get_list(Association)
    
    @property
    def clubs(self) -> list:
        """ Returns a list of all created club objects
        :return: A list of all clubs
        """
        return self._get_list(Club)
    
    @property
    def sections(self) -> list:
        """ Returns a list of all created section objects
        :return: A list of all sections
        """
        return self._get_list(Section)
    
    @property
    def years(self) -> list:
        """ Returns a list of all created year objects
        :return: A list of all years
        """
        return self._get_list(Year)
    
    @property
    def judges(self) -> list:
        """ Returns a list of all created judge objects
        :return: A list of all judges
        """
        return self._get_list(Judge)
    
    @property
    def athletes(self) -> list:
        """ Returns a list of all created athlete objects
        :return: A list of all athletes
        """
        return self._get_list(Athlete)
    
    @property
    def competitions(self) -> list:
        """ Returns a list of all created competition objects
        :return: A list of all competitions
        """
        return self._get_list(Competition)
    
    @property
    def heats(self) -> list:
        """ Returns a list of all created heat objects
        :return: A list of all heats
        """
        return self._get_list(Heat)
    
    @property
    def lanes(self) -> list:
        """ Returns a list of all created lane objects
        :return: A list of all lanes
        """
        return self._get_list(Lane)
    
    @property
    def config(self) -> [Config, None]:
        """ Returns the configuration for this collection
        :return: The actual configuration object
        """
        return _Base._config
    
    @config.setter
    def config(self, value: [Config, None]):
        """ Set a new configuration to this collection """
        if value:
            _Base._config = value
    
    def _get_list(self, obj_type) -> list:
        """ Returns a specific object type list
        :param obj_type: Type of object
        :return: A list of objects with the obj_type
        """
        # Set collection to the default one
        self._set_active()
        # Get the list
        ret_list = self._registry.get_all(obj_type)
        # If list is instance (type not in instance)
        if ret_list == self._registry.entry.instance:
            # return empty list
            return []
        else:
            # return list
            return ret_list
    
    def _set_active(self):
        """ Set actual collection to the active one """
        # Check if collection is not active
        if not self._registry.entry.is_active(self._name):
            # Set collection to active one
            self._registry.entry.name = self._name
    
    def __str__(self) -> str:
        return fr'Collection({self._name})'


class SpecialCollection(Collection):
    """
    Represents an object with stored all club classes
    
    Methods:
    --------
    competition_by_no(value) : [Competition, None]
        Return a competition class by its number
    competition_by_no(value) : dict
        Returns a dictionary of competitions objects with number as key
    sections_by_no(value): [Section, None]
        Return a section class by its number
    sections_dict : dict
        Returns a dictionary of section objects with number as key
    club_by_name : [Club, None]
        Returns a club by it name
    club_dict : dict
        Returns a dictionary of club objects with name as key
    athletes_by_name : [list, None]
        Returns a list athletes by it name
    athletes_by_year : [list, None]
        Returns a list athletes by year
    athlete_by_club : [list, None]
        Returns a list athletes by club
    athletes_dict : dict
        Returns a dictionary of athletes objects with the represent str as key
    get_year : [Year, None]
        Returns the year object by its number
    """
    
    def competition_by_no(self, value: int):
        """ Return a competition class by its number
        :type value: int
        :param value: Number of the competition to be returned
        :return: A competition where the number is value
        """
        return self._by_int(value, self.competitions, 'no')
    
    def competitions_dict(self) -> dict:
        """ Returns a dictionary of competition objects with number as key
        :return: A dictionary with all Competitions
        """
        return dict(map(lambda x: (x.no, x), self.competitions))
    
    def sections_by_no(self, value: int):
        """ Return a section class by its number
        :type value: int
        :param value: Number of the competition to be returned
        :return: A Section where the number is value
        """
        return self._by_int(value, self.sections, 'no')
    
    def sections_dict(self) -> dict:
        """ Returns a dictionary of section objects with number as key
        :return: A dictionary of all Sections
        """
        return dict(map(lambda x: (x.no, x), self.sections))
    
    def club_by_name(self, value: str):
        """ Returns a club by it name
        :type value: str
        :param value: Name of the club
        :return: A Club with name == value
        """
        return self._by_str(value, self.clubs, 'name')
    
    def clubs_dict(self):
        """ Returns a dictionary of club objects with name as key
        :return: A dictionary of all Clubs
        """
        return dict(map(lambda x: (x.name, x), self.clubs))
    
    def athletes_by_name(self, value: str) -> [list, None]:
        """ Returns a list athletes by it name
        :type value: str
        :param value: Name of the athlete
        :return: A list of all athletes with the name
        """
        return self._by_str(value, self.athletes, 'name', False)
    
    def athletes_by_year(self, value: int) -> [list, None]:
        """ Returns a list of athletes by year
        :type value : int
        :param value: Number of year
        :return: A list of all athletes from the Year with the value
        """
        # get year
        year = self.get_year(value)
        if year:
            # return list of athletes (belongs to year)
            return year.athletes
        return None
    
    def athlete_by_club(self, value: str) -> [list, None]:
        """ Returns a list of athletes by club
        :param value: Name of the Club
        :return: A list of all athletes from the Club with the name value
        """
        club = self.club_by_name(value)
        if club:
            return club.athletes
        return None
    
    def athletes_dict(self) -> dict:
        """ Returns a dictionary of athletes objects with represent str as key
        :return: A dictionary of all athletes
        """
        return dict(map(lambda x: (str(x), x), self.athletes))
    
    def get_year(self, year: int):
        """
        Returns the year object by its number
        
        :param year: The year
        :return: A Year object with the year no = value or None
        """
        return self._by_int(year, self.years, 'year')
    
    @staticmethod
    def _by_int(value: int, objects: list, attr: str):
        """ Returns an object by its integer property
        :type value: int
        :param value: Value to be searched for
        :type objects: list
        :param objects: Objects to be searched in
        :type: str
        :param attr: Name of property to compare with
        :return A subset of the objects
        :raise ValueError: In case type is not int
        """
        # Check type
        if type(value) != int:
            raise ValueError
        # If object is not empty
        if objects:
            # Get a list of values
            values = [item for item in objects if getattr(item, attr) == value]
            if values:
                # If value exists return first one
                return values[0]
        return None
    
    @staticmethod
    def _by_str(value: str, objects: list, attr: str, single_obj: bool = True):
        """ Returns an object by its string property
        :type value: str
        :param value: Value to be searched for
        :type objects: list
        :param objects: Objects to be searched in
        :type attr: str
        :param attr: Name of property to compare with
        :type single_obj: bool
        :param single_obj: If a list to be returned or only the first value
        :return A subset of the objects
        :raise ValueError: In case type is not int
        """
        # Check type
        if type(value) != str:
            raise ValueError
        # If object is not empty
        if objects:
            # Get a list of values
            values = [item for item in objects if getattr(item, attr) == value]
            if values:
                if single_obj:
                    # If value exists and a single object should be returned, return first one
                    return values[0]
                else:
                    # If value exists return list
                    return values
        return None


# ----- Base Class Area -----

class HasOccurrence:
    """
    Represents a class which has a list of occurrences

    Methods:
    --------
    occurrence : list
        Returns a list of occurrences
    add_occurrence
        Add an occurrence to list
    remove_occurrence
        Removes an occurrence from list
    """
    
    def __init__(self):
        """ Initializes a new HasOccurrence class """
        self._occurrence: list = []
    
    @property
    def occurrence(self) -> list:
        """ Returns the occurrence list
        :return: The occurrence list
        """
        return self._occurrence
    
    def add_occurrence(self, value):
        """ Add occurrence to list
        :param value: Value add to the list
        """
        if not value in self._occurrence:
            self._occurrence.append(value)
    
    def remove_occurrence(self, value):
        """ Remove occurrence from list
        :param value: Value remove from list
        """
        if value in self._occurrence:
            self._occurrence.remove(value)


class HasLanes:
    """
    Represents a class which has a list of lanes

    Methods:
    --------
    lanes : list
        Returns a list of lanes
    add_lane
        Add a lane to list
    remove_lane
        Removes a lane from list
    """
    
    def __init__(self):
        """ Initializes a new HasLanes class """
        self._lanes: list = []
    
    @property
    def lanes(self) -> list:
        """ Returns the lane list
        :return: The lane list
        """
        return self._lanes
    
    def add_lane(self, value):
        """ Add lane to list
        :param value: Value add to the list
        """
        if not value in self._lanes:
            self._lanes.append(value)
    
    def remove_lane(self, value):
        """ Remove lane from list
        :param value: Value remove from list
        """
        if value in self._lanes:
            self._lanes.remove(value)


class HasHeats:
    """
    Represents a class which has a list of heats

    Methods:
    --------
    heats : list
        Returns a list of heats
    add_heat
        Add a heat to list
    remove_heat
        Removes a heat from list
    """
    
    def __init__(self):
        """ Initializes a new HasHeats class """
        self._heats: list = []
    
    @property
    def heats(self) -> list:
        """ Returns the heat list
        :return: The heat list
        """
        return self._heats
    
    def add_heat(self, value):
        """ Add heat to list
        :param value: Value add to the list
        """
        if not value in self._heats:
            self._heats.append(value)
    
    def remove_heat(self, value):
        """ Remove heat from list
        :param value: Value remove from list
        """
        if value in self._heats:
            self._heats.remove(value)


class HasClubs:
    """
    Represents a class which has a list of clubs

    Methods:
    --------
    clubs : list
        Returns a list of clubs
    add_club
        Add a club to list
    remove_club
        Removes a club from list
    """
    
    def __init__(self):
        """ Initializes a new HasClubs class """
        self._clubs: list = []
    
    @property
    def clubs(self) -> list:
        """ Returns the club list
        :return: The club list
        """
        return self._clubs
    
    def add_club(self, value):
        """ Add club to list
        :param value: Value add to the list
        """
        if not value in self._clubs:
            self._clubs.append(value)
    
    def remove_club(self, value):
        """ Remove club from list
        :param value: Value remove from list
        """
        if value in self._clubs:
            self._clubs.remove(value)


class HasAthletes:
    """
    Represents a class which has a list of athletes

    Methods:
    --------
    athletes : list
        Returns a list of athletes
    add_athlete
        Add an athlete to list
    remove_athlete
        Removes an athlete from list
    """
    
    def __init__(self):
        """ Initializes a new HasAthletes class """
        self._athletes: list = []
    
    @property
    def athletes(self) -> list:
        """ Returns the athlete list
        :return: The athlete list
        """
        return self._athletes
    
    def add_athlete(self, value):
        """ Add athlete to list
        :param value: Value add to the list
        """
        if not value in self._athletes:
            self._athletes.append(value)
    
    def remove_athlete(self, value):
        """ Remove athlete from list
        :param value: Value remove from list
        """
        if value in self._athletes:
            self._athletes.remove(value)


class HasJudges:
    """
    Represents a class which has a list of judges

    Methods:
    --------
    judges : list
        Returns a list of judges
    add_judge
        Add a judge to list
    remove_judge
        Removes a judge from list
    """
    
    def __init__(self):
        """ Initializes a new HasJudges class """
        self._judges: list = []
    
    @property
    def judges(self) -> list:
        """ Returns the judge list
        :return: The judge list
        """
        return self._judges
    
    def add_judge(self, value):
        """ Add judge to list
        :param value: Value add to the list
        """
        if not value in self._judges:
            self._judges.append(value)
    
    def remove_judge(self, value):
        """ Remove judge from list
        :param value: Value remove from list
        """
        if value in self._judges:
            self._judges.remove(value)


class HasCompetitions:
    """
    Represents a class which has a list of competitions

    Methods:
    --------
    competitions : list
        Returns a list of competitions
    add_competition
        Add a competition to list
    remove_competition
        Removes a competition from list
    """
    
    def __init__(self):
        """ Initializes a new HasCompetitions class """
        self._competitions: list = []
    
    @property
    def competitions(self) -> list:
        """ Returns the competition list
        :return: The competition list
        """
        return self._competitions
    
    def add_competition(self, value):
        """ Add competition to list
        :param value: Value add to the list
        """
        if not value in self._competitions:
            self._competitions.append(value)
    
    def remove_competition(self, value):
        """ Remove competition from list
        :param value: Value remove from list
        """
        if value in self._competitions:
            self._competitions.remove(value)


class Quantity:
    """
    Represents a class which can hold q quantity of two different things
    
    Methods:
    --------
    to_list : list
        Return the values as list
    to_dict : dict
        Returns the values as dict
    is_empty : bool
        Return if there are no value stored
    cnt : int
        Returns the sum of the quantities
    """
    
    def __init__(self, first_enty_name: str, second_entry_name: str, args: tuple, kwargs: dict):
        """ Initializes a new Quantity class
        :type first_enty_name: str
        :param first_enty_name: Name of the first entry
        :type second_entry_name: str
        :param second_entry_name: Name of the second entry
        :raise ValueError: In case the args or kwargs are not the correct type
        """
        # set local variables
        self.__first_enty_name = first_enty_name
        self.__second_entry_name = second_entry_name
        self._value: dict = {first_enty_name: 0, second_entry_name: 0}
        
        # Check args
        if len(args) == 0:
            # use kwargs
            self.__check_kwargs(kwargs)
        elif len(args) == 1:
            # check types of args
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
        """ Check the inputs kwargs and set class values depending on input
        :type kwargs: dict
        :param kwargs: input dictionary
        """
        # Check len
        if len(kwargs) != 0:
            # loop over values and check if key is known
            for key, value in kwargs.items():
                if not (key == self.__first_enty_name or key == self.__second_entry_name and type(value) is int):
                    raise ValueError
                else:
                    self._value[key] = value
    
    def __check_list(self, args: list):
        """ In case the input is a list check it for correct values and set class values
        :type: list
        :param args: Input list
        """
        # loop over list
        for i in range(0, len(args)):
            # check type of list
            if type(args[i]) is int:
                self._value[list(self._value.keys())[i]] = args[i]
            else:
                raise ValueError
    
    def to_list(self) -> list:
        """ Returns a list of the stored values
        :return: A list of the values stored
        """
        return [self._value[self._first_enty_name], self._value[self._first_enty_name]]
    
    def to_dict(self) -> dict:
        """ Returns a dictionary where every stored value has a name
        :return: A dictionary where every value has a name
        """
        return self._value
    
    def is_empty(self) -> bool:
        """ Check if there are values stored
        :return: True in case min one value is stored
        """
        return self.cnt == 0
    
    @property
    def cnt(self) -> int:
        """ Returns the sum of all stored values
        :return: The sum of all stored values
        """
        return sum(self.to_list())
    
    @property
    def _first_enty_name(self) -> str:
        """ Name of first entry
        :return: Name of first entry
        """
        return self.__first_enty_name
    
    @property
    def _second_entry_name(self) -> str:
        """ Name of second entry
        :return: Name of second entry
        """
        return self.__second_entry_name


# ----- Working Classes -----

class Participants(Quantity):
    """
    Represents a participants class with 'female' and 'male'
    
    Attributes:
    -----------
    female : int
        Count of female participants
    male : int
        Count of male participants
    """
    
    def __init__(self, *args, **kwargs):
        """ Initializes a new Participants class """
        Quantity.__init__(self, 'female', 'male', args, kwargs)
    
    @property
    def female(self) -> int:
        """ Returns count of female participants
        :return: female count
        """
        return self._value[self._first_enty_name]
    
    @female.setter
    def female(self, cnt: int):
        """ Sets count of female participants
        :param cnt: No of participants
        """
        self._value[self._first_enty_name] = cnt
    
    @property
    def male(self) -> int:
        """ Returns count of male participants
        :return: male count
        """
        return self._value[self._second_entry_name]
    
    @male.setter
    def male(self, cnt: int):
        """ Sets count of male participants
        :param cnt: No of participants
        """
        self._value[self._second_entry_name] = cnt


class Starts(Quantity):
    """
    Represents starts with 'single' (starts) and 'relay' (starts)

    Attributes:
    -----------
    single : int
        Count of single starts
    relay : int
        Count of relay starts
    """
    
    def __init__(self, *args, **kwargs):
        """ Initializes a new Starts class """
        Quantity.__init__(self, 'single', 'relay', args, kwargs)
    
    @property
    def single(self) -> int:
        """ Returns count of single starts
        :return: single start count
        """
        return self._value[self._first_enty_name]
    
    @single.setter
    def single(self, cnt: int):
        """ Sets count of single starts
        :param cnt: No of single starts
        """
        self._value[self._first_enty_name] = cnt
    
    @property
    def relay(self) -> int:
        """ Returns count of relay starts
        :return: relay start count
        """
        return self._value[self._second_entry_name]
    
    @relay.setter
    def relay(self, cnt: int):
        """ Sets count of relays starts
        :param cnt: No of relays starts
        """
        self._value[self._second_entry_name] = cnt


class Association(_Base, HasClubs):
    """
    Represents an association

    Attributes:
    -----------
    name : str
        Name of association
    dsv_id : int
        DSV identification number
    """
    NO_STRING: str = 'LSV-Nr.: '
    
    def __init__(self, name: str, dsv_id: int = 0):
        """ Initializes a new Association class
        :type name: str
        :param name: Name of association
        :type dsv_id: int
        :param dsv_id: No of association
        """
        self.name: str = name
        self.dsv_id: int = dsv_id
        # Init base classes
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
    
    @classmethod
    def from_string(cls, string: str):
        """ Function returns an association object form a string (if possible)
        :param string:
        :return: An Association object
        """
        local_id = 0
        # split string by (
        parts = string.split('(')
        if len(parts) == 2:
            # remove string and use number for id
            local_id = int(parts[1][:-1].replace(cls.NO_STRING, ''))
        # name is part one
        name = parts[0].strip()
        # Check if association still there
        name_list = [x.name for x in cls._registry.get_all(cls)]
        if name in name_list:
            # Get association form collection
            return cls._registry.get_all(cls)[name_list.index(name)]
        else:
            # Create new association
            return cls(name, local_id)


class Club(_Base, HasAthletes, HasOccurrence, HasJudges):
    """
    Represents a club

    Attributes:
    -----------
    name : str
        Name of association
    dsv_id : str
        DSV identification number
    participants : Participants
        List of active athletes
    association : [Association, None]
        The Association the club belongs to
    starts_by_segments : list
        All starts of a Segment
        
    Methods:
    --------
    starts : Starts
        Returns the sum of all starts
    
    """
    
    def __init__(self, name: str, dsv_id: str = '', association: [Association, None] = None):
        """ Initializes a new Club class
        :type name: str
        :param name: Name of club
        :type dsv_id: str
        :param dsv_id: No of club
        :type association: [Association, None]
        :param association: The association the club belongs to
        """
        # Set Attributes
        self.name = name
        self.dsv_id = dsv_id
        self.participants: Participants = Participants()
        self.starts_by_segments: list = []
        self.__association = None
        self.association = association
        # Call base classes
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
    def association(self) -> [Association, None]:
        """ The association the club belongs to
        :return: The Association if available
        """
        return self.__association
    
    @association.setter
    def association(self, value: [Association, None]):
        """ Sets the association the club belongs to """
        self.__association = self.__setter(value, self.__association)
    
    @property
    def starts(self) -> Starts:
        """ Returns the sum of all starts
        :return: The sum of all starts of the club
        """
        single = 0
        relay = 0
        for start in self.starts_by_segments:
            if type(start) == Starts:
                single += start.single
                relay += start.relay
        return Starts([single, relay])
    
    def __setter(self, value: [Association, None], obj: [Association, None]):
        """ Function sets or removes the club from an association
        :type value: [Association, None]
        :param value: The Association object or none
        :type obj: [Association, None]
        :param obj: The Association object from the class [to set or remove from]
        :return: The Association to store
        """
        # Check if value and obj are valid
        if value and obj:
            # first remove club
            obj.remove_club(self)
            # the set new
            value.add_club(self)
        elif value:
            # only value is valid, add club
            value.add_club(self)
        elif obj:
            # only obj is valid, remove club from obj
            obj.remove_club(self)
        return value


class Section(_Base, HasCompetitions, HasJudges):
    """ Represents a section """
    
    def __init__(self, no: int):
        """ Initializes a new Section class
        :type no: int
        :param no: No of Section
        """
        self.no: int = int(no)
        
        HasCompetitions.__init__(self)
        HasJudges.__init__(self)
        _Base.__init__(self)
    
    def __str__(self):
        return fr'{_Base._config.pdf_values.segment} {self.no}'
    
    def __repr__(self):
        return fr'{self.__class__.__name__}({self.no})'


class Judge(_Base):
    """
    Represents a judge

    Attributes:
    -----------
    name : str
        Name of the judge
    position : str
        Position of the judge
    section : [Section, None]
        The Section in which the judge should work
    club : [Club, None]
        The club the judge belongs to
    """
    
    def __init__(self, position: str, name: str = '-', club: [Club, None] = None, section: [Section, None] = None):
        """ Initializes a new Judge class
        :type position: str
        :param position: Position of the judge
        :type name: str
        :param name: Name of judge
        :type club: [Club, None]
        :param club: The club the judge belongs to
        :type section: [Section, None]
        :param section: The section in which the judge works
        """
        self.name = name
        self.position = position
        self._section = None
        self._club = None
        self.section = section
        self.club = club
        
        _Base.__init__(self)
    
    def __str__(self):
        no = 0
        club = ''
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
        """ Return the section the judge works in
        :return The section the judge works in
        """
        return self._section
    
    @section.setter
    def section(self, value: [Section, None]):
        """ Set the section the judge works in """
        self._section = self.__setter(value, self._club)
    
    @property
    def club(self) -> [Club, None]:
        """ Return the club the judge belongs to
        :return The club the judge belongs to
        """
        return self._club
    
    @club.setter
    def club(self, value: [Club, None]):
        """ Sets the club the judge belongs to """
        self._club = self.__setter(value, self._club)
    
    def __setter(self, value, obj):
        """ Function sets or removes the club an object which belongs to the club
        :type value: [Club, Section, None]
        :param value: The set value
        :type obj: [Club, Section, None]
        :param obj: The object of the class
        :return: The value to store
        """
        # Check if value and obj are valid
        if value and obj:
            # first remove judge
            obj.remove_judge(self)
            # the set new
            value.add_judge(self)
        elif value:
            # only value is valid, add judge
            value.add_judge(self)
        elif obj:
            # only obj is valid, remove judge from obj
            obj.remove_judge(self)
        return value


class Year(_Base, HasOccurrence, HasAthletes):
    """
    Represents a year

    Methods:
    --------
    year : int
        The year
    """
    
    def __init__(self, year: int):
        """ Initializes a new Year class
        :param year: The number of the year
        """
        self._year: int = int(year)
        
        HasOccurrence.__init__(self)
        HasAthletes.__init__(self)
        _Base.__init__(self)
    
    def __str__(self):
        return str(self._year)
    
    def __repr__(self):
        return fr'{self.__class__.__name__}({str(self)})'
    
    @property
    def year(self):
        """ Returns the number of the year
        :return: The number of the year
        """
        return self._year


class Athlete(_Base, HasLanes, HasOccurrence):
    """
    Represents an athlete

    Attributes:
    -----------
    name : str
        Name of the athlete
    year : [year, None]
        Year object the athlete is born in
    club : [Club, None]
        The club the athlete belongs to
    """
    
    def __init__(self, name: str, year: [Year, None], club: [Club, None] = None):
        """ Initializes a new Athlete class
        :type name: str
        :param name: Name of the Athlete
        :type year: [Year, None]
        :param year: The year the athlete is born in
        :type club: [Club, None]
        :param club: The club the athlete belongs to
        """
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
        """ Return the year the athlete belongs to
        :return The year the athlete belongs to
        """
        return self._year
    
    @year.setter
    def year(self, value: [Year, None]):
        """ Sets the year the athlete belongs to """
        self._year = self.__setter(value, self._year)
    
    @property
    def club(self) -> [Club, None]:
        """ Return the club the athlete belongs to
        :return The club the athlete belongs to
        """
        return self._club
    
    @club.setter
    def club(self, value: [Club, None]):
        """ Sets the club the athlete belongs to """
        self._club = self.__setter(value, self._club)
    
    def __setter(self, value, obj):
        """ Function sets or removes an object which belongs to the club
        :type value: [Club, Year, None]
        :param value: The set value
        :type obj: [Club, Year, None]
        :param obj: The object of the class
        :return: The value to store
        """
        if value and obj:
            # first remove athlete
            obj.remove_athlete(self)
            # set to the new value
            value.add_athlete(self)
        elif value:
            # only value is valid, add athlete
            value.add_athlete(self)
        elif obj:
            # only obj is valid, remove athlete from obj
            obj.remove_athlete(self)
        return value


class Competition(_Base, HasHeats):
    """
    Represents a competition

    Attributes:
    -----------
    no : str
        Name of the athlete
    section : [Section, None]
        Year object the athlete is born in
    discipline : str
        The club the athlete belongs to
    distance : int
        The distance in [m]
    repetition : int
        In case of relay the repetition count
    text : str
        The full text of the competition
    sex : str
        The sex of the competition [male, female, mixed]
    heat_cnt : int
        The number of heats the competition has
    
    Methods:
    --------
    name(with_heat: bool = False) : str
        Returns the name of the competition
    is_finale : bool
        Returns if the competition is a final
    is_relay : bool
        Returns if the competition is a relay
    """
    
    def __init__(self, *, no: int, discipline: str, distance: int, sex: str, section: [Section, None] = None,
                 text: str = '',
                 repetition: int = 0, heat_cnt: int = 0, final: bool = False):
        """ Initializes a new Competition class
        :type no: int
        :param no: Number of the competition
        :type discipline: str
        :param discipline: Name of the discipline
        :type distance: int
        :param distance: Distance of the discipline in [m]
        :type sex: str
        :param sex: Sex of the discipline [male, female, mixed]
        :type section: [Section, None]
        :param section: Section in which the competition is
        :type text: str
        :param text: The full description of the competition
        :type repetition: int
        :param repetition: The repetition count in case it is a relay
        :type heat_cnt: int
        :param heat_cnt: No of heats the competition has
        :type final: bool
        :param final: Indicator if it is a final or not
        """
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
        """ Returns the name of the Competition
        :param with_heat: Name with or without heat cnt
        :return: Name of the competition
        """
        # Check if full description is set
        if self.text != '':
            if with_heat:
                # If full description and heat should be displayed return text
                return self.text
            else:
                # otherwise split text
                parts = self.text.split('(')
                # Check if values for heat or heats in the parts
                if _Base._config.pdf_values.heats in parts[len(parts) - 1] or _Base._config.pdf_values.heat in parts[
                    len(parts) - 1]:
                    # Remove the last one
                    parts = parts[0:len(parts) - 1]
                # return parts joined by (
                return str('('.join(parts)).strip()
        # No full description available
        else:
            # Set all values together for the competition
            result: str = fr'{_Base._config.pdf_values.competition} {self.no} - '
            if self.repetition != 0:
                result += fr'{self.repetition}x'
            result += fr'{self.distance}m {self.discipline} {self.sex}'
            if with_heat:
                if len(self.heats) != 1:
                    result += fr' ({self.heat_cnt} {_Base._config.pdf_values.heats})'
                else:
                    result += fr' ({self.heat_cnt} {_Base._config.pdf_values.heat})'
            return result
    
    def is_final(self) -> bool:
        """ Return if competition is final
        :return Is it a final
        """
        return self._final
    
    def is_relay(self) -> bool:
        """ Returns if competition is a relay
        :return: Is it a relay
        """
        return self.repetition > 0
    
    @property
    def section(self) -> Section:
        """ Return the section the competition belongs to
        :return The section the competition belongs to
        """
        return self._section
    
    @section.setter
    def section(self, value: [None, Section]):
        """ Sets the section the competition belongs to """
        self._section = self.__setter(value, self._section)
    
    def __setter(self, value, obj):
        """ Function sets or removes an object which belongs to the competition
        :type value: [Section, None]
        :param value: The set value
        :type obj: [Section, None]
        :param obj: The object of the class
        :return: The value to store
        """
        # Check if value and obj are valid
        if value and obj:
            # first remove competition
            obj.remove_competition(self)
            # set to the new value
            value.add_competition(self)
        elif value:
            # only value is valid, add competition
            value.add_competition(self)
        elif obj:
            # only obj is valid, remove competition from obj
            obj.remove_competition(self)
        return value
    
    @classmethod
    def from_string(cls, string: str, section: [Section, None] = None):
        """ Returns a Competition object from a string
        :type string: str
        :param string: String to be parsed
        :type section: [Section, None]
        :param section: The Section the competition belongs to
        :return: A Competition object
        """
        # In case there is a configuration object
        if _Base._config:
            # Create pattern for regex from the object
            pattern = re.compile(
                _Base._config.pdf_values.competition + r' (\d+) - (\d+|\d+x\d+)m (.+?) (' + _Base._config.pdf_values.male + r'|' + _Base._config.pdf_values.female + r'|' + _Base._config.pdf_values.mixed + r')(.*)')
            sub_pat = re.compile(
                r'.*\((\d+) (' + _Base._config.pdf_values.heats + r'|' + _Base._config.pdf_values.heat + r')\)')
        else:
            # POtherwise take the default pattern
            pattern = re.compile(r'Wettkampf (\d+) - (\d+|\d+x\d+)m (.+?) (männlich|weiblich|mixed)(.*)')
            sub_pat = re.compile(r'.*\((\d+) (Läufe|Lauf)\)')
        # Do regex operation
        match = pattern.match(string)
        # In case there is a match
        if match:
            # Split by x in case there is a relay
            parts = match.group(2).split('x')
            # We have a relay
            if len(parts) == 2:
                # Set variables for relay
                distance = int(parts[1])
                repetition = int(parts[0])
            else:
                # No relay set variable for normal competition
                distance = int(parts[0])
                repetition = 0
            # Init heat count with 0
            heat_cnt: int = 0
            # Run regex to check for heat cnt
            sub_match = sub_pat.match(match.group(5))
            if sub_match:
                # We have a match and a heat count
                heat_cnt = int(sub_match.group(1))
            # Check if competition is final
            is_final: bool = cls._config.pdf_values.final in string
            # Get Competition number
            no = int(match.group(1))
            # check if no in list -> before create list of numbers
            no_list = [x.no for x in cls._registry.get_all(cls)]
            if no in no_list:
                # If number in list return available competition
                return cls._registry.get_all(cls)[no_list.index(no)]
            else:
                # Otherwise create new competition
                return cls(no=no, distance=distance, discipline=match.group(3), sex=match.group(4),
                           text=string, section=section, repetition=repetition, heat_cnt=heat_cnt,
                           final=is_final)
        else:
            # No match
            return None


class Heat(_Base, HasLanes):
    """
    Represents a heat

    Attributes:
    -----------
    no : int
        Name of the athlete
    competition : [Competition, None]
        Competition where the heat belongs to
    """
    
    def __init__(self, no: int, competition: [Competition, None] = None):
        """ Initializes a new Heat class
        :type no: int
        :param no: No of the heat
        :type competition: [Competition, None]
        :param competition: Competition the heat belongs to
        """
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
        """ Return the competition the heat belongs to
        :return The competition the heat belongs to
        """
        return self._competition
    
    @competition.setter
    def competition(self, value: [Competition, None]):
        """ Sets the competition the heat belongs to """
        self._competition = self.__setter(value, self._competition)
    
    def __setter(self, value, obj):
        """ Function sets or removes an object which belongs to the heat
        :type value: [Competition, None]
        :param value: The set value
        :type obj: [Competition, None]
        :param obj: The object of the class
        :return: The value to store
        """
        # Check if value and obj are valid
        if value and obj:
            # first remove competition
            obj.remove_heat(self)
            # set to the new value
            value.add_heat(self)
        elif value:
            # only value is valid, add competition
            value.add_heat(self)
        elif obj:
            # only obj is valid, remove competition from obj
            obj.remove_heat(self)
        return value
    
    @classmethod
    def from_string(cls, string: str):
        """ Returns a Heat object from a string
        :type string: str
        :param string: The string to parse
        :return: A heat object
        """
        # Create regex pattern, in case there is a config use it otherwise use default one
        if _Base._config:
            pattern = re.compile(_Base._config.pdf_values.heat + r' (\d+)(.*)')
        else:
            pattern = re.compile(r'Lauf (\d+)(.*)')
        # Run regex and check for match
        match = pattern.match(string)
        if match:
            # Return new class
            return cls(match.group(1))
        else:
            return None


class Lane(_Base):
    """
    Represents a lane

    Attributes:
    -----------
    no : str
        Number of the lane
    time : datetime.time
        Time the athlete should swimm
    athlete : Athlete
        The Athlete which swims on this lane
    heat : [Heat, None]
        The heat the lane belongs to
    list_entry : bool
        If it is not a lane then it ios a list - this value sets this

    Methods:
    --------
    is_lane() : bool
        Returns it is a lane
    is_start_list_entry() : bool
        Returns is is is a list entry
    time_str : str
        Returns the time a std time string
    """
    
    def __init__(self, no: int, time: datetime.time, athlete: Athlete, heat: [Heat, None], list_entry: bool = False):
        """ Initializes a new Lane class
        :type no: int
        :param no: No of the lane
        :type time: datetime.time
        :param time: Time the athlete should swimm
        :type athlete: Athlete
        :param athlete: The Athlete which should start
        :type heat: [Heat, None]
        :param heat: The heat the lane belongs to
        :type list_entry: bool
        :param list_entry: If is it a list entry
        """
        self.no: int = int(no)
        self.list_entry: bool = list_entry
        self.time: datetime.time = time
        self._athlete: [None, Athlete] = None
        self.athlete: Athlete = athlete
        self._heat: [Heat, None] = None
        
        if heat:
            self.heat = heat
        
        _Base.__init__(self)
    
    def __str__(self):
        return fr'{_Base._config.pdf_values.lane} {self.no} - {str(self.athlete)} - {self.time_str}'
    
    def __repr__(self):
        tmp = fr'{self.__class__.__name__}({self.no}, {self.time_str}, {self.athlete}'
        if self.heat:
            tmp += fr', {self.heat.no}'
        return tmp + ')'
    
    def __del__(self):
        self.heat = None
        self.athlete = None
        _Base.__del__(self)
    
    def is_lane(self) -> bool:
        """ Returns if it is a lane
        :return: If it is a lane
        """
        return self.list_entry == False
    
    def is_start_list_entry(self) -> bool:
        """ Returns if it is a list entry
        :return: If it is a list entry
        """
        return self.list_entry == True
    
    @property
    def time_str(self) -> str:
        """ Returns a time string like 00:00,00 (%M:%S:%f[2])
        :return: A time string
        """
        return fr'{self.time.strftime("%M:%S,")}{int(int(self.time.strftime("%f")) / 10000):02d}'
    
    @property
    def heat(self) -> Heat:
        """ Return the heat the lane belongs to
        :return The heat the lane belongs to
        """
        return self._heat
    
    @heat.setter
    def heat(self, value: [Heat, None]):
        """ Sets the heat the lane belongs to """
        self._heat = self.__setter(value, self._heat)
    
    @property
    def athlete(self) -> Athlete:
        """ Return the athlete the lane belongs to
        :return The athlete the lane belongs to
        """
        return self._athlete
    
    @athlete.setter
    def athlete(self, value: [Athlete, None]):
        """ Sets the athlete the lane belongs to """
        self._athlete = self.__setter(value, self._athlete)
    
    def __setter(self, value, obj):
        """ Function sets or removes an object which belongs to the heat
        :type value: [Athlete, Heat, None]
        :param value: The set value
        :type obj: [Athlete, Heat, None]
        :param obj: The object of the class
        :return: The value to store
        """
        # Check if value and obj are valid
        if value and obj:
            # first remove lane
            obj.remove_lane(self)
            # set to the new value
            value.add_lane(self)
        elif value:
            # only value is valid, add lane
            value.add_lane(self)
        elif obj:
            # only obj is valid, remove lane from obj
            obj.remove_lane(self)
        return value
