"""All major logic behind commands.py."""

from __future__ import annotations
from datetime import date
import json
import logging
import os
import re
import shutil
from typing import TYPE_CHECKING

import pandas as pd
import requests

from query import QueryVars, FetchData
from paths import FilePaths
from sheets import WorkbookSheets 
import workbook_tools

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger('screenerfetch')

def get_date() -> str:
    """Returns current date in DD/MM/YYYY format.
    
    Returns:
        str:
        Current date string.
    """
    current = str(date.today()).split('-')
    year, month, day = current[0], current[1], current[2]
    return day+'/'+month+'/'+year

def round_to_int(value: float | int | str) -> int | str:
    """Returns floor integer value of a float.
    
    Args:
        value (float | int | str): Float, int or '-' for pandas NaN values.

    Returns:
        int/str:
        Either an integer or '-'.
    """
    if value != '-': 
        return int(float(value))
    else:
        return '-'

def requests_api_data() -> Any:
    """Request data from Tradingview API based on current settings.json values.
    
    Data is send as json dictionary query. If request was succesful, returns all as another json dictionary.

    Returns:
        Any:
        Json dictionary of fetched api data.
    
    Raises:
        Exception: Request status code was not 200.
    """
    logger.debug("commands_utils> requests_api_data")
    request_data = requests.post(url=QueryVars.url, json=QueryVars.my_query, headers=FetchData.REQUEST_HEADERS)
    if request_data.status_code == requests.codes.ok:
        return request_data.json()
    else:
        logger.debug("commands_utils> requests_api_data: Invalid http status code, critical error")
        raise Exception("Could not fetch any data from API.")

def clean_fetched_data(request_data: Any) -> pd.DataFrame:
    """Cleans fetched API data, updates numeric types for columns, and saves it for utilization.

    Request JSON data has two components: 'totalCount' and 'data'.
    'totalCount' lists total amount of row elements (= symbols) that request found.
    'data' contains a list of dictionaries with 's' and 'd' keys:
        's' contains a ticker symbol with market/exchange included in front e.g. 'NASDAQ: NVDA'.
        'd' contains all data columns, filtered accordingly to your query, in a list-like format. It preserves order of 
        columns from MY_QUERY so you can easily pinpoint which value corresponds to which.

    Notes:
    1. Any float-type value is rounded to 2 decimals with column:.2f. This also means they get converted to strings. 
    As pandas has only types int64, float64 and object, it means dataframe has types int64 for integers or object for 
    anything else.
    Rounding will also save zero digits: e.g. 100.001 becomes 100.00, 100.999 becomes 101.00.

    2. If value is a list e.g. with query has column 'typespecs' which returns list objects like ['prefered'], all list 
    elements are joined as string with comma as separator.

    Args:
        request_data (Any): JSON data dictionary object fetched from TradingView web API.

    Returns:
        pandas.Dataframe:
            Cleaned fetch data.
    """
    logger.debug("commands_utils> clean_fetched_data")
    current_data = []
    raw_data = []
    for data in request_data['data']:
        raw_temp = []
        for column in data['d']:
            raw_temp.append(column)
        raw_data.append(raw_temp)
    current_data = raw_data

    modified = []
    for symbol_data in current_data:
        newcolumn = []
        for column in symbol_data:
            if isinstance(column, list):
                column = ', '.join(column)
            newcolumn.append(column)
        modified.append(newcolumn)
    current_data = modified

    txt_dataframe = pd.DataFrame(data=current_data, 
                                 columns=[QueryVars.col_headers[header] for header in QueryVars.txt_headers])
    txt_dataframe = txt_dataframe.fillna('-')
    try:
        target_cols = [QueryVars.col_headers[headers] for headers in QueryVars.int_cols]
        for col in target_cols:
            txt_dataframe[col] = txt_dataframe[col].apply(round_to_int)
    except AttributeError:
        ...
    try:
        target_cols = [QueryVars.col_headers[headers] for headers in QueryVars.float_cols]
        decimals = {QueryVars.col_headers[headers]: QueryVars.float_decimals[headers] for headers in QueryVars.
                    float_decimals.keys()}
        for col in target_cols:
            try:
                decimal_val = decimals[col]
                txt_dataframe[col] = txt_dataframe[col].apply(lambda t: f"{float(t):.{decimal_val}f}")
            except KeyError:
                ...
    except AttributeError:
        ...
    return txt_dataframe
    

def create_fetch_display_txt(df_string: list[str]) -> None:
    """Creates a displayable txt file for symbol data saving process.

    Data is written into a text file, which is used with 'txt' and 'save' commands, and is located in 'data' folder. 
    Previous file data is overwritten each time.

    Args:
        df_string (list[str]): Pandas dataframe of screener data, converted into a list of row strings.
    """
    logger.debug("commands_utils> create_fetch_display_txt")
    display_txt = df_string[:]  # creates a copy, otherwise the line separator gets appended below!
    date_str = get_date().split('/')
    ymd_date = date_str[2]+'/'+date_str[1]+'/'+date_str[0]
    with open(FilePaths.TXT_PATH, 'w') as f:
        f.write('#After calling \'save\', insert a single \'+\' (without quotations) before symbol names you\'d '
                'like to save in excel worksheet.\n\n')
        f.write('['+ymd_date+']\n\n')
    with open(FilePaths.TXT_PATH, 'a') as f:
        display_txt.insert(1, '-'*len(display_txt[0]))
        file_str = '\n'.join(display_txt)
        f.write(file_str)

def create_screener_data(df_dict: dict[Any, Any]) -> list[list[Any]]:
    """Arranges fetched data from a dictionary into its own symbol data list that preserves column order.

    Args:
        df_dict (dict[Any, Any]): Pandas dataframe of screener data, converted into a dictionary. Each key lists 
            corresponding data in fetch order, e.g. df_dict["name][N-1] to get "name" of Nth symbol from query.

    Returns:
        list[list[str]]:
        All symbol data in a list, each symbol in its own sublists, creating a list of lists.
    """
    logger.debug("commands_utils> create_screener_data")
    final_query_data: list[list[str]] = []
    first_col = tuple(df_dict.keys())[0]
    symbol_total = len(df_dict[first_col])
    for symb in range(0, symbol_total):
        current_symbol_data = []
        for key in df_dict.keys():
            current_symbol_data.append(df_dict[key][symb])
        final_query_data.append(current_symbol_data)
    return final_query_data

def select_saved_objects() -> tuple[bool, list[list[str]]]:
    """Checks for any symbols that should be added by reading the fetch txt file.
    
    Symbols meant to be saved are recognized by having a '+' character before symbol name.

    Returns:
        tuple[bool,list[list[str]]]:
        A tuple where first value indicates whether saving was succesful and second is list of all symbol data needed 
        to be stored in an excel workbook.
    """
    logger.debug("commands_utils> select_saved_objects")
    symbols: list[str] = []
    if FetchData.query_data == []:
            print('No data available to save. Fetch data before you attempt to save it.')
            return False, []
    with open(FilePaths.TXT_PATH) as file:
        lines = file.readlines()[4:]
    for elem in lines:
        if elem.lstrip().startswith('+'):
            start = elem.index('+')
            for pos in range(start, len(elem)-1):
                if elem[pos+1] != ' ':
                    symbol_end = elem[pos+1:len(elem)].index(' ')
                    symbols.append(elem[pos+1: pos+1+symbol_end])
                    break
    check = False
    added_symbols: list[list[Any]] = []
    for symb in symbols:
        check = False
        for symbol_data in FetchData.query_data:
            if symb in symbol_data:
                check = True
                added_symbols.append(symbol_data)
                break
        if not check:
            print(f'Error: Invalid symbol "{symb}", saving process halted.')
            return False, []
    return check, added_symbols

def check_wb_name_validity(wb_name: str) -> int:
    """Check if workbook name is valid.

    Name cannot be '_default', empty, or contain characters.
    
    Args:
        wb_name (str): Workbook name.

    Returns:
        int:
        -1 for bad input, 0 is valid name.
    """
    logger.debug("commands_utils> check_wb_name_validity")
    invalid_chars = re.compile(r"""[#%&{}\/<>*?$!'":@+´'¨`|=]""")
    if wb_name == '_default':
        print("This workbook cannot be selected!")
        return -1
    elif len(wb_name.strip()) == 0:
        print('Workbook name cannot be empty.')
        return -1
    elif len(invalid_chars.findall(wb_name)) > 0:
        print('Workbook name cannot contain following characters:\n'
              r'''#%&{}\/<>*?$!'":@+´'¨`|=''')
        return -1
    else:
        logger.debug("commands_utils> check_wb_name_validity: Returned 0")
        return 0

def change_workbook(wb_name_input: str, new: bool, check_name: bool = True) -> int:
    """Changes to existing workbook or creates a new one.
    
    Args:
        wb_name_input (str): Workbook name string.
        new (bool): True if new workbook is created, False is existing one is used.
        check_name (bool=True): True if workbook name validity check is performed, False is not. Default value is 
            True.

    Returns:
        int:
        -1 if wb_name_input was not accepted,  
        -2 if name is fine, new = False, but workbook not found.  
        -3 if name is fine, new = True, but workbook already exist  
        1 if wb name fine, new = False, and workbook was found and selected as current  
        2 if wb name fine, new = True, and a new workbook was created and selected as current.
    """
    logger.debug("commands_utils> change_workbook: Called with following args\n"
                f"wb_name_input: {wb_name_input}\n"
                f"new: {new}\n"
                f"check_name: {check_name}")
    if check_name:
        if check_wb_name_validity(wb_name_input) == -1:
            logger.debug("commands_utils> change_workbook: Returned -1")
            return -1
    exists = False
    for dir in os.listdir(FilePaths.WB_FILES_ROOT_PATH):
        if dir == wb_name_input:
            exists = True
            break
    with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json') as f:
        wb_fname = json.load(f)
    wb_fname['wb_name'] = wb_name_input
    if not new and not exists:
        logger.debug("commands_utils> change_workbook: Returned -2")
        return -2
    elif not new and exists: 
        with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as f:
            json.dump(wb_fname, f, indent=4)
        FilePaths.wb_name = wb_name_input
        print(f"Workbook '{wb_name_input}' selected.")
        FilePaths.update_filepaths()
        QueryVars.update_query_variables()
        WorkbookSheets.update_sheets()
        logger.debug("commands_utils> change_workbook: Returned 1")
        return 1
    elif new and not exists:
        with open(FilePaths.WB_FILES_ROOT_PATH/'current_wb.json', 'w') as f:
            json.dump(wb_fname, f, indent=4)
        FilePaths.wb_name = wb_name_input
        print("Creating new folder structure under workbooks...")
        workbook_tools.create_wb()
        print(f"Workbook '{wb_name_input}' with type 'basic' created and selected.")
        logger.debug("commands_utils> change_workbook: Returned 2")
        return 2
    else:
        print("Workbook already exists.")
        logger.debug("commands_utils> change_workbook: Returned 3")
        return -3

def update_settings_json(query_input: str, manual_update: bool = True) -> None:
    """Updates settings.json query and header values for current workbook.

    Also auto-updates market value based on your query.
    
    Args:
        query_input (str): 'query' or 'headers'.
        manual_update (bool=True): Default value True means user inserts their data into opened files. False requires 
            writing into query.txt & headers.txt before calling this function.
    """
    if manual_update:
        logger.debug("commands_utils> update_settings_json: Called with manual_update=True")
    else:
        logger.debug("commands_utils> update_settings_json")
    match query_input:
        case 'query':
            logger.debug("commands_utils> update_settings_json: Input 'query'")
            if manual_update:
                os.system(str(FilePaths.settings_path/'query.txt'))
            try:
                if os.path.getsize(FilePaths.settings_path/'query.txt') == 0:
                    current_query = {}
                else:
                    with open(FilePaths.settings_path/'query.txt') as f:
                        current_query = json.load(f)
                with open(FilePaths.settings_path/'settings.json') as f:
                    settings = json.load(f)
                settings["query"] = current_query
                try:
                    if len(current_query["markets"]) > 1:
                        settings["market"] = "global"
                    else:
                        settings["market"] = current_query["markets"][0]
                except KeyError:
                    settings["market"] = "global"
                with open(FilePaths.settings_path/'settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)
                if QueryVars.my_query["columns"] == ['name']:
                    workbook_tools.create_wb(False)
                    QueryVars.update_query_variables()
            except json.decoder.JSONDecodeError:
                print('Invalid json text given. Make sure all properties are enclosed in double quotes.') 
        case 'headers':
            logger.debug("commands_utils> update_settings_json: Input 'headers'")
            if manual_update:
                os.system(str(FilePaths.settings_path/'headers.txt'))
            try:
                if os.path.getsize(FilePaths.settings_path/'headers.txt') == 0:
                    current_headers = {}
                else:
                    with open(FilePaths.settings_path/'headers.txt') as f:
                        current_headers = json.load(f)
                with open(FilePaths.settings_path/'settings.json') as f:
                    settings = json.load(f)
                settings['headers'] = current_headers
                with open(FilePaths.settings_path/'settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)
            except json.decoder.JSONDecodeError:
                print('Invalid json text given. Make sure all properties are enclosed in double quotes.')

def delete_workbook(wb_name_to_del: str) -> int:
    """Deletes workbook.
    
    Args:
        wb_name_to_del (str): To be deleted workbook folder.

    Returns:
        int:
        -1 if no file was deleted; invalid name/doesn't exist. 0 if delete was succesful.
    """
    logger.debug(f"commands_utils> delete_workbook: Called with name arg {wb_name_to_del}")
    if wb_name_to_del == '_default':
        print("Cannot delete default workbook!")
        return -1
    elif wb_name_to_del.endswith(('.txt', '.json')):
        return -1
    elif wb_name_to_del in os.listdir(FilePaths.WB_FILES_ROOT_PATH):
        try:
            shutil.rmtree(FilePaths.WB_FILES_ROOT_PATH/wb_name_to_del)
        except PermissionError:
            print("Unable to delete workbook: one or more of its files are in use.")
            return -1
        print(f"Workbook '{wb_name_to_del}' contents deleted succesfully!")
        logger.debug("commands_utils> delete_workbook: Delete succesful'")
        return 0
    else:
        return -1