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
import copy
import json
import logging
from typing import TYPE_CHECKING

from paths import FilePaths

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger('screenerfetch')

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
    wb_type: str

    header_chars: list[str]
    col_headers: dict[str, str]
    int_cols: list[str]
    float_cols: list[str]
    float_decimals: dict[str, int]

    date_col: str
    txt_headers: list[str]
    sheet_xlsx_int_cols: list[int]
    sheet_xlsx_float_cols: list[int]

    @staticmethod
    def get_header_values() -> list[str]:
        """Return xlsx column character list depending on length of provided query columns.

        Support up to 52 values (date + 51 query column values). Exceeding this limit will cause a crash.

        Returns:
            list[str]:
            List of all required excel column letters.
        """
        total_cols = len(QueryVars.my_query["columns"])
        header_chrs = [
                f'{c}' for c in list(map(chr,range(ord('A'), ord('A')+len(QueryVars.my_query["columns"][:25])+1)))]
        if 26 <= total_cols <= 52:
            header_chrs += [
                f'A{c}' for c in list(map(chr,range(ord('A'), ord('A')+len(QueryVars.my_query["columns"][25:]))))]
        if total_cols > 52:
            print("Column characters exceed 52. Returning empty list.")
            return []
        return header_chrs

    @staticmethod
    def get_column_header_data(query_cols: list[str],
                                custom_headers: dict[str, dict[str, Any]],
                                header_chars: list[str]
                                ) -> tuple[dict[str, str], list[str], list[str], list[str]]:
        """Updates column values with custom names and lists all integer and float-valued columns.

        Args:
            query_cols (list[str]): Query columns list.
            custom_headers (dict[str, dict[str, Any]]): Custom column header dictionary.
            header_chars (list[str]): Xlsx sheet column letters.

        Returns:
            tuple[dict[str,str],list[str],list[str]]:
            a 3-tuple of column headers with their names, integer column headers, and float column headers, alongside 
                their decimal counts.
        """
        logger.debug("query.py> QueryVars.get_column_header_data")
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
        float_decimals = {}
        for char in custom_headers.keys():
            try:
                if custom_headers[char]['type'] == 'int':
                    int_columns.append(char+'1')  
                elif custom_headers[char]['type'] == 'float':
                    float_columns.append(char+'1')
                decimals = custom_headers[char]['decimals']
                if decimals >= 0:
                    float_decimals.update({char+'1': decimals})
            except (KeyError, TypeError):
                ...
        return column_headers, int_columns, float_columns, float_decimals

    @staticmethod
    def update_query_variables() -> None:
        """Updates all QueryVars values."""
        logger.debug("query.py> QueryVars.update_query_variables")
        with open(FilePaths.settings_path/'settings.json') as f:
            current_settings = json.load(f)
        QueryVars.market = current_settings['market']
        QueryVars.url = f'https://scanner.tradingview.com/{QueryVars.market}/scan'
        QueryVars.my_query = current_settings['query']
        QueryVars.custom_headers = current_settings['headers']
        QueryVars.wb_type = current_settings['type']

        QueryVars.header_chars = QueryVars.get_header_values()

        QueryVars.col_headers, QueryVars.int_cols, QueryVars.float_cols, QueryVars.float_decimals = (
                QueryVars.get_column_header_data(QueryVars.my_query["columns"], 
                                                    QueryVars.custom_headers, 
                                                    QueryVars.header_chars))
        QueryVars.date_col = [header[0] for header in QueryVars.col_headers.keys()][0]
        QueryVars.txt_headers = [header for header in list(QueryVars.col_headers)[1:]]
        QueryVars.sheet_xlsx_int_cols  = [ord(col_header[0].lower())-96 for col_header in QueryVars.int_cols]
        QueryVars.sheet_xlsx_float_cols = [ord(col_header[0].lower())-96 for col_header in QueryVars.float_cols]
        logger.debug("query.py> QueryVars.update_query_variables: All values updated")