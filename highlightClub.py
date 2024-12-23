import os.path
import webcolors

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject, ArrayObject, FloatObject, TextStringObject

class __Occurrence:
    def __init__(self, page: int, x: float, y: float, width: float, height: float):
        self.page = page
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def __str__(self):
        return fr'Page: {self.page} (x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height})'

def find_text_positions_and_highlight(in_pdf: str, out_pdf: str, search_text: str, rgb_color: list, start_rect: float, end_rect: float):
    """
    Finds the position of a specific word in a PDF, highlights its line, and saves a new PDF.

    Args:
        in_pdf (str): Path to the PDF file.
        search_text (str): The word to search for in the PDF.
        out_pdf (str): Path to save the output PDF with highlights.
    """
    # create list for occurence
    occurrences: list = []

    # Read the input PDF using PyPDF2
    reader = PdfReader(in_pdf)
    writer = PdfWriter()

    # Loop through each page in the PDF
    for page_number, page_layout in enumerate(extract_pages(in_pdf), start=0):
        # Get the current page from the PDF
        page = reader.pages[page_number]
        
        # Process each element in the layout of the page
        for element in page_layout:
            if isinstance(element, LTTextContainer):  # Check if the element is a text container
                for text_line in element:  # Iterate over each text line in the container
                    line_text = text_line.get_text()  # Extract the text content of the line
                    if search_text in line_text:  # Check if the search text is in the line
                        # Get the bounding box for the entire line
                        line_bbox = get_printable_area_bbox(text_line, page_layout)
                        # Save occurrence for e.g. log output
                        occurrences.append(__Occurrence(page_number, line_bbox[0], line_bbox[1], line_bbox[2]-line_bbox[0], line_bbox[3]-line_bbox[1]))

                        # Add a highlight annotation for the line
                        add_highlight_annotation(page, (page_layout.width * start_rect, line_bbox[1], page_layout.width * end_rect, line_bbox[3]), rgb_color)
        
        # Add the processed page to the writer
        writer.add_page(page)

    # Write the modified PDF to the output file
    with open(out_pdf, "wb") as f:
        writer.write(f)
    print(f"Found {len(occurrences)} occurrence of {search_text}.")
    print(f"Saved highlighted PDF to {out_pdf}.")

def get_printable_area_bbox(text_line, page_layout):
    """
    Calculates the bounding box for the full printable area of a text line.

    Args:
        text_line (LTTextLine): The text line to calculate the bounding box for.

    Returns:
        tuple: The bounding box (x0, y0, x1, y1) for the printable area of the line.
    """
    # Initialize the bounding box coordinates
    line_start_x, line_start_y = float('inf'), float('inf')
    line_end_x, line_end_y = float('-inf'), float('-inf')

    # Iterate over each character in the line to determine the bounding box
    for character in text_line:
        if isinstance(character, LTChar):  # Ensure the element is a character
            x0, y0, x1, y1 = character.bbox  # Get the character's bounding box
            line_start_x = min(line_start_x, x0)
            line_start_y = min(line_start_y, y0)
            line_end_x = max(line_end_x, x1)
            line_end_y = max(line_end_y, y1)

    return line_start_x, line_start_y, line_end_x, line_end_y

def add_highlight_annotation(page, bbox, rgb_color: list):
    """
    Adds a highlight annotation to a PDF page.

    Args:
        page (PageObject): The PDF page to annotate.
        bbox (tuple): The bounding box (x0, y0, x1, y1) of the line.
    """
    # Unpack the bounding box coordinates
    x0, y0, x1, y1 = bbox

    # Create a highlight annotation dictionary
    highlight = DictionaryObject()
    highlight.update({
        NameObject("/Type"): NameObject("/Annot"),  # Annotation type
        NameObject("/Subtype"): NameObject("/Highlight"),  # Highlight annotation subtype
        NameObject("/Rect"): ArrayObject([
            FloatObject(x0), FloatObject(y0), FloatObject(x1), FloatObject(y1)
        ]),  # Rectangle defining the annotation area
        NameObject("/QuadPoints"): ArrayObject([
#todo make configurable offset to expand text
            # Coordinates for the highlight area (quadrilateral points)
            FloatObject(x0), FloatObject(y1+1),  # Top-left
            FloatObject(x1), FloatObject(y1+1),  # Top-right
            FloatObject(x0), FloatObject(y0-1),  # Bottom-left
            FloatObject(x1), FloatObject(y0-1)   # Bottom-right
        ]),
        NameObject("/C"): ArrayObject([FloatObject(rgb_color[0]),FloatObject(rgb_color[1]),FloatObject(rgb_color[2])]),
        NameObject("/F"): FloatObject(4),  # Annotation flags (4 = printable)
    })

    # Add the annotation to the page's annotations list
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
    page[NameObject("/Annots")].append(highlight)

def highlight_in_pdf(in_pdf: str, search_str: str, *, color: [str,list] = 'yellow', out_pdf = None, start_rect: int = 7, end_rect: int = 95):
    rgb_color = []
    
    # Check input path
    if not os.path.exists(in_pdf):
        print(fr'{in_pdf} not exist')
        return 1
    # Check search str
    if search_str == '':
        print(fr'no search string found')
        return 2
    
    # Check color
    if type(color) is str:
        #Valid rgb value
        if len(color) == 7 and color.startswith('#') and color[1:7].isnumeric():
            rgb_color = [float(i)/255 for i in webcolors.hex_to_rgb(color)]
        elif color.lower() in webcolors.names():
            rgb_color = [float(i)/255 for i in webcolors.name_to_rgb(color)]
        else:
            print(fr'Color: {color} unknown or wrong type')
            return 3
    elif type(color) is list:
        if len(color) == 3:
            try:
                rgb_color = [float(i)/255 for i in color]
            except ValueError:
                print(fr'Color: {color} unable to proces value')
                return 3
            for val in rgb_color:
                if 0 < val < 1.0:
                    print(fr'Color: {color} values only between 0 and 255 are allowed')
                    return 3
    else:
        print(fr'Color: {color} has an unknown type')
    
    # Set output = input
    if out_pdf is None:
        out_pdf = in_pdf
    
    find_text_positions_and_highlight(in_pdf, out_pdf, search_str, rgb_color, float(start_rect)/100.0, float(end_rect)/100.0)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #find_text_positions_and_highlight('Meldeergebnis_Nikolaus_2024.pdf', 'SV Georgsmarienhütte', 'Test.pdf')
    highlight_in_pdf('Meldeergebnis_Nikolaus_2024.pdf', 'SV Georgsmarienhütte', out_pdf='Test.pdf')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/