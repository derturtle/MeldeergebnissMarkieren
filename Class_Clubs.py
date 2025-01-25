


class Participants:
    __value:dict = {'male': 0, 'female': 0}
    
    def __init__(self, *args, **kwargs):
        # super().__init__()
        if len(args) == 0:
            # use kwargs
            self.__check_kwargs(kwargs)
        elif len(args) == 1:
            if type(args[0]) is dict:
                self.__check_kwargs(args[0])
            elif type(args[0]) is list and len(args[0]) <= 2:
                self.__check_list(args[0])
            elif type(args[0]) is int:
                self.__value['male'] = args[0]
            else:
                raise ValueError
        elif len(args) == 2:
            self.__check_list(list(args))
        else:
            raise ValueError
    
    def __str__(self):
        return fr'{self.__value["male"] / self.__value["female"]}'
    
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
    
    def __check_list(self, args:list):
        for i in range(0, len(args)):
            if type(args[i]) is int:
                self.__value[list(self.__value.keys())[i]] = args[i]
            else:
                raise ValueError
    
    def __check_kwargs(self, kwargs:dict):
        if len(kwargs) != 0:
            for key, value in kwargs.items():
                # self[key] = value
                if not (key == 'male' or key == 'female' and type(value) is int):
                    raise ValueError
                else:
                    self.__value[key] = value
    
    def toList(self) -> list:
        return [self.__value['male'], self.__value['female']]
    
    def toDict(self) -> dict:
        return self.__value
    
    def isEmpty(self) -> bool:
        return self.cnt == 0
    
    @property
    def cnt(self) -> int:
        return sum(self.toList())
    
    @property
    def male(self):
        return self.__value['male']
    
    @male.setter
    def male(self, cnt: int):
        self.__value['male'] = cnt
    
    @property
    def female(self):
        return self.__value['female']
    
    @female.setter
    def female(self, cnt: int):
        self.__value['female'] = cnt

class Association:
    name: str
    id: 0
    clubs: list
    
    def __init__(self, name: str, id: str = ''):
        self.name = name
        self.id = id
        pass
    
    def __str__(self) -> str:
        result = self.name
        if self.id != '':
            if self.id.isnumeric():
                result += fr' (LSV-Nr.: {self.id})'
            else:
                result += fr' ({self.id})'
        if len(self.clubs) > 0:
            result += fr' [{len(self.clubs)}]'

class Club:
    name: str
    id: str
    participants: Participants
    segments: list
    __association: [Association, None] = None
    
    def __init__(self, name: str, id: str = ''):
        self.name = name
        self.id = id
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
   
   
    @property
    def association(self):
        return self.__association
    
    @association.setter
    def association(self, value: Association):
        if self.__association is not None:
            self.__association.clubs.remove(self.__association)
            
        self.__association = value
        self.__association.clubs.append(self)
    
    
    
    
    
