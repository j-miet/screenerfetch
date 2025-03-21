"""Handles all query and custom header data.

Query is used to fetch screener data from Tradingview API. API requests can be tracked through browser developer tools: 
(F12) -> Network -> filter URL by 'scanner' and choose domain -> 'Request': JSON code updates as you change screener 
settings and update page.

You can create a query by writing it yourself, or just copy all the code from request page with
right click -> Copy All.

To setup your own query + save its contents in a workbook, use the command 'update query' in ui.

Example
--- 

market = 'america'

my_query = {
    "markets": ["america"],
    "options": {"lang": "en"},
    "columns": ["name",
                "open",
                "close",
                "low",
                "high", 
                "change_from_open", 
                "change", 
                "volume",
                "float_shares_outstanding_current", 
                "market_cap_basic",
                "premarket_open",
                "premarket_close",
                "premarket_change",
                "premarket_volume" 
                ],
    "filter": [{"left" : "premarket_change", "operation" : "greater", "right" : 7},
               {"left" : "premarket_volume", "operation" : "greater", "right" : 250000},
               {"left" : "premarket_close", "operation" : "less", "right" : 20},
               {"left" : "country", "operation" : "not_in_range", "right" : ["Aland Islands", "Anguilla",
                "Azerbaijan", "Barbados", "Cambodia", "China", "Faroe Islands", "Gibraltar", "Hong Kong",
                "Jamaica", "Kenya", "Macau", "Mauritius", "Montenegro", "Papua New Guinea",
                "Russian Federation", "Thailand", "Vietnam"]},
               {"left" : "typespecs", "operation" : "has", "right" : ["common"]},
               {"left" : "exchange", "operation" : "in_range", "right" : ["AMEX", "NYSE", "NASDAQ"]}             
               ],
    "sort": {"sortBy": "premarket_change", "sortOrder": "desc"},
    "range": [0, 75]
}

custom_headers = {
    'A' : {'name': 'Date'},
    'B' : {'name': 'Symbol'},
    'C' : {'name': 'Open', 'type': 'float'},
    'D' : {'name': 'Price', 'type': 'float'},
    'E' : {'name': 'Low', 'type': 'float'},
    'F' : {'name': 'High', 'type': 'float'},
    'G' : {'name': 'Chg from Open %', 'type': 'float'},
    'H' : {'name': 'Change %', 'type': 'float'},
    'I' : {'name': 'Volume', 'type': 'int'},
    'J' : {'name': 'Float', 'type': 'int'},
    'K' : {'name': 'Market Cap', 'type': 'int'},
	'L' : {'name': 'Pre-market Open', 'type': 'float'},
    'M' : {'name': 'Pre-market Close', 'type': 'float'},
    'N' : {'name': 'Pre-market Chg %', 'type': 'float'},
    'O' : {'name': 'Pre-market Vol', 'type': 'int'}
}
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import copy
import json

from paths import FilePaths

if TYPE_CHECKING:
    from typing import Any

class FetchData:
    """Wrapper class that stores request headers + screener data for excel workbooks.
    
    query_data should only be modified by calling commands.fetch().
    """
    REQUEST_HEADERS = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.5',
    'content-type': 'text/plain;charset=UTF-8',
    'host': 'scanner.tradingview.com',
    'origin': 'https://www.tradingview.com/',
    'referer': 'https://www.tradingview.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'
    } 
    query_data: list[list[str]] = []


class QueryVars:
    """Wrapper class for all variables tied to current query, market and custom header values.
    
    Values are only updated under 2 separate cases:
    -initialization after program starts
    -using command 'update query' & exiting update mode by typing 'back'.
    """
    market: str
    url: str
    my_query: dict[str, dict[str, Any] | list[Any]]
    custom_headers: dict[str, dict[str, str]]

    actual_columns: list[str]
    header_chars: list[str]
    col_headers: dict[str, str]
    int_cols: list[str]
    float_cols: list[str]

    date_col: str
    first_col: str
    last_col: str
    txt_headers: list[str]
    sheet_xlsx_int_cols: list[int]
    sheet_xlsx_float_cols: list[int]


def get_actual_column_values(my_query: list[str]) -> list[str]:
    """Removes irrelevant column values from MY_QUERY.
    
    The web JSON request header has some column values that are not relevant to screenering: they are removed. 
    Currently, those values are:

    "description",
    "logoid",
    "update_mode",
    "type",
    "typespecs",
    "pricescale",
    "minmov",
    "fractional",
    "minmove2",
    "currency",
    "fundamental_currency_code",
    "exchange"

    Args:
        my_query: Columns of MY_QUERY i.e. query.MY_QUERY['columns']

    Returns:
        MY_QUERY column values with unused values removed.
    """
    delete_cols = ["description",
                "logoid",
                "update_mode",
                "type",
                "typespecs",
                "pricescale",
                "minmov",
                "fractional",
                "minmove2",
                "currency",
                "fundamental_currency_code",
                "exchange"]
    actual_cols = my_query
    for col in copy.copy(actual_cols):
        if col in delete_cols:
            actual_cols.remove(col)
    return actual_cols

def get_column_header_data(query_cols: list[str],
                                  custom_headers: dict[str, dict[str, Any]],
                                  header_chars: list[str]
                                  ) -> tuple[dict[str, str], list[str], list[str]]:
    """Updates column values with custom names and lists all integer and float-valued columns.

    Returns:
        a 3-tuple of column headers with their names, integer column headers, and float column headers.
    """
    init_column_headers = {char: name for char, name in zip(header_chars, ['date']+(query_cols))}
    if len(custom_headers.keys()) > 0:
        for header in copy.deepcopy(init_column_headers).keys():
            try:
                init_column_headers[header] = custom_headers[header]['name']
            except KeyError:
                ...
    column_headers = {key+'1': val for key, val in init_column_headers.items()}

    int_columns = []
    float_columns = []
    for char in custom_headers.keys():
        try:
            if custom_headers[char]['type'] == 'int':
                int_columns.append(char+'1')  
            elif custom_headers[char]['type'] == 'float':
                float_columns.append(char+'1')
            else:
                ...
        except (KeyError, TypeError):
            ...

    return column_headers, int_columns, float_columns

def update_query_variables() -> None:
    """Updates all QueryVars values."""
    with open(FilePaths.settings_path+'\\settings.json') as f:
        current_settings = json.load(f)
    QueryVars.market = current_settings['market']
    QueryVars.url = f'https://scanner.tradingview.com/{QueryVars.market}/scan'
    QueryVars.my_query = current_settings['query']
    QueryVars.custom_headers = current_settings['headers']

    QueryVars.actual_columns = get_actual_column_values(QueryVars.my_query['columns']) # type: ignore
    QueryVars.header_chars = [f'{c}' for c in list(map(chr,range(ord('A'), ord('A')+len(QueryVars.actual_columns)+1)))]
    QueryVars.col_headers, QueryVars.int_cols, QueryVars.float_cols  = get_column_header_data( 
                                                                        QueryVars.actual_columns, 
                                                                        QueryVars.custom_headers, 
                                                                        QueryVars.header_chars)
    QueryVars.date_col = [header[0] for header in QueryVars.col_headers.keys()][0]
    QueryVars.first_col = [header[0] for header in QueryVars.col_headers.keys()][1]
    QueryVars.last_col = [header[0] for header in QueryVars.col_headers.keys()][-1]
    QueryVars.txt_headers = [f'{char}1' for char in list(map(chr,range(ord(QueryVars.first_col),
                                                                       ord(QueryVars.last_col)+1)))] 
    QueryVars.sheet_xlsx_int_cols  = [ord(col_header[0].lower())-96 for col_header in QueryVars.int_cols]
    QueryVars.sheet_xlsx_float_cols = [ord(col_header[0].lower())-96 for col_header in QueryVars.float_cols]