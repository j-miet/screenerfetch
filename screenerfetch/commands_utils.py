"""Utility functions for commands.py."""

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date

import pandas as pd

from query import QueryVars, FetchData
from paths import FilePaths

if TYPE_CHECKING:
    from typing import Any

def get_date() -> str:
    """Returns current date in DD/MM/YYYY format.
    
    Returns:
        Current date string.
    """
    current = str(date.today()).split('-')
    year, month, day = current[0], current[1], current[2]
    return day+'/'+month+'/'+year

def round_to_int(value: float | None) -> int | str:
    """Returns floor integer value of a float.
    
    Args:
        value: Float or empty value.
    Returns:
        Either a integer value, or '-' if value if NoneType.
    """
    if value is not None: 
        return int(float(value))
    else:
        return '-'

def clean_fetched_data(request_data: dict[str, Any]) -> pd.DataFrame:
    """Cleans fetched API data and saves it for utilization.

    Request JSON data has two components: 'totalCount' and 'data'.
    'totalCount' lists total amount of row elements (= symbols) that request found.
    'data' contains a list of dictionaries with 's' and 'd' keys:
        's' contains a ticker symbol with market/exchange included in front e.g. 'NASDAQ: NVDA'.
        'd' contains all data columns, filtered accordingly to your query, in a list-like format. It preserves order of 
        columns from MY_QUERY so you can easily pinpoint which value corresponds to which.

    Args:
        request_data: JSON data from TradingView API.

    Returns:
        Pandas dataframe storing all cleaned fetch data.
    """
    raw_data = []
    for data in request_data['data']:
        raw_temp = []
        for column in data['d']:
            raw_temp.append(column)
        raw_data.append(raw_temp)
 
    rounded = []
    for symbol_data in raw_data:
        newcolumn = []
        for column in symbol_data:
            if isinstance(column, float):
                column = f"{column:.2f}"
            newcolumn.append(column)
        rounded.append(newcolumn)

    txt_dataframe = pd.DataFrame(data=rounded, 
                                 columns=[QueryVars.col_headers[header] for header in QueryVars.txt_headers])
    try:
        target_cols = [QueryVars.col_headers[headers] for headers in QueryVars.int_cols]
        for col in target_cols:
            txt_dataframe[col] = txt_dataframe[col].apply(round_to_int)
    except AttributeError:
        ...
    return txt_dataframe

def create_fetch_display_txt(df_string: list[str]) -> None:
    """Creates a displayable txt file for symbol data saving process.

    Data is written into a text file, which is used with 'txt' and 'save' commands, and is located in 'data' folder. 
    Previous file data is overwritten each time.

    Args:
        df_string: Pandas dataframe of screener data, converted into a list of row strings.
    """
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

def create_screener_data(df_string: list[str]) -> list[list[str]]:
    """Arranges each row of data string into its own symbol data list that preserves column order.

    Saving process:
        String data is split into sublists containing data for each symbol, and all of these lists are then stored 
        inside the variable list. This variable is used with 'save all' and 'save' commands to locate, verify and save 
        valid data rows into an excel workbook.

    Args:
        df_string: Pandas dataframe of screener data, converted into a list of row strings.

    Returns:
        All symbol data in a list, each symbol in its own sublists.
    """
    screenerdata_strings = df_string[1:]    # cut off the column names and include only symbol data
    all_data_rows: list[str] = []
    for data_row in screenerdata_strings:
        data_row_list = list(data_row.strip()) 
        status = 'empty'
        for index in range(len(data_row_list)):
            if data_row_list[index] == ' ' and status == 'empty':
                data_row_list[index] = '!'
                status = 'filled'
            elif data_row_list[index] != ' ' and status == 'filled':
                status = 'empty'
        all_data_rows.append(''.join(data_row_list).replace(' ', ''))

    final_query_data: list[list[str]] = []
    for data in all_data_rows:
        final = data.split('!')
        final_query_data.append(final)

    return final_query_data

def select_saved_objects() -> tuple[bool, list[list[str]]]:
    """Checks for any symbols that should be added by reading the fetch txt file.
    
    Symbols meant to be saved are recognized by having a '+' character before symbol name.

    Returns:
        A tuple where first value indicates whether saving was succesful and second is list of all symbol data needed 
        to be stored in an excel workbook.
    """
    symbols: list[str] = []
    if FetchData.query_data == []:
            print('No data available to save. Fetch data before you attempt to save it.')
            return False, []
    with open(FilePaths.TXT_PATH) as file:
        lines = file.readlines()[4:]
    for elem in lines:
        if '+' in elem:
            start = elem.index('+')
            for pos in range(start, len(elem)-1):
                if elem[pos+1] != ' ':
                    symbol_end = elem[pos+1:10].index(' ')   # space for symbol names should never exceed 10 symbols.
                    symbols.append(elem[pos+1: pos+1+symbol_end])
                    break
    check = False
    added_symbols: list[list[str]] = []
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