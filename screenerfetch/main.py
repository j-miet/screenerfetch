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
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as f:
        names_json = json.load(f)
    FilePaths.wb_name = names_json["wb_name"]
    FilePaths.update_filepaths()
    try:
        sheets.update_sheets()
    except FileNotFoundError:
        with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as f:
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
        "cw/change wb => change current workbook, or create new ones. You can see your currently selected "
        "workbook as 'WB=...' when in main ui.\n"
        "uq/update query => update query data, market and (optional) custom header values.\n"
        "f/fetch => fetch data from TradingView API based on query.MY_QUERY.\n"
        f"s/save => shows fetched data by opening data/{FilePaths.TXT_NAME}.txt.\n"
            "\t  Add '+' in front of each symbol "
            f"you'd wish to add, then save file. Data of each symbol is stored in workbooks/{FilePaths.wb_name}.xlsx "
            "file.\n"
        f"all/save all => saves all fetched data to {FilePaths.wb_name}.xlsx.\n"
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
    _HELP_MESSAGE = (">>>Quick guide on how to run this<<<\n"
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
                print('Unknown command.')

if __name__ == '__main__':
    # for running quick run.bat: fetch data, save all data in current workbook, then make a copy of this workbook.
    if len(sys.argv) > 1:
        with open(FilePaths.wb_files_path/'current_wb.json') as f:
            names_json = json.load(f)
        FilePaths.wb_name = names_json["wb_name"]
        FilePaths.update_filepaths()
        sheets.update_sheets()
        query.update_query_variables()
        cmds = sys.argv[1].split()
        for c in cmds:
            if c == 'fetch':
                commands.fetch()
            elif c == 'saveall':
                commands.saveall()
            elif c == 'copy':
                shutil.copy2(FilePaths.wb_path, FilePaths.wb_autocopy_path) # doesn't overwrite manual copy, only autocopy.
        sys.exit()
    else:
        main()