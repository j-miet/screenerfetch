"""Fetches data from TradingView API and saves it to an excel spreadsheet.

You should check https://github.com/shner-elmo/TradingView-Screener
This project wouldn't be possible without accessing TradingView api which existence I was not aware of before finding their screener tools.
"""

import sys

import run
import run_script

def main() -> None:
    """Runs screenerfetch with optional command line arguments.
    
    If arguments are passed, runs commands matching to these args, then exits: for scripting purposes.
    If ran without commands, will instead open the full CLI program.
    """
    if len(sys.argv[1:]) > 0:
        run_script.execute_args_commands()
    else:
        run.open_cli()

if __name__ == '__main__':
    main()