"""Fetches data from TradingView API and saves it to an excel spreadsheet.

You should check https://github.com/shner-elmo/TradingView-Screener
This project wouldn't be possible without accessing TradingView api which existence I was not aware of before finding their screener tools.
"""

import logging
import pathlib
import sys

import run
import run_script

logger = logging.getLogger('screenerfetch')
logger.addHandler(logging.FileHandler(str(pathlib.Path(__file__).parent.parent/'logs.log'), mode='w'))
logger.addHandler(logging.StreamHandler())

def main() -> None:
    """Runs screenerfetch with optional command line arguments.
    
    If arguments are passed, runs commands matching to these args, then exits: for scripting purposes.
    If ran without commands, will instead open the full CLI program.
    """
    if len(sys.argv[1:]) > 0:
        if len(sys.argv[1:]) == 1 and sys.argv[1] == '-log':  
            logger.setLevel(logging.DEBUG)
            logger.debug('Starting screenerfetch')
            run.open_cli()
        else:
            run_script.execute_args_commands()
    else:
        run.open_cli()
    logger.debug('Closing screenerfetch')

if __name__ == '__main__':
    main()