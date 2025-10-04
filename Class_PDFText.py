class PDFText:
    """
    Represents a pdf text object

    Attributes:
    -----------
    value: tuple
        pymupdf tuple with the information about the text
    page_no: int
        No. of the page on with this container could be found
    bbox : tuple
        The bounding box of the text object
    text : str
        The text value of the pdf object
    x : int
        X-position of the pdf object
    y : int
        Y-position ob the pdf object
    width : int
        Width: of the pdf object
    height : int
        Height of the pdf object

    Methods:
    --------
    combine : PDFText
        combines a list of PDFText objects
    """
    
    def __init__(self, value: tuple, page_no: int = -1):
        """
        Initializes a new PDFText instance.
        
        :param value: pymupdf text information
        :param page_no: No. of the page on with this container could be found
        """
        # Store value
        self._value: tuple = value
        # Check page no and store
        if page_no > 0:
            self._page_no = page_no
        else:
            self._page_no: int = -1
    
    def __str__(self) -> str:
        return self.text
    
    def __getitem__(self, index):
        # Allows indexing like a string (e.g., obj[0])
        return str(self)[index]
    
    @property
    def page_no(self) -> int:
        """
        Return the page no of the object. -1 in case it is stored without page
        
        :return: int
        """
        return self._page_no
    
    @property
    def value(self) -> tuple:
        return self._value
    
    @property
    def bbox(self) -> tuple:
        """
        Returns the x1, y1, x2, y2 position pdf text object

        :return: tuple
        """
        return self._value[0], self._value[1], self._value[2], self._value[3]
    
    @property
    def x(self) -> float:
        """
        Returns the x-position on the page of the pdf text object

        :return: float
        """
        return self._value[0]
    
    @property
    def y(self) -> float:
        """
        Returns the y-position on the page of the pdf text object

        :return: float
        """
        return self._value[1]
    
    @property
    def width(self) -> float:
        """
        Returns the width of the pdf text object

        :return: float
        """
        return self._value[2] - self._value[0]
    
    @property
    def height(self) -> float:
        """
        Returns the height of the pdf text object

        :return: float
        """
        return self._value[3] - self._value[1]
    
    @property
    def text(self) -> str:
        """
        Returns text of the pdf text object

        :return: float
        """
        return self._value[4]
    
    @staticmethod
    def combine(pdftext_objects: list, page_no: int = -1):
        """
        Combines multiple PDFText objects into one
        :param pdftext_objects: List of PDFText objects
        :param page_no: No of the page where to find the Text object
        :return: A new PDFText object
        """
        # todo: The list should be sorted so that everything what is in one line should be in line (the text) and in case there is a new line a '\n' should be added
        
        # Check for only a single object
        if len(pdftext_objects) == 1 and type(pdftext_objects[0]) == PDFText:
            return pdftext_objects[0]
        # Initialize values for new tuple
        x1: float = 10000.0
        y1: float = 10000.0
        x2: float = 0.0
        y2: float = 0.0
        text: str = ''
        # Loop over object and check max, min values also concat text
        for obj in pdftext_objects:
            # It is a PDFText Object
            if type(obj) is PDFText:
                text += obj.text + ' '
                if x1 > obj.bbox[0]:
                    x1 = obj.bbox[0]
                if y1 > obj.bbox[1]:
                    y1 = obj.bbox[1]
                if x2 < obj.bbox[2]:
                    x2 = obj.bbox[2]
                if y2 < obj.bbox[3]:
                    y2 = obj.bbox[3]
            # It is a tuple > 5 (valid tuple)
            elif type(obj) is tuple and len(obj) >= 5:
                text += obj[4] + ' '
                if x1 > obj[0]:
                    x1 = obj[0]
                if y1 > obj[1]:
                    y1 = obj[1]
                if x2 < obj[2]:
                    x2 = obj[2]
                if y2 < obj[3]:
                    y2 = obj[3]
        # New PDF object with new data
        return PDFText((x1, y1, x2, y2, text.strip()), page_no)


class PDFTextCombined(PDFText):
    """
    Represents a pdf text object which is combined from multiple PDFText objects
    
    Attributes:
    -----------
    objects: list
        A list of all objects where the object PDFTextCombine object is created from
    page_no: int
        No. of the page on with this container could be found

    Methods:
    --------
    combine : PDFTextCombined
        Combines a list of PDFText objects
        
    pop :  PDFText, tuple
        Removes an object from the list and returns the removed one
    """
    
    def __init__(self, value, page_no: int = -1):
        """
        Initializes a new PDFTextCombined instance.
        
        :param value: The objects the Combined class is made from
        :param page_no: No. of the page on with this container could be found
        """
        # Init object list
        self.objects: list = []
        
        # In case of tuple try to create PDF object
        if type(value) is tuple:
            PDFText.__init__(self, value, page_no)
            self.objects = [PDFText(value, page_no)]
        # In case of list check list and data in it
        elif type(value) is list:
            if len(value) == 1:
                if type(value[0]) == PDFText:
                    PDFText.__init__(self, value[0].value, page_no)
                    self.objects = [value]
                else:
                    PDFText.__init__(self, value[0], page_no)
                    self.objects = [PDFText(value, page_no)]
            else:
                pdftext = PDFText.combine(value, page_no)
                PDFText.__init__(self, pdftext.value, page_no)
                for obj in self.value:
                    if type(obj) is tuple and len(obj) > 5:
                        self.objects.append(PDFText(obj, page_no))
                    elif type(PDFText):
                        self.objects.append(PDFText)
        else:
            raise ValueError(f'Wrong value type {value}')
    
    def __getitem__(self, index: int):
        return self.objects[index]
    
    def pop(self, index: int):
        """
        Remove a value from the list which has the index and returns it
        
        :param index: Index in the list
        :return: The removed object from the list
        """
        obj = self.objects.pop(index)
        self._value = PDFText.combine(self.objects, self.page_no).value
        return obj
    
    @property
    def page_no(self) -> int:
        """
        Return the page no of the object. -1 in case it is stored without page

        :return: int
        """
        if self._page_no == -1 and all(map(lambda x: x.page_no == self.objects[0].page_no, self.objects)):
            return self.objects[0].page_no
        else:
            return self._page_no
    
    @staticmethod
    def combine(pdftext_objects: list, page_no: int = -1):
        """
        Combines multiple PDFText objects into one
        :param pdftext_objects: List of PDFText objects
        :param page_no: No of the page where to find the Text object
        :return: A new PDFTextCombined object
        """
        if len(pdftext_objects) == 1 and type(pdftext_objects[0]) == PDFText:
            return pdftext_objects[0]
        return PDFTextCombined(pdftext_objects, page_no)
