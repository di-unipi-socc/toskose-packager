import os
import sys
from enum import Enum, auto
from dataclasses import dataclass, field
import app
from app.gui.effects import print_cli
from app.config import AppConfig
from app.tosca.loader import ToscaLoader
from app.tosca.validator import ToscaValidator
from app.tosca.model import ToscaModel
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError
from app.common.logging import LoggingFacility


logger = LoggingFacility.get_instance().get_logger()


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

class Alerts(Enum):
    Success = auto()
    Warning = auto()
    Failure = auto()

class CLI():  

    class BaseSession():

        def print(self):
            return [attr for attr in dir(self) if not attr.startswith('__') and not attr == 'print']

    @dataclass
    class SessionPaths(BaseSession):
        archive: str = None
        csar_dir: str = None
        manifest: str = None

        def print(self):
            return '\n'.join(['- {0}: {1}'.format(attr, 'Not loaded yet' if not getattr(self, attr) else (getattr(self, attr))) for attr in super().print()])

    @dataclass
    class SessionFlags(BaseSession):
        validated: bool = False
        topology: bool = False
        toskosed: bool = False

        def print(self):
            return '\n'.join(['- {0}: {1}'.format(attr, 'No' if not getattr(self, attr) else 'Yes') for attr in super().print()])

    def __init__(self):

        self._paths = CLI.SessionPaths()
        self._flags = CLI.SessionFlags()

        self._csar_metadata = None
        self._tosca_model = None

        self.menu_stack = [Menus.Main]
        self.current_action = None
        self.notify = None


    def run(self):
    
        while True:

            self.load_menu()
            
            self.__action_validator(input('\nMake your choice: '))
            if self.current_action is not None:
                self.__action_handler()

    def load_menu(self):

        os.system('clear')
        self.print_app_info()
        self.print_session()
        self.print_menu()
        self.print_notification()

    def __action_validator(self, input):
        """ Validate actions inserted by the user """

        try:

            action_idx = int(input)

            if action_idx < 0 or action_idx > len(menus_options[self.menu_stack[-1]]['options'])-1:
                raise ValueError
            else: 
                self.current_action = action_idx
                
        except ValueError as err:
            self.current_action = None
            self.notify = ('It doesn\'t seem a valid option. Try Again!', Alerts.Failure)
    
    def __action_handler(self):
        """ Call a subroutine by name based on the current menu and the current selected action 
        
        Note: the menu path is represented as a (list) stack, so the last inserted item is the current menu and it's
        obtained using list[-1]
        """

        try:
            getattr(self, menus_options[self.menu_stack[-1]]['subroutines'][self.current_action])()
        except Exception as err:
            logger.exception(err)
            self.notify = ('An internal error is occurred', Alerts.Failure)
    
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
        """ Load a CSAR archive from a source """

        while True:

            archive_path = None
            if source == 'File':
                archive_path = input('\nInsert the file path (0 Abort): ')
            
            # Abort
            if archive_path == '0':
                break

            try:

                # Loading
                tl = ToscaLoader(archive_path)
                self._paths = CLI.SessionPaths(**tl.get_paths())

                # Validation
                ToscaValidator(os.path.join(self._paths.csar_dir, self._paths.manifest)).validate()
                self._flags.validated = True
                self._csar_metadata = tl.csar_metadata

                # Build Model
                self._tosca_model = ToscaModel(self._paths.manifest)
                self._flags.topology = True

                break
            
            except (ToscaParsingError, ToscaValidationError) as err:
                self.notify = (err, Alerts.Failure)
            except Exception as err:
                logger.exception(err)
                self.notify = ('An internal error is occurred', Alerts.Failure)
             
        self.go_main_menu() 

    def tosca_metadata(self):
        pass

    def toskoserization(self):
        pass    

    def quit(self):
        """ Quit the program """

        print_cli('Goodbye!', color='blue', attrs=['bold'])
        sys.exit()

    def print_app_info(self):
        """ Show info about the app """

        print_cli(app.__name__, color="blue", attrs=['bold'], figlet=True)
        print_cli("version {0}\n".format(app.__version__), color="yellow")

    def print_session(self):
        """ Show the current session """

        print_cli('=== Current Session ===\n{0}\n{1}\n'
            .format(self._paths.print(), self._flags.print()), color="green", attrs=['bold']) 
    
    def print_menu(self):
        """ Show the current menu options """

        menu_text = ''
        for idx, option in enumerate(menus_options[self.menu_stack[-1]]['options'][1:]):
            menu_text += '{0}. {1}\n'.format(idx+1, option)

        back_option = menus_options[self.menu_stack[-1]]['options'][0] # self.menu_stack[-1] is the current menu
        menu_text += '\n0. {0}'.format(back_option)

        print_cli('Menu\n\n{0}\n'.format(menu_text), color='blue', attrs=['bold']) 

    def print_notification(self):
        """ """

        def print_alert(msg, type, attrs=['bold']):

            color = 'blue'
            if type == Alerts.Success:
                color = 'green'
            elif type == Alerts.Warning:
                color = 'yellow'
            elif type == Alerts.Failure:
                color = 'red'
            print_cli(msg, color=color, attrs=attrs)

        if self.notify is not None:
            print_alert(self.notify[0], self.notify[1])
            self.notify = None