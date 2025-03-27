"""Opens and controls the full command line interface program."""

import json
import os
import shutil

import commands
import custom
import custom.small_cap1.c_commands
import custom.small_cap1.c_workbook_tools
from paths import FilePaths
from query import QueryVars
from sheets import WorkbookSheets
# put custom workbook packages here
import custom.small_cap1
#

def _custom_create(wb_type: str) -> None:
    """Creates workbook for given workbook type..
    
    Args:
        wb_type: Workbook type.
    """
    # Add workbook creation command of any custom package here
    match wb_type:
        case 'basic':
            commands.create()
        case 'small_cap1':
            custom.small_cap1.c_workbook_tools.create_custom_wb()

def _select_custom_package() -> None:
    """Selects current custom package based on settings.json "type" value."""
    with open(FilePaths.settings_path/'settings.json') as f:
        wb_type = json.load(f)["type"]
    if wb_type in os.listdir(FilePaths.PATH/'custom'):
        # add interface access command for any custom package here
        if wb_type == 'small_cap1':
            custom.small_cap1.c_commands.select_custom_command()
        #
        return
    print(f"Unsupported custom package type '{wb_type}'.")

def _create_new_wb() -> None:
    print("Select workbook type.\n# Supported types:\nbasic")
    for type in os.listdir(FilePaths.PATH/'custom'):
        if type.startswith(('_', '.')):
            continue
        else:
            print(type)
    type_input = input('[wb type]>>>')
    if type_input.startswith(('_', '.')):
        print("Invalid characters in custom type.")
        return
    elif type_input in os.listdir(FilePaths.PATH/'custom') or type_input == 'basic':
        _custom_create(type_input)
        QueryVars.update_query_variables()
        print(f"Workbook '{FilePaths.wb_name}' formated to support type '{type_input}'.")
    else:
        print("Unsupported custom type.")

def _initialize_workbook() -> None:
    """Sets initial values for filepaths, workbook sheets and query variables."""
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as f:
        wb_name_dict = json.load(f)
    FilePaths.wb_name = wb_name_dict["wb_name"]
    FilePaths.update_filepaths()
    try:
        WorkbookSheets.update_sheets()
    except FileNotFoundError:
        with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as f:
            wb_name_dict["wb_name"] = '_default'
            json.dump(wb_name_dict, f, indent=4)
        FilePaths.wb_name = wb_name_dict["wb_name"]
        FilePaths.update_filepaths()
    WorkbookSheets.update_sheets()
    QueryVars.update_query_variables()

def open_cli() -> None:
    """Opens full command line interface program."""
    _initialize_workbook()
    # these constants must be located here in order to initialize their f-string values before first print.
    print("===================\n"
        "===screenerFetch===\n"
        "===================\n"
        "Type 'help' to get started or 'commands' to list all basic commands.")
    
    COMMAND_MESSAGE = (
        "--------------------------------------------------------\n"
        "--------------------------------------------------------\n"
        "help => how to get started.\n"
        "commands => displays all basic commands available.\n"
        "wb/change wb => change current workbook. Is also used in creating new ones. You can see your currently "
            "selected workbook on CLI as 'WB=...'\n"
        "q/update query => update query data, market and (optional) custom header values.\n"
        "f/fetch => fetch data from TradingView API based on query.MY_QUERY.\n"
        f"s/save => shows fetched data by opening data/{FilePaths.TXT_NAME}.txt. Add '+' in front of each symbol "+
            f"you'd wish to add, then save file.\n "
            f"\t  Data for each symbol is stored in workbooks/{FilePaths.wb_name}.xlsx file.\n"
        f"sa/saveall => saves all fetched data to {FilePaths.wb_name}.xlsx.\n"
        f"txt/open txt => opens {FilePaths.wb_name}.txt file where you see the fetched data.\n"
        f"e/excel => opens {FilePaths.wb_name}.xlsx file which contains all symbols you saved.\n"
        f"copy => copy your current {FilePaths.wb_name}.xlsx file into {FilePaths.wb_manual_copy_name}.xlsx; replaces " 
            "previous copy.\n"
        f"export wb => reads {FilePaths.wb_name}.xlsx and saves data in selected format inside 'data' folder.\n"
        f"exit => close the program and copy current {FilePaths.wb_name}.xlsx data "
                f"into '{FilePaths.wb_autocopy_name}.xlsx'; replaces previous copy.\n"
        "print => prints current MY_QUERY contents.\n"
        "update date => update dates to yyyy/mm/dd format in case they show as yyyy/mm/dd; hh.mm.ss.\n"
        "update nums => update all customly listed columns to numerical values - so don't use this on other than "
        "columns with numerical values!\n"
            "\t       Select different columns by modifying query.py CUSTOM_HEADERS.\n"
        f"remove duplicates => removes all duplicate rows from {FilePaths.wb_name}.xlsx. Duplicate rows are those with "
            "same data and symbol name.\n"
        "\t\t     Remove iterates in reverse, meaning higher row indices are removed and lowest stays untouched.\n"
        "\t\t     E.g. if rows 10, 20, 35 have same date and name values, only 10 remains.\n"
        "\t\t     Gaps are automatically adjusted: when a row is deleted, newer rows will move one index down.\n"
        "custom => commands for custom type workbook if they have been implemented; see FORMAT WB below.\n"
        f"UPDATE WB => overwrites current workbook '{FilePaths.wb_name}'. Overwrites current xlsx data (not the copy " 
            "files), but preserves all settings files.\n"
            "\t     Meant to be used for updating your xlsx headers values according to settings.json: call this "
            "command if you are creating\n"
            "\t     a new workbook and have already set all query stuff with 'update query'.\n"
        f"FORMAT WB => format current workbook '{FilePaths.wb_name}' to any supported type, default being 'basic'. "
            "All custom i.e. non-basic type workbooks support basic commands, though!\n"
            "\t     This process will both overwrite any of your xlsx data (excluding copies) AND settings folder "
            "data!\n"
            "\t     Custom workbooks can access their custom commands, if they have been implemented, "
            "via 'custom'.\n"
        "DELETE WB => deletes selected workbook directory and all its contents. Cannot delete currently selected "
            "workbook.")
    HELP_MESSAGE = ("-----------------------------------------------\n"
                    ">>>Quick guide on how to setup screenerfetch<<<\n"
                    "-write all commands without quotations."
                    "-some commands have normal & short notation, both are fine.\n"
                    "1. Create a new workbook (or use existing one) by typing 'cw'/'change wb'.\n"
                    "2. type 'q'/'update query' and update these settings to your own liking.\n"
                    "3. after you've returned to main interface, type 'f'/'fetch' to get data based on your query.\n"
                    "Optionally, type 'txt'/'open txt' afterwards to check your query output - close this txt file "
                    "before proceeding to next step.\n"
                    "4. type either\n"
                    " -'s'/'save', if you'd wish to safe only specific rows of data, or\n"
                    " -'sa'/'saveall', if you'd like to save all data from query.\n"
                    "5. type 'e'/'excel' to open your .xlsx workbook file and check that everything was saved!\n"
                    "6. close your workbook and optionally try other commands. Type 'exit' to leave program and to "
                    "create an automatic copy of your workbook.\n"
                    "To make a separate manual copy, use 'copy' instead.")
    while True:
        while FilePaths.wb_name == '_default':
            print("\n***Previously used workbook no longer exists. Select/create a new workbook to proceed.***\n")
            commands.update_wb_file_name()
        user_input = input(f'--------------------\n[main | WB={FilePaths.wb_name} | Type: {QueryVars.wb_type}]>>> ')
        match user_input:
            case 'help':
                print(HELP_MESSAGE)
                input("\n~Press Enter to continue...")
            case 'commands':
                print(COMMAND_MESSAGE)
                input("\n~Press Enter to continue...")
            case 'q' | 'update query':
                commands.update_query()
            case 'wb' | 'change wb':
                commands.update_wb_file_name()
            case 'f' | 'fetch':
                commands.fetch()
            case 's' | 'save':
                commands.save()
            case 'sa' | 'saveall':
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
            case 'UPDATE WB':
                commands.create(False)
            case 'FORMAT WB':
                _create_new_wb()
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
                _select_custom_package()
            case _:
                print('Invalid command.')