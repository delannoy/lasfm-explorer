#!/usr/bin/env python3

import logging, os


class C:
    '''Manage text format and text via tput'''
    # [https://stackoverflow.com/a/287944/13019084]
    # [https://janakiev.com/blog/python-shell-commands/]
    # [https://www.gnu.org/software/termutils/manual/termutils-2.0/html_chapter/tput_1.html]
    reset = os.popen('tput sgr 0 0').read() # Turn off all attributes
    bold = os.popen('tput bold').read() # Begin double intensity mode
    uline = os.popen('tput smul').read() # Begin underscore mode
    class F: # foreground
        black, red, green, yellow, blue, magenta, cyan, white = [os.popen(f'tput setaf {c}').read() for c in range(0,8)]
        grey, lred, lgreen, lyellow, lblue, lmagenta, lcyan, lwhite = [os.popen(f'tput setaf {c}').read() for c in range(8,16)]
    class B: # background
        black, red, green, yellow, blue, magenta, cyan, white = [os.popen(f'tput setab {c}').read() for c in range(0,8)]
        grey, lred, lgreen, lyellow, lblue, lmagenta, lcyan, lwhite = [os.popen(f'tput setab {c}').read() for c in range(8,16)]


class LogFmt(logging.Formatter):
    '''Custom logging formatter with color.'''
    # [https://docs.python.org/3/howto/logging-cookbook.html#customized-exception-formatting]
    # [https://stackoverflow.com/a/56944256/13019084]
    FORMATS = {
        logging.DEBUG: f'{C.F.grey}[%(levelname)s] [%(message)s]{C.reset}',
        logging.INFO: f'{C.F.grey}%(message)s{C.reset}',
        logging.WARNING: f'{C.F.yellow}%(message)s{C.reset}',
        logging.ERROR: f'{C.F.red}[%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s()] [%(message)s]{C.reset}',
        logging.CRITICAL: f'{C.B.red}{C.F.black}[%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s()] [%(message)s]{C.reset}'
    }
    def format(self, record):
        logFmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(logFmt)
        return formatter.format(record)


def logConfig(level:str='INFO'):
    log = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(LogFmt())
    log.addHandler(handler)
    log.setLevel(level)

logConfig(level='DEBUG')
logging.getLogger('urllib3').setLevel(logging.INFO) # [https://stackoverflow.com/a/11029841/13019084]
