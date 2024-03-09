#!/usr/bin/env python3
### Hellsing main function

import sys
import traceback

from lib.core.ArgumentsParser import ArgumentsParser
from lib.core.Config import *
from lib.core.Exceptions import *
from lib.core.Settings import Settings
from lib.controller.MainController import MainController
# from lib.db.Mission import Mission
# from lib.db.Session import *
from lib.output.Logger import logger


class Program:
    def __init__(self):

        try:
            print(BANNER)
            # Parse settings files
            settings = Settings()

            # Parse command-line arguments
            arguments = ArgumentsParser(settings)
            
            # Controller
            controller = MainController(arguments, settings)
            controller.run()

        except KeyboardInterrupt:
            print()
            logger.error('Ctrl+C received ! Terminating...')
            sys.exit(0)
        except (SettingsException, AttackException) as e:
            logger.error(e)
            sys.exit(1)
        except (ValueError, ArgumentsException):
            print
            sys.exit(1)
        except Exception as e:
            print
            logger.error('Unexpected error occured: {0}'.format(str(e)))
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main = Program()