import os
import sys
from enum import Enum, auto
import app
from app.gui.effects import print_cli
from app.config import AppConfig
from app.tosca.parser import ToscaLoader
from app.tosca.model import ToscaModel
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError
from app.common.logging import LoggingFacility


logger = LoggingFacility.get_instance().get_logger()


current_session_text = \
"""
=== Current Session ===
Archive: {0}
Manifest: {1}
Validated: {2}
Toskosed: {3}
=======================
"""


class Menus(Enum):
    Main = auto()
    Loader = auto()
    Validator = auto()
    Metadata = auto()
    Toskose = auto()

menus_options = {

    Menus.Main: {
        'options': (
            'Quit',
            'Load CSAR',
            'Show Topology',
            'Toskose it!',
        ),
        'subroutines': (
            'quit',
            'tosca_loader_menu',
            'tosca_metadata',
            'toskoserization',
        ),
    },
    Menus.Loader: {
        'options': (
            'Back',
            'Load from file',
        ),
        'subroutines': (
            'go_back_menu',
            'tosca_load_from',
        )
    }
}


class CLI():

    def __init__(self):

        self.archive_path = None
        self.manifest_path = None
        self.is_valid = False
        self.is_toskosed = False

        self.csar_metadata = None
        self.tosca_model = None

        self.menu_stack = [Menus.Main]
        self.current_action = None

        self.notification = None


    def run(self):
    
        self.menu()

    def menu(self):
        """ """

        while True:

            self.load_menu()
            self.__action_validator(input('\nMake your choice: '))
            if self.current_action is not None:
                self.__action_handler()

    def load_menu(self):
        """ """

        os.system('clear')
        print_app_info()

        self.print_session()
        self.print_menu()

        if self.notification is not None:
            print_cli('\n{0}'.format(self.notification), color='red')
            self.notification = None

    def __action_validator(self, input):
        """ Validate actions inserted by the user """

        try:

            action_idx = int(input)

            if action_idx < 0 and action_idx > len(menus_options[self.menu_stack[-1]]['options'])-1:
                raise ValueError
            else: 
                self.current_action = action_idx
                
        except ValueError as err:
            self.current_action = None
            self.notification = 'It doesn \'t seem a valid option. Try Again!'
    
    def __action_handler(self):
        """ Call a subroutine by name based on the current menu and the current selected action 
        
        Note: the menu path is represented as a (list) stack, so the last inserted item is the current menu and it's
        obtained using list[-1]
        """

        getattr(self, menus_options[self.menu_stack[-1]]['subroutines'][self.current_action])()
    
    def go_back_menu(self):
        """ Go to the previous menu following the path on the menu stack """

        self.menu_stack.pop()

    def go_main_menu(self):
        """ Go to the main menu"""

        self.menu_stack = [Menus.Main]

    def tosca_loader_menu(self):
        """ """

        self.menu_stack.append(Menus.Loader) 

    def tosca_load_from(self, source='File'):
        """ """

        """ user input """
        while True:

            archive_path = None
            if source == 'File':
                archive_path = input('\nInsert the file path (0 Abort): ')
            
            if archive_path == '0':
                break

            try:
                
                tl = ToscaLoader(archive_path)
                self.archive_path, self.yaml_path, self.csar_metadata = \
                tl.archive_path, tl.yaml_path, tl.csar_metadata
                break
            
            except (ToscaParsingError, ToscaValidationError) as err:
                print_cli('{0}'.format(str(err)), color="red") 

        """ build model """
        self.tosca_model = ToscaModel(self.archive_path)

        self.go_main_menu() 

    def tosca_metadata(self):
        """ """
        pass

    def toskoserization(self):
        pass    

    def quit(self):
        """ Quit the program """

        print_cli('Goodbye!', color='blue', attrs=['bold'])
        sys.exit()
        

    def print_menu(self):
        """ Show the current menu options """

        menu_text = ''
        for idx, option in enumerate(menus_options[self.menu_stack[-1]]['options'][1:]):
            menu_text += '{0}. {1}\n'.format(idx+1, option)

        back_option = menus_options[self.menu_stack[-1]]['options'][0] # self.menu_stack[-1] is the current menu
        menu_text += '\n0. {0}'.format(back_option)

        print_cli('Menu\n\n{0}'.format(menu_text), color='blue', attrs=['bold'])


    def print_session(self):
        """ """

        print_cli(current_session_text.format( \
            'not loaded yet' if self.archive_path is None else self.archive_path,
            'not loaded yet' if self.manifest_path is None else self.manifest_path
            'No' if not self.is_valid else 'Yes',
            'No' if not self.is_toskosed else 'Yes'
        ), color="green", attrs=['bold'])


def print_app_info():
    """ Show info about the app """

    print_cli(app.__name__, color="blue", attrs=['bold'], figlet=True)
    print_cli("version {0}\n".format(app.__version__), color="yellow")