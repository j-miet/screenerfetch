"""Fetches data from TradingView API and saves it to an excel spreadsheet.

You should check
https://github.com/shner-elmo/TradingView-Screener
This project wouldn't be possible without accesing TradingView api their project utilizes.
"""

import sys

import run

def main() -> None:
    """Runs screenerfetch with optional command line arguments.
    
    If arguments are passed, will run commands matching to these args, then exit.
    If ran without commands, will instead open the full CLI program.
    """
    if len(sys.argv[1:]) > 0:
        run.execute_args_commands()
    else:
        run.open_cli()

if __name__ == '__main__':
    main()