"""Initializes and maintains the main command line interface."""

import argparse
import json
import shutil

import commands
import custom.c_commands
from paths import FilePaths
import query
import sheets
import workbook_tools

def _initialize_workbook() -> None:
    """Sets initial values for filepaths, workbook sheets and query variables."""
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as f:
        wb_name_dict = json.load(f)
    FilePaths.wb_name = wb_name_dict["wb_name"]
    FilePaths.update_filepaths()
    try:
        sheets.update_sheets()
    except FileNotFoundError:
        with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as f:
            wb_name_dict["wb_name"] = '_default'
            json.dump(wb_name_dict, f, indent=4)
        FilePaths.wb_name = wb_name_dict["wb_name"]
        FilePaths.update_filepaths()
    sheets.update_sheets()
    query.update_query_variables()

def execute_args_commands() -> None:
    """Runs commands based on passed command-line arguments and closes.

    Use 'py main.py -h' to see possible arguments.

    Arguments are processed in order. Flag -h is always read first and will only display help, ignoring further flags.  
    For the rest, order is left to right:
    -wb, -f, -s, -sa, -c, --export  
    This means writing 'py main.py -f -c --export -sa' does -f -> -sa -> -c -> --export.
    """
    _initialize_workbook()
    print(f"# Current workbook: {FilePaths.wb_name}")
    parser = argparse.ArgumentParser("main.py")
    parser.add_argument("-wb", "--change-wb", nargs=1, type=str,
                         help="change to another existing workbook or create a new one")
    parser.add_argument("-f", "--fetch", action='store_true',
                         help="fetch data from Tradingview API based on your current "
                         f"{FilePaths.wb_name}/data/query.txt."
                         " To edit query data, run main.py without args to access full cli -> q/update query")
    parser.add_argument("-s", "--save", action='store_true',
                         help="opens api_data.txt where you can select which symbols to save in "
                         f"{FilePaths.wb_name}.xlsx. "
                         "Saving is possible only after data has been fetched with -f/--fetch")
    parser.add_argument("-a", "--saveall", action='store_true',
                         help="save all fetched data in .xlsx file. Saving is possible only after "
                         "data has been fetched with -f/--fetch")
    parser.add_argument("-c", "--autocopy", action='store_true',
                         help=f"makes/overwrites automatic copy of {FilePaths.wb_name}.xlsx. Copy is named as "
                         f"{FilePaths.wb_autocopy_name}.xlsx.")
    parser.add_argument("--export", const='all', nargs='?', type=str,
                         help="export workbook data into specified data format: 'csv', 'txt', 'json'. "
                         f"Default value 'all' creates all files at {FilePaths.wb_name}/data")
    args = parser.parse_args()
    
    if args.change_wb:
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

def open_cli() -> None:
    """Opens command line interface."""
    _initialize_workbook()
    # these constants must be located here in order to initialize their f-string values before first print.
    COMMAND_MESSAGE = (
        "===================\n"
        "===screenerFetch===\n"
        "===================\n"
        "Commands\n"
        "--------------------------------------------------------\n"
        "help => how to get started.\n"
        "wb/change wb => change current workbook. Is also used in creating new ones. You can see your currently "
        "selected workbook on CLI as 'WB=...'\n"
        "q/update query => update query data, market and (optional) custom header values.\n"
        "f/fetch => fetch data from TradingView API based on query.MY_QUERY.\n"
        f"s/save => shows fetched data by opening data/{FilePaths.TXT_NAME}.txt. Add '+' in front of each symbol "+
            f"you'd wish to add, then save file.\n "
            f"\t  Data for each symbol is stored in workbooks/{FilePaths.wb_name}.xlsx file.\n"
        f"sa/save all => saves all fetched data to {FilePaths.wb_name}.xlsx.\n"
        f"txt/open txt => opens {FilePaths.wb_name}.txt file where you see the fetched data.\n"
        f"e/excel => opens {FilePaths.wb_name}.xlsx file which contains all symbols you saved.\n"
        f"copy => copy your current {FilePaths.wb_name}.xlsx file into {FilePaths.wb_manual_copy_name}.xlsx; replaces " 
            "previous copy.\n"
        f"export wb => reads {FilePaths.wb_name}.xlsx and saves data in selected format inside 'data' folder.\n"
        f"exit => close the program and copy current {FilePaths.wb_name}.xlsx data "
                f"into '{FilePaths.wb_autocopy_name}.xlsx'; replaces previous copy.\n"
        "print => prints current MY_QUERY contents.\n"

        f"FORMAT WB => overwrites current {FilePaths.wb_name}.xlsx. Fresh workbook has only column headers defined.\n"
        "\t     This preserves all settings files - so change those with 'update query' command, then format \n"
        "\t     afterwards if you need to update columns in xlsx files.\n"
        "DELETE WB => deletes selected workbook directory and all its contents.\n"
        "update date => update dates to yyyy/mm/dd format in case they show as yyyy/mm/dd; hh.mm.ss.\n"
        "update nums => update all customly listed columns to numerical values - so don't use this on other than "
        "columns with numerical values!\n"
            "\t       Select different columns by modifying query.py CUSTOM_HEADERS.\n"
        f"remove duplicates => removes all duplicate rows from {FilePaths.wb_name}.xlsx. Duplicate rows are those with "
        "same data and symbol name.\n"
        "\t\t     Remove iterates in reverse, meaning higher row indices are removed and lowest stays untouched.\n"
        "\t\t     E.g. if rows 10, 20, 35 have same date and name, only 10 stays.\n"
        "\t\t     Gaps are automatically adjusted: when a row is deleted, newer rows will move one index down.\n"
        
        "custom => custom commands. These are meant for user-specific query+workbook combos and should be "
            "manually implemented.\n\t"+
            "  Using them without correct query and workbook structure will likely crash this program.")
    HELP_MESSAGE = (">>>Quick guide on how to run this<<<\n"
                    "When typing commands, ignore the quotations. Some commands have normal & short notation, as seen "
                    "below.\n"
                    "1. Create a new workbook by typing 'change wb'/'cw'.\n"
                    "2. type 'update query'/'cw' and update these settings to your own liking.\n"
                    "3. after you've returned to main interface, type 'fetch'/'f' to get data based on your query.\n"
                    "Optionally, type 'txt' afterwards to check your query output - close this txt file before "
                    "proceeding to next step.\n"
                    "4. type either\n"
                    " -'save'/'s', if you'd wish to safe only specific rows of data, or\n"
                    " -'all'/'save all', if you'd like to save all data from query.\n"
                    "5. type 'excel'/'e' to open your .xlsx workbook file and check that everything was saved!\n"
                    "6. close your workbook and type 'exit' to leave program and to create an automatic copy of your "
                    "workbook. To make a manual hard copy, use 'copy' command instead.\n"
                    "[Quick save] run the 'quick run.bat' file located in screenerfetch root folder: this will perform "
                    "data fetching, saves all data to workbook and \n" 
                    "makes a autocopy before exiting (i.e. won't override your existing hard copy).\n")
        
    print(COMMAND_MESSAGE)
    while True:
        while FilePaths.wb_name == '_default':
            print("\n***Previously used workbook no longer exists. Select/create a new workbook to proceed.***\n")
            commands.update_wb_file_name()
        user_input = input(f'--------------------\n[main | WB={FilePaths.wb_name}]>>> ')
        match user_input:
            case 'help':
                print(HELP_MESSAGE)
                input("\n~Press Enter to return")
                print(COMMAND_MESSAGE)
            case 'q' | 'update query':
                commands.update_query()
            case 'wb' | 'change wb':
                commands.update_wb_file_name()
            case 'f' | 'fetch':
                commands.fetch()
            case 's' | 'save':
                commands.save()
            case 'sa' | 'save all':
                commands.saveall()
            case 'txt' | 'open txt':
                commands.show_txt()
            case 'e' | 'excel':
                commands.show_xlsx()
            case 'update date':
                commands.update_date_format()
            case 'update nums':
                commands.update_to_nums()
            case 'remove duplicates':
                commands.remove_duplicate_data()
            case 'copy':
                commands.copy()
            case 'FORMAT WB':
                commands.create()
                sheets.update_sheets()
                query.update_query_variables()
            case 'DELETE WB':
                commands.delete_workbook()
            case 'export wb':
                commands.export_wb()
            case 'exit':           
                shutil.copy2(FilePaths.wb_path, FilePaths.wb_autocopy_path)
                return
            case 'print':
                commands.print_query()
            case 'custom':
                custom.c_commands.select_custom_command()
            case _:
                print('Invalid command.')