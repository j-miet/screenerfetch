"""For making screenerfetch scripts.

If command line args are passed, instead of opening the full program, will run specified commands then close.
"""

import argparse
import json
import shutil

import commands
from paths import FilePaths
import run
import workbook_tools

def execute_args_commands() -> None:
    """Runs commands based on passed command-line arguments and closes.

    Use 'py screenerfetch -h' to see possible arguments.

    Arguments are processed in order. Flag -h is always read first and will only display help, ignoring further flags.  
    For the rest, order is following:
    -wb -> -f -> -s -> -sa -> -c -> --export  
    This means writing 'py screenerfetch -f -c --export -sa' does -f -> -sa -> -c -> --export.
    """
    parser = argparse.ArgumentParser("screenerfetch")
    parser.add_argument("-log", action='store_true')
    parser.add_argument("-wb", "--change-wb", nargs=1, type=str,
                         help="change to another existing workbook or create a new one")
    parser.add_argument("-f", "--fetch", action='store_true',
                         help="fetch data from Tradingview API based on your current workbook query.txt."
                         " To edit query data, run screenerfetch without args to access full cli -> q/update query")
    parser.add_argument("-s", "--save", action='store_true',
                         help="opens api_data.txt where you can select which symbols to save in current xlsx file"
                         "Saving is possible only after data has been fetched with -f/--fetch")
    parser.add_argument("-a", "--saveall", action='store_true',
                         help="save all fetched data in .xlsx file. Saving is possible only after "
                         "data has been fetched with -f/--fetch")
    parser.add_argument("-c", "--autocopy", action='store_true',
                         help=f"makes/overwrites autocopy of current xlsx file. This won't override normal copy.")
    parser.add_argument("--export", const='all', nargs='?', type=str,
                         help="export workbook data into specified data format: 'csv', 'txt', 'json'. "
                         f"Default value 'all' creates all files inside workbook data folder")
    args = parser.parse_args()
    
    run._initialize_workbook()
    if args.change_wb:
        with open(FilePaths.settings_path/'settings.json') as f:
            settings = json.load(f)
        settings["wb_name"] = args.change_wb
        with open(FilePaths.settings_path/'settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
        run._initialize_workbook()
        commands.update_wb_file_name(args.change_wb)
    if args.fetch:
        commands.fetch()
    if args.save:
        commands.save()
    if args.saveall:
        commands.saveall()
    if args.autocopy:
        shutil.copy2(FilePaths.wb_path, FilePaths.wb_autocopy_path)
    if args.export:
        workbook_tools.export_wb(args.export)