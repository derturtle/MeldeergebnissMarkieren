from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject, ArrayObject, FloatObject

def find_text_positions_and_highlight(pdf_path, search_text, output_path):
    """
    Finds the position of a specific word in a PDF, highlights its line, and saves a new PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        search_text (str): The word to search for in the PDF.
        output_path (str): Path to save the output PDF with highlights.
    """
    # Read the PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Loop through each page in the PDF
    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=0):
        page = reader.pages[page_number]
        page_found = False

        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text()
                    if search_text in line_text:
                        # Get the full printable bounding box for the line
                        line_bbox = get_printable_area_bbox(text_line)

                        # Add a highlight annotation to the PDF
                        add_highlight_annotation(page, line_bbox)
                        page_found = True

        if page_found:
            print(f"Highlighted line containing '{search_text}' on page {page_number + 1}.")

        writer.add_page(page)

    # Write the modified PDF
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Saved highlighted PDF to {output_path}.")

def get_printable_area_bbox(text_line):
    """
    Calculates the bounding box for the full printable area of a text line.

    Args:
        text_line (LTTextLine): The text line to calculate the bounding box for.

    Returns:
        tuple: The bounding box (x0, y0, x1, y1) for the printable area of the line.
    """
    line_start_x, line_start_y = float('inf'), float('inf')
    line_end_x, line_end_y = float('-inf'), float('-inf')

    for character in text_line:
        if isinstance(character, LTChar):
            x0, y0, x1, y1 = character.bbox
            line_start_x = min(line_start_x, x0)
            line_start_y = min(line_start_y, y0)
            line_end_x = max(line_end_x, x1)
            line_end_y = max(line_end_y, y1)

    # Expand bounding box to span the entire printable area of the line
    line_start_x = 0  # Left margin of the printable area
    line_end_x = text_line.width  # Right margin of the printable area

    return line_start_x, line_start_y, line_end_x, line_end_y

def add_highlight_annotation(page, bbox):
    """
    Adds a highlight annotation to a PDF page.

    Args:
        page (PageObject): The PDF page to annotate.
        bbox (tuple): The bounding box (x0, y0, x1, y1) of the line.
    """
    x0, y0, x1, y1 = bbox

    # Create a highlight annotation dictionary
    highlight = DictionaryObject()
    highlight.update({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Highlight"),
        NameObject("/Rect"): ArrayObject([FloatObject(x0), FloatObject(y0), FloatObject(x1), FloatObject(y1)]),
        NameObject("/QuadPoints"): ArrayObject([FloatObject(x0), FloatObject(y1), FloatObject(x1), FloatObject(y1),
                                                FloatObject(x0), FloatObject(y0), FloatObject(x1), FloatObject(y0)]),
        NameObject("/C"): ArrayObject([FloatObject(1), FloatObject(1), FloatObject(0)]),  # Yellow color
        NameObject("/F"): FloatObject(4)  # Print the highlight annotation
    })

    # Add the annotation to the page
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
    page[NameObject("/Annots")].append(highlight)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    find_text_positions_and_highlight('MN2024.pdf', 'SV Georgsmarienhütte', 'Test.pdf')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
