import six
from termcolor import colored
from pyfiglet import figlet_format

from app.common.commons import Alerts


def print_cli(text, color, attrs=[], font='slant', figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(text, color, attrs=attrs))
        else:
            six.print_(colored(figlet_format(text, font=font), color, attrs=attrs))

def print_notification_cli(msg, alert_type):

    color = 'default'
    if alert_type == Alerts.Success:
        color = 'green'
    elif alert_type == Alerts.Warning:
        color = 'yellow'
    elif alert_type == Alerts.Failure:
        color = 'red'

    print_cli(msg, color, attrs=['bold'])