from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject, ArrayObject, FloatObject

__COLORS: dict = {
    'red' : [FloatObject(1), FloatObject(0), FloatObject(0)], # Red color in RGB
    'orange' : [FloatObject(1), FloatObject(0.647), FloatObject(0)], # Red color in RGB
    'green' : [FloatObject(0), FloatObject(1), FloatObject(0)],  # Green color in RGB
    'blue' : [FloatObject(0), FloatObject(0), FloatObject(1)],  # blue color in RGB
    'lightblue' : [FloatObject(173/255), FloatObject(216/255), FloatObject(230/255)],  # light blue color in RGB
    'magenta' : [FloatObject(1), FloatObject(0), FloatObject(1)],  # Pink color in RGB
    'yellow' : [FloatObject(1), FloatObject(1), FloatObject(0)],  # Yellow color in RGB
    'cyan' : [FloatObject(0), FloatObject(1), FloatObject(1)],  # Cyan color in RGB
    'lightgrey' : [FloatObject(0.827), FloatObject(0.827), FloatObject(0.827)],  # light grey color in RGB
    'grey' : [FloatObject(0.745), FloatObject(0.745), FloatObject(0.745)],  # grey color in RGB
}

class __Occurrence:
    def __init__(self, page: int, x: float, y: float, width: float, height: float):
        self.page = page
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def __str__(self):
        return fr'Page: {self.page} (x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height})'

def find_text_positions_and_highlight(pdf_path, search_text, output_path):
    """
    Finds the position of a specific word in a PDF, highlights its line, and saves a new PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        search_text (str): The word to search for in the PDF.
        output_path (str): Path to save the output PDF with highlights.
    """
    # create list for occurence
    occurrences: list = []

    # Read the input PDF using PyPDF2
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Loop through each page in the PDF
    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=0):
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

# todo add here configuration for left and right in %
                        # Add a highlight annotation for the line
                        add_highlight_annotation(page, (page_layout.width * 0.07, line_bbox[1], page_layout.width * 0.95, line_bbox[3]))
        
        # Add the processed page to the writer
        writer.add_page(page)

    # Write the modified PDF to the output file
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Found {len(occurrences)} occurrence of {search_text}.")
    print(f"Saved highlighted PDF to {output_path}.")

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

def add_highlight_annotation(page, bbox):
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
        NameObject("/C"): ArrayObject(__COLORS['yellow']),
        NameObject("/F"): FloatObject(4)  # Annotation flags (4 = printable)
    })

    # Add the annotation to the page's annotations list
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
    page[NameObject("/Annots")].append(highlight)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    find_text_positions_and_highlight('MN2024.pdf', 'SV Georgsmarienhütte', 'Test.pdf')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
