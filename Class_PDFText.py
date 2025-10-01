class PDFText:
    
    def __init__(self, value: tuple, page_no: int = -1):
        self._value: tuple = value
        
        if page_no > 0:
            self._page_no = page_no
        else:
            self._page_no: int = -1
    
    def __str__(self) -> str:
        return self.text
    
    @property
    def page_no(self) -> int:
        return self._page_no
    
    @property
    def value(self) -> tuple:
        return self._value
    
    @property
    def bbox(self) -> tuple:
        return self._value[0], self._value[1], self._value[2], self._value[3]
    
    @property
    def x(self) -> float:
        return self._value[0]
    
    @property
    def y(self) -> float:
        return self._value[1]
    
    @property
    def width(self) -> float:
        return self._value[2] - self._value[0]
    
    @property
    def height(self) -> float:
        return self._value[3] - self._value[1]
    
    @property
    def text(self) -> str:
        return self._value[4]
    
    @staticmethod
    def combine(pdftext_objects: list, page_no: int = -1):
        # Check for only a single object
        if len(pdftext_objects) == 1 and type(pdftext_objects[0]) == PDFText:
            return pdftext_objects[0]
        
        x1: float = 10000.0
        y1: float = 10000.0
        x2: float = 0.0
        y2: float = 0.0
        text: str = ''
        for obj in pdftext_objects:
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
        return PDFText((x1, y1, x2, y2, text.strip()), page_no)


class PDFTextCombined(PDFText):
    
    def __init__(self, value, page_no: int = -1):
        self.objects: list = []
        
        if type(value) is tuple:
            PDFText.__init__(self, value, page_no)
        elif type(value) is list:
            if len(value) == 1:
                if type(value[0]) == PDFText:
                    PDFText.__init__(self, value[0].value, page_no)
                else:
                    PDFText.__init__(self, value[0], page_no)
            else:
                pdftext = PDFText.combine(value, page_no)
                PDFText.__init__(self, pdftext.value, page_no)
                self.objects = value
        else:
            raise ValueError(f'Wrong value type {value}')
    
    def __getitem__(self, index: int):
        return self.objects[index]
    
    def pop(self, index: int):
        obj = self.objects.pop(index)
        self._value = PDFText.combine(self.objects, self.page_no).value
        return obj
    
    @property
    def page_no(self) -> int:
        if self._page_no == -1 and all(map(lambda x: x.page_no == self.objects[0].page_no, self.objects)):
            return self.objects[0].page_no
        else:
            return self._page_no
    
    @staticmethod
    def combine(pdftext_objects: list, page_no: int = -1):
        if len(pdftext_objects) == 1 and type(pdftext_objects[0]) == PDFText:
            return pdftext_objects[0]
        return PDFTextCombined(pdftext_objects, page_no)
