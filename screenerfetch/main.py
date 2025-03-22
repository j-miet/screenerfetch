"""Fetches data from TradingView API and saves it to an excel spreadsheet.

You should check
https://github.com/shner-elmo/TradingView-Screener
This project wouldn't be possible without accesing the non-public TradingView api their project utilizes.
"""

import json
import shutil
import shutil
import sys

import commands
import custom.c_commands
from paths import FilePaths
import query
import sheets

def main() -> None:
    """Opens the command line user interface."""
    with open(FilePaths.WB_FILES_ROOT_PATH+'\\current_wb.json') as f:
        names_json = json.load(f)
    FilePaths.wb_name = names_json["wb_name"]
    FilePaths.update_filepaths()
    try:
        sheets.update_sheets()
    except FileNotFoundError:
        with open(FilePaths.WB_FILES_ROOT_PATH+'\\current_wb.json', 'w') as f:
            names_json["wb_name"] = '_default'
            json.dump(names_json, f, indent=4)
        FilePaths.wb_name = names_json["wb_name"]
        FilePaths.update_filepaths()
    sheets.update_sheets()
    query.update_query_variables()

    # these constants must be located here in order to initialize their f-string values before first print.
    _COMMAND_MESSAGE = ("===================\n"
        "===screenerFetch===\n"
        "===================\n"
        "Commands\n"
        "--------------------------------------------------------\n"
        "help => how to get started.\n"
        "cw/change wb => change current workbook. You can see your currently selected workbook on CLI as 'WB=...'\n"
        "uq/update query => update query data, market and (optional) custom header values.\n"
        "f/fetch => fetch data from TradingView API based on query.MY_QUERY.\n"
        f"s/save => shows fetched data by opening data/{FilePaths.TXT_NAME}.txt. Add '+' in front of each symbol "+
            f"you'd wish to add, then save file. Data of each symbol is stored in workbooks/{FilePaths.wb_name}.xlsx "
            "file.\n"
        f"all/save all => saves all fetched data to {FilePaths.wb_name}.xlsx.\n"
        f"txt/open txt => opens {FilePaths.wb_name}.txt file where you see the fetched data.\n"
        f"e/excel => opens {FilePaths.wb_name}.xlsx file which contains all symbols you saved.\n"
        f"copy => copy your current {FilePaths.wb_name}.xlsx file into {FilePaths.wb_manual_copy_name}.xlsx; replaces " 
            "previous copy.\n"
        f"export wb => reads {FilePaths.wb_name}.xlsx and saves data in selected format inside 'data' folder.\n"
        f"exit => close the program and copy current {FilePaths.wb_name}.xlsx data "+
                f"into {FilePaths.wb_autocopy_name}.xlsx; replaces previous copy.\n"
        "print => prints current MY_QUERY contents.\n"

        f"FORMAT WB => overwrites current {FilePaths.wb_name}.xlsx. Fresh workbook has only column headers defined.\n"
        "update date => update dates to yyyy/mm/dd format in case they show as yyyy/mm/dd; hh.mm.ss.\n"
        "update nums => update all customly listed columns to numerical values - so don't use this on other than"
            "columns with numerical values!\n\t\t"
            "Select different columns by modifying query.py CUSTOM_HEADERS.\n"
        
        "custom => custom commands. These are meant for user-specific query+workbook combos and should be "
            "manually implemented.\n\t"+
            "Using them without correct query and workbook structure will likely crash this program.")
    _HELP_MESSAGE = (">>>Quick guide on how to run this<<<\n"
                    "1. type 'update query' and update these settings to your own liking.\n"
                    "2. Create a new workbook by typing 'CREATE NEW WB': type 'basic' as your workbook type.\n"
                    "3. type 'f' or 'fetch' to get data based on your query. Optionally, type 'txt' afterwards to check"
                    " your query output - close this txt file before proceeding to next step.\n"
                    "4. type either\n"
                    " -'save', if you'd wish to safe only specific pieces of data, or\n"
                    " -'all' or 'save all', if you'd like to save all data from query.\n"
                    "5. type 'excel' to open your workbook and check that everything was saved!\n"
                    "6. close your workbook and type 'exit' to leave program and to create an automatic copy of your "
                    "workbook (to make a manual hard copy, use 'copy' command instead).\n"
                    "[Quick save] run the 'run.bat' file: this will perform fetching, saves all data to workbook and " 
                    "makes a copy before exiting (so not a hard copy).\n")
    
    print(_COMMAND_MESSAGE)
    while True:
        while FilePaths.wb_name == '_default':
            print("\n***Previously used workbook no longer exists. Select/create a new workbook to proceed.***\n")
            commands.update_wb_file_name()
        user_input = input(f'--------------------\n[main | WB={FilePaths.wb_name}]>>> ')
        match user_input:
            case 'help':
                print(_HELP_MESSAGE)
                input("\n~Press Enter to return")
                print(_COMMAND_MESSAGE)
            case 'uq' | 'update query':
                commands.update_query()
            case 'cw' | 'change wb':
                commands.update_wb_file_name()
            case 'f' | 'fetch':
                commands.fetch()
            case 's' | 'save':
                commands.save()
            case 'all' | 'save all':
                commands.saveall()
            case 'txt' | 'open txt':
                commands.show_txt()
            case 'e' | 'excel':
                commands.show_xlsx()
            case 'update date':
                commands.update_date_format()
            case 'update nums':
                commands.update_to_nums()
            case 'copy':
                commands.copy()
            case 'FORMAT WB':
                commands.create()
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
                print('Unknown command.')

if __name__ == '__main__':
    # for running quick run.bat: fetch data, save all in a workbook, then make a copy of current workbook.
    if len(sys.argv) > 1 and sys.argv[1] == 'fetch saveall copy':
        with open(FilePaths.wb_files_path+'\\current_wb.json') as f:
            names_json = json.load(f)
        FilePaths.wb_name = names_json["wb_name"]
        FilePaths.update_filepaths()
        sheets.update_sheets()
        query.update_query_variables()
        commands.fetch()
        commands.saveall()
        shutil.copy2(FilePaths.wb_path, FilePaths.wb_autocopy_path) # doesn't overwrite manual copy, only autocopy.
        sys.exit()
    else:
        main()