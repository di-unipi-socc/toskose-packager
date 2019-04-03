import six
from termcolor import colored
from pyfiglet import figlet_format


def print_cli(text, color, font='slant', figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(text, color))
        else:
            six.print_(colored(figlet_format(text, font=font), color))