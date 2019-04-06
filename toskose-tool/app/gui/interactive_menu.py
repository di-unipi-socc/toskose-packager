import os
import click
from app.gui.effects import print_cli
from app.config import AppConfig
from app.tosca.tosca_parser import ToscaParser
from app.common.exception import ToscaParsingError
from app.common.logging import LoggingFacility


logger = LoggingFacility.get_instance().get_logger()


@dataclass
class CLIState:
    """ """

    file_path: str
    is_valid: bool


def cli():

    clistate = CLIState()

    while True:

        os.system('clear')
        print_app_info()






    if file is not None:

        try:

            tosca = ToscaParser(file)

        except ToscaParsingError as parse_err:
            logger.exception(parse_err)
            print_cli('{0}'.format(str(parse_err)), color="red")


def print_app_info():
    """ """

    print_cli(AppConfig._APP_NAME, color="blue", figlet=True)
    print_cli("version {0}\n".format(AppConfig._APP_VERSION), color="yellow")










# _MAIN_MENU_OPTIONS = ('Load')

# _MENU_OPTIONS = {
#     "MAIN_MENU": _MAIN_MENU_OPTIONS
# }


# class InteractiveMenu():
#     """ """

#     def __init__(self):
        
#         self.current_selection = None
#         self.is_main_menu = False

#         self.main()

#     @click.command()
#     def main(self):
#         """ """

#         self._menu_selector()


            
#     def _menu_selector(self):
#         """ """

#         __print_app_info()
#         __print_menu(_MENU_OPTIONS['MAIN_MENU'])


#     @staticmethod
#     def __print_menu(menu_options, is_main_menu=True):
#         """ """

#         txt = ''
#         entries = []
#         for idx, val in enumerate(menu_options):
#             entries.append('{0}. {1}'.format(idx,val))

#         last_entry = 'Back'
#         if is_main_menu:
#             last_entry = 'Exit'

#         entries.append('0. {1}'.format(last_entry))

#         print_cli(txt.join(entries))
        
#     @staticmethod
#     def __print_app_info():
#         """ """

#         print_cli(AppConfig._APP_NAME, color="blue", figlet=True)
#         print_cli("version {0}\n".format(AppConfig._APP_VERSION), color="yellow")


# @click.group()
# def main():
#     pass