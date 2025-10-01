from enum import Enum
from Class_Competition_Objects import Club


class FileType(Enum):
    """
    Represents an Enum with the file type (supported)
    """
    NONE = 0
    TEXT = 1
    MARKDOWN = 2
    HTML = 3


def _add_bootstrap() -> str:
    """ Add bootstrap to html file
    :return: link and script tag with bootstrap
    """
    return '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">\n<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>\n'


def _file_header(file_type: FileType, title: str = '') -> str:
    """ Generates the header of the file
    :param file_type: Type of file
    :param title: Title of file
    :return: Header of file
    """
    result: str = ''
    if file_type == FileType.HTML:
        result += fr'<!DOCTYPE html>' + '\n'
        result += fr'<html lang="de">' + '\n'
        result += fr'  <head>' + '\n'
        result += fr'    <meta charset="utf-8">' + '\n'
        result += fr'    <meta name="viewport" content="width=device-width, initial-scale=1.0">' + '\n'
        result += fr'    <title>{title}</title>' + '\n'
        result += _add_bootstrap()
        result += fr'  </head>' + '\n'
        result += fr'  <body class="container py-5">' + '\n'
    return result


def _file_heading(heading: str, no: int, file_type: FileType, is_card: bool = False) -> str:
    """ Generates a heading of the file
    :param heading: Name of heading
    :param no: Depth of heading (starts by 1)
    :param file_type: Type of file
    :param is_card: In case the heading is a card type (only html)
    :return: A heading string
    """
    result = ''
    if file_type == FileType.MARKDOWN:
        result += fr'{"#" * no} {heading}' + '\n\n'
    elif file_type == FileType.HTML and not is_card:
        adaption: str = ''
        if no < 3:
            adaption += fr'class="text-center  mb-4"'
        elif no < 5:
            adaption += fr'class="text-center"'
        else:
            pass
        result += fr'<!-- {heading} -->' + '\n'
        result += fr'<h{no} {adaption}>{heading}</h{no}>' + '\n'
    elif file_type == FileType.HTML and is_card:
        result += fr'<!-- {heading} -->' + '\n'fr'<div class="card mb-4"><div class="card-header bg-info text-white text-center">{heading}</div>'
    elif file_type == FileType.TEXT:
        result += heading + '\n'
        if no < 3:
            result += '\n'
    else:
        pass
    return result


def _file_footer(file_type: FileType) -> str:
    """ Generates the footer of the file
    :param file_type: Type of file
    :return: A footer of the file
    """
    result: str = ''
    if file_type == FileType.HTML:
        result += fr'  </body>' + '\n'
        result += fr'</html>' + '\n'
    return result


def _judges_list_element(element: str, file_type: FileType, no: int = 1) -> str:
    """ Generates an element of the list of Judges
    :param element: Element value
    :param file_type: Type of file
    :param no: No. of the entry
    :return: A judge list element
    """
    result: str = ''
    if file_type == FileType.MARKDOWN:
        result += fr'{no}. {element}' + '\n'
    elif file_type == FileType.HTML:
        result += fr'  <li class="list-group-item">{element}</li>' + '\n'
    elif file_type == FileType.TEXT:
        result += element + '\n'
    else:
        pass
    return result


def _judges_list(heading: str, values: list, file_type: FileType) -> str:
    """ Creates a list of judges
    :param heading: The heading of this list
    :param values: the list values
    :param file_type: Type of file
    :return: A list of judges
    """
    result = ''
    heading = _file_heading(heading, 3, file_type, )
    for no, value in enumerate(values, start=1):
        result += _judges_list_element(value, file_type, no)
    
    if file_type == FileType.MARKDOWN:
        result = heading + result + '\n\n'
    elif file_type == FileType.HTML:
        heading = fr'  <div class="col-md-6 mb-4">' + '\n' + heading
        result = heading + '<ol class="list-group">\n' + fr'{result}</ol>' + '\n'
        result += fr'  </div>' + '\n'
    elif file_type == FileType.TEXT:
        result = heading + result + '\n'
    else:
        pass
    return result


def _judges_begin(file_type: FileType) -> str:
    """ Some type of header of the judges
    :param file_type: Type of file
    :return: Header of judges
    """
    result = ''
    if file_type == FileType.HTML:
        result += fr'<div class="row">' + '\n'
    else:
        pass
    return result


def _judges_end(file_type: FileType) -> str:
    """ Some type of footer of the judges
    :param file_type: Type of file
    :return: Footer of judges
    """
    result = ''
    if file_type == FileType.HTML:
        result += fr'</div>' + '\n'
    else:
        pass
    return result


def _starts_entry(section_no: int, competition_no: int, heat_no: int, lane_no: int, discipline: str,
                  file_type: FileType, no: int = 1) -> str:
    """ Creates are start entry
    :param section_no: No of the section
    :param competition_no: No of the competition
    :param heat_no: No of the heat
    :param lane_no: No of the lane
    :param discipline: Discipline of the competition
    :param file_type: Type of file
    :param no: No of the entry
    :return: A start entry
    """
    result = ''
    if file_type == FileType.MARKDOWN:
        result += fr'{no}. {competition_no:2d}/{heat_no:2d}/{lane_no} {discipline} [{section_no}]' + '\n'
    elif file_type == FileType.HTML:
        result += fr'  <tr>' + '\n'
        result += fr'    <td class="text-center">{no}</td>' + '\n'
        result += fr'    <td class="text-center">{competition_no}</td>' + '\n'
        result += fr'    <td class="text-center">{heat_no}</td>' + '\n'
        result += fr'    <td class="text-center">{lane_no}</td>' + '\n'
        result += fr'    <td class="text-left">{discipline}</td>' + '\n'
        result += fr'    <td class="text-center">{section_no}</td>' + '\n'
        result += fr'  </tr>' + '\n'
    elif file_type == FileType.TEXT:
        result += fr'[{section_no}]  {competition_no:2d}/{heat_no:2d}/{lane_no} {discipline}' + '\n'
    else:
        pass
    
    return result


def _starts_begin(file_type: FileType) -> str:
    """ Generates a header of a start
    :param file_type: Type of file
    :return: Header of a start
    """
    result = ''
    if file_type == FileType.MARKDOWN:
        result += '*Nr. Wk/ L/B Strecke [Abschnit]*\n\n'
    elif file_type == FileType.HTML:
        result += fr'<div class="card-body">' + '\n'
        result += fr'  <table class="table table-bordered table-striped table-fixed">' + '\n'
        result += fr'    <thead>' + '\n'
        result += fr'      <tr>' + '\n'
        result += fr'        <th scope="col" class="text-center" style="width: 50px;">Nr.</th>' + '\n'
        result += fr'        <th scope="col" class="text-center" style="width: 50px;">WK</th>' + '\n'
        result += fr'        <th scope="col" class="text-center" style="width: 50px;">L</th>' + '\n'
        result += fr'        <th scope="col" class="text-center" style="width: 50px;">B</th>' + '\n'
        result += fr'        <th scope="col" class="text-left" style="width: 200px;">Discipline</th>' + '\n'
        result += fr'        <th scope="col" class="text-center" style="width: 80px;">Abschnit</th>' + '\n'
        result += fr'      </tr>' + '\n'
        result += fr'    </thead>' + '\n'
        result += fr'    <tbody>' + '\n'
    else:
        pass
    
    return result


def _starts_end(file_type: FileType) -> str:
    """ Generates a footer of a start
    :param file_type: Type of file
    :return: Footer of a start
    """
    result: str = ''
    if file_type == FileType.MARKDOWN or file_type == FileType.TEXT:
        result += '\n'
    elif file_type == FileType.HTML:
        result += fr'    </tbody>' + '\n'
        result += fr'  </table>' + '\n'
        result += fr'</div>' + '\n'
    else:
        pass
    return result


def club_to_file(file_name: str, club: Club, file_type: FileType = FileType.NONE):
    """ Generates a file with the club data
    :param file_name: Name of the output file
    :type club: Club
    :param club: Class with all the club data
    :param file_type: Type of file
    """
    if file_type == FileType.NONE:
        # Check file name to determine file type
        if file_name.endswith('.html') or file_name.endswith('.htm') or file_name.endswith('.php'):
            file_type = FileType.HTML
        elif file_name.endswith('.md') or file_name.endswith('.markdown'):
            file_type = FileType.MARKDOWN
        else:
            file_type = FileType.TEXT
    # Create headings
    output: str = ''
    output += _file_header(file_type, fr'Meldungen {club.name}')
    output += _file_heading(club.name, 1, file_type, )
    
    # Generate judges
    output += _file_heading('Kampfgericht', 2, file_type, )
    # loop over judges to create a dict with section
    judge_dict: dict = {}
    for judge in club.judges:
        judge_dict.setdefault(judge.section.no, []).append(fr'{judge.position}: {judge.name}')
    # Create key list for all sections
    key_list = sorted(list(judge_dict.keys()))
    output += _judges_begin(file_type)
    # For evey section crete entry
    for key in key_list:
        output += _judges_list(fr'Abschnit {key}', judge_dict[key], file_type)
    output += _judges_end(file_type)
    
    # Generate starts
    output += _file_heading('Starts', 2, file_type, )
    # Get athletes
    athletes = club.athletes
    athletes.sort(key=lambda x: x.name)
    # Loop over every athlete
    for athlete in athletes:
        # Athlete as heading
        output += _file_heading(fr'{athlete.name} ({athlete.year})', 3, file_type)
        # Header of start
        output += _starts_begin(file_type)
        # loop over every competition of the athlete starts
        for no, lane in enumerate(athlete.lanes, start=1):
            competition = lane.heat.competition
            output += _starts_entry(competition.section.no, competition.no, lane.heat.no, lane.no,
                                    fr'{competition.distance:4d}m {competition.discipline}', file_type, no)
        # Footer of start
        output += _starts_end(file_type)
    # Write to output
    output += _file_footer(file_type)
    
    with open(file_name, 'w') as fp:
        fp.write(output)
