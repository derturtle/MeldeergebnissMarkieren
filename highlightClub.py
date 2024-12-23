from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

def find_text_positions(pdf_path, search_text):
    """
    Finds the position of a specific word in a PDF and marks its line.

    Args:
        pdf_path (str): Path to the PDF file.
        search_text (str): The word to search for in the PDF.
    """
    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text()
                    if search_text in line_text:
                        # Get the bounding box for the word
                        word_bbox = get_word_bbox(text_line, search_text)
                        if word_bbox:
                            x0, y0, x1, y1 = word_bbox
                            print(f"Found '{search_text}' on page {page_number}:")
                            print(f"  Word Bounding Box -> x0: {x0}, y0: {y0}, x1: {x1}, y1: {y1}")

                            # Mark the entire line
                            line_bbox = get_line_bbox(text_line)
                            print(f"Line Bounding Box -> x0: {line_bbox[0]}, y0: {line_bbox[1]}, x1: {line_bbox[2]}, y1: {line_bbox[3]}")
                            return

    print(f"'{search_text}' not found in the PDF.")

def get_word_bbox(text_line, search_text):
    """
    Calculates the bounding box for a specific word within a text line.

    Args:
        text_line (LTTextLine): The text line containing the word.
        search_text (str): The word to search for.

    Returns:
        tuple: The bounding box (x0, y0, x1, y1) of the word.
    """
    start_idx = text_line.get_text().find(search_text)
    if start_idx == -1:
        return None

    end_idx = start_idx + len(search_text)
    word_start_x, word_start_y = None, None
    word_end_x, word_end_y = None, None

    for character_idx, character in enumerate(text_line):
        if isinstance(character, LTChar):
            if start_idx <= character_idx < end_idx:
                x0, y0, x1, y1 = character.bbox
                if word_start_x is None:
                    word_start_x, word_start_y = x0, y0
                word_end_x, word_end_y = x1, y1

    if word_start_x is not None and word_end_x is not None:
        return word_start_x, word_start_y, word_end_x, word_end_y
    return None

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

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    find_text_positions('MN2024.pdf', 'SV Georgsmarienhütte')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
