from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter


def find_text_positions_and_highlight(pdf_path, search_text, output_path):
    """
    Finds the position of a specific word in a PDF, highlights its line, and saves a new PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        search_text (str): The word to search for in the PDF.
        output_path (str): Path to save the output PDF with highlights.
    """
    # Open the original PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    # Temporary overlay file for highlights
    overlay_path = "overlay.pdf"
    
    # Loop through each page in the PDF
    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=0):
        page_found = False
        
        # Create a canvas for drawing highlights
        c = canvas.Canvas(overlay_path, pagesize=(reader.pages[page_number].mediabox.width,
                                                  reader.pages[page_number].mediabox.height))
        
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text()
                    if search_text in line_text:
                        # Get the line bounding box
                        line_bbox = get_line_bbox(text_line)
                        
                        # Draw a rectangle to highlight the line
                        highlight_line(c, line_bbox)
                        page_found = True
        
        # Save the overlay for this page
        c.showPage()
        c.save()
        
        # Merge the overlay with the original page
        overlay_reader = PdfReader(overlay_path)
        page = reader.pages[page_number]
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)
        
        if page_found:
            print(f"Highlighted line containing '{search_text}' on page {page_number + 1}.")
    
    # Write the new PDF
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Saved highlighted PDF to {output_path}.")


def get_line_bbox(text_line):
    """
    Calculates the bounding box for an entire text line.

    Args:
        text_line (LTTextLine): The text line to calculate the bounding box for.

    Returns:
        tuple: The bounding box (x0, y0, x1, y1) of the text line.
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
    
    return line_start_x, line_start_y, line_end_x, line_end_y


def highlight_line(canvas_obj, bbox, color=(1, 1, 0), opacity=0.3):
    """
    Highlights a line in the PDF using a semi-transparent rectangle.

    Args:
        canvas_obj (canvas.Canvas): The canvas object to draw on.
        bbox (tuple): The bounding box (x0, y0, x1, y1) of the line.
        color (tuple): RGB color of the highlight (default is yellow).
        opacity (float): Opacity of the highlight (default is 0.3).
    """
    x0, y0, x1, y1 = bbox
    canvas_obj.saveState()
    canvas_obj.setFillColorRGB(*color, alpha=opacity)
    canvas_obj.rect(x0, y0, x1 - x0, y1 - y0, fill=True, stroke=False)
    canvas_obj.restoreState()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    find_text_positions_and_highlight('MN2024.pdf', 'SV Georgsmarienhütte', 'Test.pdf')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
