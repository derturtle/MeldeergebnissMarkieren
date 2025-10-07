import os
import sys
import argparse

from Class_Config import Config
from Class_PDFOperations import PDFOperations
from CreateFileOutput import FileType, club_to_file
from Class_TextInterface import TextInterface

MAIN_DEBUG: bool = False

def debug_func():
    tst_path: str = './TestFiles/in'
    tests: dict = {
        "2024_HF":  [f'{tst_path}/2024_HF.pdf', 89, None],
        "2024_Nikolaus": [f'{tst_path}/2024_Nikolaus.pdf', 39, None],
        "2024_TSG": [f'{tst_path}/2024_TSG.pdf', 76, None],
        "2025_TSG": [f'{tst_path}/2025_TSG.pdf', 90, None],
        "2025_KMS": [f'{tst_path}/2025_KMS.pdf', 41, None],
        "2025_BadEssen": [f'{tst_path}/2025_BadEssen.pdf', 20, None],
        "2025_Rheine": [f'{tst_path}/2025_Rheine_SVG.pdf', 86, None],
        "2025_TSWF": [f'{tst_path}/2025_TWSF.pdf', 35, None],  # last page was not scanned
        "2025_Wagenfeld": [f'{tst_path}/2025_Wagenfeld.pdf', 29, None],  # last page was not scanned
    }
    
    for key, value in tests.items():
        base = os.path.dirname(value[0])
        name = os.path.basename(value[0])
        out = base + '/../out/' + name
        print(f'[DEBUG] Processing {key}')

        # Reading pdf
        pdf_obj = PDFOperations()
        pdf_obj.read_pdf(value[0])
        
        # Store collection
        coll = pdf_obj.collection
        
        print(f'[DEBUG] {key} has {value[1]} pages')
        # Create outputs
        club_to_file(out[:-4]+'.md', coll.club_by_name('SV Georgsmarienhütte'), FileType.MARKDOWN)
        club_to_file(out[:-4]+'.html', coll.club_by_name('SV Georgsmarienhütte'), FileType.HTML)
        club_to_file(out[:-4]+'.txt', coll.club_by_name('SV Georgsmarienhütte'), FileType.TEXT)
        
        # PDFOperations.highlight_pdf(value[0], out[:-4] + '_marked.pdf',
        #                             coll.club_by_name('SV Georgsmarienhütte').occurrence,
        #                             coll.config.colors.rgb['grey_75'],
        #                             pdf_obj.text_x_range[0], pdf_obj.text_x_range[1], 1)
        PDFOperations.highlight_pdf_clubs(value[0], out[:-4] + '_marked.pdf',
                                          [coll.club_by_name('SV Georgsmarienhütte')],
                                          [coll.config.colors.rgb['grey_75']],
                                          pdf_obj.text_x_range[0], pdf_obj.text_x_range[1], 1)
        
        PDFOperations.add_product_info(out[:-4] + '_marked.pdf', coll)

        # store collection and borders
        tests[key][1] = pdf_obj.text_x_range
        tests[key][2] = pdf_obj.collection
        
    # Check config
    config = Config()
    color = config.colors.valid_color('255,0,0')
    if color:
        config.colors.add('red', color)
    config.save()
    
def run_parser():
    parser = argparse.ArgumentParser(  # prog='ProgramName',
        description='This program marks clubs like "SV Georgsmarienhütte" in so called "Meldeergebnissen". In future, it should is also possible to mark Person like "Max Mustermann"',
        epilog='Created by Florian Grafe from SV Georgsmarienhütte')
    # usage="The string describing the program usage (default: generated from arguments added to parser)")
    parser.add_argument('file', help='The "Meldeergbniss" to mark clubs in')
    parser.add_argument('club',
                        help='The Name of the club which should be marked like "SV Georgsmarienhütte"')
    # parser.add_argument('-h', '--help', help='Display this help')
    parser.add_argument('-c', '--color',
                        help='Color of the highlight, e.g. "yellow", "cyan",... or use rgb code like 255,255,0',
                        default='yellow')
    parser.add_argument('-o', '--output', help='Alternative output file', default=None)
    parser.add_argument('-ro', '--offset', type=int,
                        help='This makes the highlighted region bigger or smaller depending on the value [Default 1]',
                        default=1)
    parser.add_argument('-rs', '--start', type=int,
                        help='This defines in percent of the page where the rect starts [Default: -1 (calculates value from pdf)]',
                        default=-1)
    parser.add_argument('-re', '--end', type=int,
                        help='This defines in percent of the page where the rect end [Default: 95 (calculates value from pdf)]',
                        default=-1)
    args = parser.parse_args()
    
    # Check colors
    config = Config()
    valid_color = config.colors.valid_color(args.color)
    if args.color in config.colors.rgb.keys():
        color = config.colors.rgb[args.color]
    elif valid_color:
        config.colors.add('NewColor', valid_color)
        color = config.colors.rgb['NewColor']
    else:
        error_color: list = []
        for key, value in config.colors.hex.items():
            error_color.append(fr'{key} (#{value})')
        print("\nerror: Invalid color, use format 255,255,255, 0xFFFFFF or #FFFFFF\n\nValid colors are: " + ', '.join(
            error_color) + '\n')
        exit(3)
    
    # Reading pdf
    obj_pdf = PDFOperations()
    pdf_file = os.path.abspath(os.path.expanduser(args.file))
    if not obj_pdf.read_pdf(pdf_file):
        print("\nerror: Reading of pdf failed")
        exit(1)
        
    # Check if reading was okay
    collection = obj_pdf.collection
    borders = obj_pdf.text_x_range

    # Check if club exist
    club = collection.club_by_name(args.club)
    if not club:
        print("\nerror: Club \"" + args.club + "\" didn't exist in " + args.file)
        exit(2)
    
    # Check output
    if args.output:
        if not os.path.exists(os.path.dirname(args.output)):
            os.mkdir(os.path.dirname(args.output))
        output = args.output
    else:
        output = args.file[:-4] + fr'_{args.club}.pdf'
    
    if args.start > 0:
        borders[0] = args.start
    if args.end > 0:
        borders[1] = args.end
    
    PDFOperations.highlight_pdf(pdf_file, output, club.occurrence, color, borders[0], borders[1], args.offset)
    club_to_file(output[:-4] + '.html', club)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if MAIN_DEBUG:
        debug_func()
        exit(0)
    
    if len(sys.argv) > 1:
        run_parser()
    else:
        TextInterface.run()


