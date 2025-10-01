from pdfminer.layout import LTItem


class PDFText:
    """
    Represents a pdf text object
    
    Attributes:
    -----------
    text_container: LTItem
        pdfminer text object
    page_no: int
        No. of the page on with this container could be found
        
    Methods:
    --------
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
    """
    def __init__(self, text_container: LTItem, page_no: int):
        """
         Initializes a new PDFText instance.
        
        :type text_container: LTItem
        :param text_container: pdfminer LTItem to store
        :type page_no: int
        :param page_no: No. of the page on with this container could be found
        """
        self.text_container: LTItem = text_container
        self.page_no = page_no

    def __str__(self) -> str:
        return self.text
    
    def __eq__(self, other):
        if isinstance(other, PDFText):
            return self is other
        elif isinstance(other, str):
            return str(self) == str(other)
        return False
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        # Less than comparison (supports: <)
        if isinstance(other, (PDFText, str)):
            return str(self) < str(other)
        return NotImplemented
    
    def __le__(self, other):
        # Less than or equal comparison (supports: <=)
        if isinstance(other, str):
            return str(self) <= str(other)
        return NotImplemented
    
    def __gt__(self, other):
        # Greater than comparison (supports: >)
        if isinstance(other, str):
            return str(self) > str(other)
        return NotImplemented
    
    def __ge__(self, other):
        # Greater than or equal comparison (supports: >=)
        if isinstance(other, str):
            return str(self) >= str(other)
        return NotImplemented
    
    # def __len__(self):
    #     # Length of the string (supports len())
    #     return len(str(self))
    
    # def __contains__(self, item):
    #     # Supports "in" operation
    #     return item in str(self)
    
    def __getitem__(self, index):
        # Allows indexing like a string (e.g., obj[0])
        return str(self)[index]

    @property
    def text(self) -> str:
        """
        Returns text of the pdf text object
        
        :return: float
        """
        return self.text_container.get_text().strip()

    @property
    def bbox(self) -> tuple:
        """
        Returns the x1, y1, x2, y2 position pdf text object
        
        :return: tuple
        """
        return self.text_container.bbox

    @property
    def x(self) -> float:
        """
        Returns the x-position on the page of the pdf text object
        
        :return: float
        """
        return self.bbox[0]

    @property
    def y(self) -> float:
        """
        Returns the y-position on the page of the pdf text object
        
        :return: float
        """
        return self.bbox[1]

    @property
    def width(self) -> float:
        """
        Returns the width of the pdf text object
        
        :return: float
        """
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        """
        Returns the height of the pdf text object
        
        :return: float
        """
        return self.bbox[3] - self.bbox[1]
    
