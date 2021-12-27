__version__ = "1.0.0"


def ansi_rgb(r: int, g: int, b: int, foreground: bool = True) -> str:
    """
    Convert rgb color into ANSI escape code format

    :param r:
    :param g:
    :param b:
    :param foreground: Whether the color applies to forground
    :return: Escape code
    """
    c = '38' if foreground else '48'
    return f'\033[{c};2;{r};{g};{b}m'


def color(msg: str) -> str:
    """
    Replace extended minecraft color codes in string

    :param msg: Message with minecraft color codes
    :return: Message with escape codes
    """
    replacements = ["&0/\033[0;30m", "&1/\033[0;34m", "&2/\033[0;32m", "&3/\033[0;36m", "&4/\033[0;31m", "&5/\033[0;35m", "&6/\033[0;33m", "&7/\033[0;37m", "&8/\033[1;30m", "&9/\033[1;34m", "&a/\033[1;32m", "&b/\033[1;36m", "&c/\033[1;31m", "&d/\033[1;35m", "&e/\033[1;33m", "&f/\033[1;37m", "&r/\033[0m", "&n/\n"]
    for r in replacements:
        msg = msg.replace(r[:2], r[3:])

    while '&gf(' in msg or '&gb(' in msg:
        i = msg.index('&gf(') if '&gf(' in msg else msg.index('&gb(')
        end = msg.index(')', i)
        code = msg[i + 4:end]
        fore = msg[i + 2] == 'f'

        if code.startswith('#'):
            rgb = tuple(int(code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            code = code.replace(',', ' ').replace(';', ' ').replace('  ', ' ')
            rgb = tuple(int(c) for c in code.split(' '))

        msg = msg[:i] + ansi_rgb(*rgb, foreground=fore) + msg[end + 1:]

    return msg


def printc(msg: str):
    """
    Print with color

    :param msg: Message with minecraft color codes
    """
    print(color(msg + '&r'))


def parse_date_time(iso: str) -> datetime:
    """
    Parse date faster. Running 1,000,000 trials, this parse_date function is 4.03 times faster than
    python's built-in dateutil.parser.isoparse() function.

    Preconditions:
        - iso is the output of datetime.isoformat() (In a format like "2021-10-20T23:50:14")
        - iso is a valid date (this function does not check for the validity of the input)

    :param iso: Input date
    :return: Datetime object
    """
    return datetime(int(iso[:4]), int(iso[5:7]), int(iso[8:10]),
                    int(iso[11:13]), int(iso[14:16]), int(iso[17:19]))


def parse_date_only(iso: str) -> datetime:
    """
    Parse date faster.

    Preconditions:
        - iso starts with the format of "YYYY-MM-DD" (e.g. "2021-10-20" or "2021-10-20T10:04:14")
        - iso is a valid date (this function does not check for the validity of the input)

    :param iso: Input date
    :return: Datetime object
    """
    return datetime(int(iso[:4]), int(iso[5:7]), int(iso[8:10]))
