from pdfminer.high_level import extract_pages  # Extracts structured page layout
from pdfminer.layout import LTTextContainer, LTChar  # Handles text elements and characters


def find_text_positions(pdf_path, search_text):
    """
    Finds and prints the position of a specific word in a PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        search_text (str): The word to search for in the PDF.
    """
    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text()
                # Search for the exact word within the text block
                if search_text in text:
                    # Initialize bounding box coordinates
                    word_start_x, word_start_y = None, None
                    word_end_x, word_end_y = None, None
                    
                    # Iterate through the text line
                    for text_line in element:
                        line_text = text_line.get_text()
                        if search_text in line_text:
                            # Find the start and end indices of the search term
                            start_idx = line_text.find(search_text)
                            end_idx = start_idx + len(search_text)
                            
                            # Extract bounding boxes for characters in the search term
                            for character_idx, character in enumerate(text_line):
                                if isinstance(character, LTChar):
                                    # If the character is part of the search word
                                    if start_idx <= character_idx < end_idx:
                                        x0, y0, x1, y1 = character.bbox
                                        if word_start_x is None:
                                            word_start_x, word_start_y = x0, y0
                                        word_end_x, word_end_y = x1, y1
                            
                            # Print the bounding box for the entire word
                            if word_start_x is not None and word_end_x is not None:
                                print(f"Found '{search_text}' on page {page_number}:")
                                print(f"  x0: {word_start_x}, y0: {word_start_y}, x1: {word_end_x}, y1: {word_end_y}")
                                print(f"  Width: {word_end_x - word_start_x}, Height: {word_end_y - word_start_y}")
                                #return
    
    print(f"'{search_text}' not found in the PDF.")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    find_text_positions('Meldeergebnis_Nikolaus_2024.pdf', 'SV Georgsmarienhütte')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
